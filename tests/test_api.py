import json
import os
import sys
from fastapi.testclient import TestClient

# ensure project src is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.app import app

client = TestClient(app)


def test_kb_crud_and_query():
    # clear kb
    data = client.get('/api/kb').json()
    # add an item
    item = {'title': 'HDB 购买流程', 'content': 'HDB相关政策摘要', 'tags': ['policy']}
    r = client.post('/api/kb', json=item)
    assert r.status_code == 200
    # list
    out = client.get('/api/kb').json()
    assert any('HDB' in i.get('title', '') for i in out)
    # query (streaming) - read body
    r2 = client.post('/api/query', json={'mode': 'buyer', 'query': 'HDB'})
    assert r2.status_code == 200
