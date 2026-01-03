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
            return {"answer": self._simulate_answer(mode, query, docs), "needs_search": False, "search_url": None}

        # Prompt to understand intent and check if up-to-date
        prompt = f"""
        用户模式: {mode}
        用户问题: {query}
        可用知识库内容: {"\n".join(docs) if docs else "无"}

        请分析用户意图，判断是否需要外部搜索官方信息（如 hdb.gov.sg）。
        如果知识库足够回答且信息最新，直接回复答案。
        如果需要搜索，返回需要搜索的 URL（如 https://www.hdb.gov.sg/）和理由。

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
            return {"answer": self._simulate_answer(mode, query, docs), "needs_search": False, "search_url": None}

    def stream_answer(self, mode: str, query: str, docs: List[str], external_info: str = None):
        """Stream the final answer, incorporating external info if provided."""
        if not self.client:
            text = self._simulate_answer(mode, query, docs)
            for i in range(0, len(text), 80):
                chunk = text[i : i + 80]
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
            text = self._simulate_answer(mode, query, docs)
            for i in range(0, len(text), 80):
                chunk = text[i : i + 80]
                yield chunk
                time.sleep(0.02)
