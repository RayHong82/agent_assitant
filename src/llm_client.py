import os
import time
from typing import List


class LLMClient:
    """Simple wrapper: if OPENAI_API_KEY is present, the code here can be extended to call OpenAI.
    For now it simulates streaming by chunking text."""

    def __init__(self):
        self.key = os.getenv("OPENAI_API_KEY")

    def _simulate_answer(self, mode: str, query: str, docs: List[str]) -> str:
        header = f"Mode: {mode}. 问题: {query}\n\n"
        body = "\n\n".join(docs) if docs else "根据知识库暂无直接匹配，我给出一般性回答：建议联系中介确认详情。"
        return header + body + "\n\n（来源：团队知识库）"

    def stream_answer(self, mode: str, query: str, docs: List[str]):
        text = self._simulate_answer(mode, query, docs)
        # simple chunking to simulate streaming
        for i in range(0, len(text), 80):
            chunk = text[i : i + 80]
            yield chunk
            time.sleep(0.02)
