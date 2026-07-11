import json
import os
from threading import Lock


class MemoryManager:
    """
    Simple persistent key/value memory manager backed by a JSON file.
    Methods:
      - remember(key, value)
      - recall(key, default=None)
      - forget(key)
      - clear()
    """

    def __init__(self, path="memory.json"):
        self.path = path
        self._lock = Lock()
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        try:
            with self._lock:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Memory save error:", e)

    def remember(self, key, value):
        self._data[key] = value
        self._save()

    def recall(self, key, default=None):
        return self._data.get(key, default)

    def forget(self, key):
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self):
        self._data = {}
        self._save()
