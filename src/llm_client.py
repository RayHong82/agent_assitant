import os
import time
import openai
from typing import List, Dict, Any


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None

    def _simulate_answer(self, mode: str, query: str, docs: List[str]) -> str:
        header = f"Mode: {mode}. 问题: {query}\n\n"
        body = "\n\n".join(docs) if docs else "根据知识库暂无直接匹配，我给出一般性回答：建议联系中介确认详情。"
        return header + body + "\n\n（来源：团队知识库）"

    def understand_intent_and_answer(self, mode: str, query: str, docs: List[str]) -> Dict[str, Any]:
        """Use LLM to understand intent and decide if external search is needed."""
        if not self.client:
            # Fallback: simple keyword-based intent detection and URL selection
            query_lower = query.lower()
            needs_search = any(keyword in query_lower for keyword in ["组屋", "hdb", "政策", "资格", "购买", "loan", "finance", "ura", "土地", "外国人", "cpf", "公积金", "tax", "税务"])
            search_url = None
            if "hdb" in query_lower or "组屋" in query_lower or "购买" in query_lower:
                search_url = "https://www.hdb.gov.sg/"
            elif "ura" in query_lower or "土地" in query_lower or "外国人" in query_lower:
                search_url = "https://www.ura.gov.sg/"
            elif "loan" in query_lower or "贷款" in query_lower or "finance" in query_lower:
                search_url = "https://www.ocbc.com/"  # Example bank site
            elif "cpf" in query_lower or "公积金" in query_lower:
                search_url = "https://www.cpf.gov.sg/"
            elif "tax" in query_lower or "税务" in query_lower:
                search_url = "https://www.iras.gov.sg/"
            return {
                "needs_search": needs_search,
                "search_url": search_url,
                "answer": None,  # Will be generated later
                "reason": "Keyword-based detection (no LLM)"
            }

        # Original LLM-based logic
        prompt = f"""
        用户模式: {mode}
        用户问题: {query}
        可用知识库内容: {"\n".join(docs) if docs else "无"}

        请分析用户意图，判断是否需要外部搜索官方信息。
        如果知识库足够回答且信息最新，直接回复答案。
        如果需要搜索，根据问题内容选择最合适的官方网站 URL（如 hdb.gov.sg, ura.gov.sg, cpf.gov.sg, iras.gov.sg, 或银行网站如 ocbc.com 等）并返回。

        回复格式:
        {{
            "needs_search": true/false,
            "search_url": "url or null",
            "answer": "直接答案或 null",
            "reason": "理由"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            result = response.choices[0].message.content.strip()
            # Parse JSON
            import json
            parsed = json.loads(result)
            return parsed
        except Exception as e:
            print(f"LLM error: {e}")
            # Fallback to keyword-based detection even if LLM failed
            query_lower = query.lower()
            needs_search = any(keyword in query_lower for keyword in ["组屋", "hdb", "政策", "资格", "购买", "loan", "finance", "ura", "土地", "外国人", "cpf", "公积金", "tax", "税务"])
            search_url = None
            if "hdb" in query_lower or "组屋" in query_lower or "购买" in query_lower:
                search_url = "https://www.hdb.gov.sg/"
            elif "ura" in query_lower or "土地" in query_lower or "外国人" in query_lower:
                search_url = "https://www.ura.gov.sg/"
            elif "loan" in query_lower or "贷款" in query_lower or "finance" in query_lower:
                search_url = "https://www.ocbc.com/"
            elif "cpf" in query_lower or "公积金" in query_lower:
                search_url = "https://www.cpf.gov.sg/"
            elif "tax" in query_lower or "税务" in query_lower:
                search_url = "https://www.iras.gov.sg/"
            return {
                "needs_search": needs_search,
                "search_url": search_url,
                "answer": None,
                "reason": f"LLM failed ({e}), using keyword fallback"
            }

    def stream_answer(self, mode: str, query: str, docs: List[str], external_info: str = None):
        """Stream the final answer, incorporating external info if provided."""
        if not self.client:
            # Fallback: generate answer based on docs and external_info
            knowledge = "\n".join(docs) if docs else "暂无相关知识库信息。"
            ext = f"\n外部信息：{external_info}" if external_info else ""
            full_answer = f"基于知识库{ext}，回答您的问题：\n\n{knowledge}\n\n建议参考官方网站获取最新信息。"
            for i in range(0, len(full_answer), 80):
                chunk = full_answer[i : i + 80]
                yield chunk
                time.sleep(0.02)
            return

        full_context = f"模式: {mode}\n问题: {query}\n知识库: {'\n'.join(docs)}\n外部信息: {external_info or '无'}"
        prompt = f"基于以下信息，回答用户问题。保持简洁、专业。\n\n{full_context}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.5,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    time.sleep(0.02)
        except Exception as e:
            print(f"Streaming error: {e}")
            # Fallback to docs + external_info even if LLM failed
            knowledge = "\n".join(docs) if docs else "暂无相关知识库信息。"
            ext = f"\n外部信息：{external_info}" if external_info else ""
            full_answer = f"基于知识库{ext}，回答您的问题：\n\n{knowledge}\n\n建议参考官方网站获取最新信息。"
            for i in range(0, len(full_answer), 80):
                chunk = full_answer[i : i + 80]
                yield chunk
                time.sleep(0.02)
