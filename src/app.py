import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List

from .kb_store import KBStore
from .llm_client import LLMClient
from .scraper import fetch_and_summarize

app = FastAPI(title="Property Agent Assistant")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
static_dir = os.path.join(BASE_DIR, "src", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

kbs = KBStore(path=os.path.join(BASE_DIR, "data", "kb.json"))
llm = LLMClient()


@app.get("/")
def index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return HTMLResponse("<h1>Property Agent Assistant</h1>")


@app.get("/api/kb")
def api_kb(q: str = None):
    return kbs.list(q=q)


@app.post("/api/kb")
async def api_kb_add(request: Request):
    body = await request.json()
    if not body.get("title") or not body.get("content"):
        raise HTTPException(status_code=400, detail="title and content required")
    item = kbs.add(body)
    return item


@app.post("/api/query")
async def api_query(request: Request):
    data = await request.json()
    mode = data.get("mode", "buyer")
    query = data.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="query required")

    print(f"Processing query: mode={mode}, query={query}")

    # simple retrieval
    hits = kbs.list(q=query)
    docs = [h.get("content") for h in hits]
    print(f"Retrieved {len(docs)} docs from KB")

    # Use LLM to understand intent
    intent_result = llm.understand_intent_and_answer(mode, query, docs)
    print(f"Intent result: needs_search={intent_result.get('needs_search')}, search_url={intent_result.get('search_url')}, reason={intent_result.get('reason')}")

    external_info = None
    if intent_result.get("needs_search") and intent_result.get("search_url"):
        try:
            search_result = fetch_and_summarize(intent_result["search_url"])
            external_info = f"从 {search_result['url']} 获取: {search_result['summary']}"
            print(f"Fetched external info from {intent_result['search_url']}")
        except Exception as e:
            external_info = f"无法获取外部信息: {str(e)}"
            print(f"Failed to fetch external info: {e}")

    print("Starting to stream answer")
    def event_stream():
        for chunk in llm.stream_answer(mode, query, docs, external_info):
            # SSE-friendly format
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/fetch")
def api_fetch(url: str):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="invalid url")
    try:
        res = fetch_and_summarize(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return res
