import json
import os
import csv
from typing import List, Dict, Any


class KBStore:
    def __init__(self, path=None, agent_csv=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "..", "data", "kb.json")
        self.path = os.path.abspath(self.path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        self.agent_kb = []
        if agent_csv:
            self.load_agent_csv(agent_csv)

    def _load(self) -> List[Dict[str, Any]]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, items: List[Dict[str, Any]]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    def load_agent_csv(self, csv_path):
        """Load agent KB from CSV."""
        if os.path.exists(csv_path):
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.agent_kb = [row for row in reader]
        else:
            self.agent_kb = []

    def list(self, q: str = None, mode: str = "buyer") -> List[Dict[str, Any]]:
        if mode == "agent":
            items = self.agent_kb
        else:
            items = self._load()
        if not q:
            return items
        qlower = q.lower()
        return [it for it in items if qlower in it.get("title", "").lower() or qlower in it.get("content", "")]

    def add(self, item: Dict[str, Any]) -> Dict[str, Any]:
        items = self._load()
        item = item.copy()
        item.setdefault("id", str(len(items) + 1))
        items.append(item)
        self._save(items)
        return item

    def clear(self):
        self._save([])
