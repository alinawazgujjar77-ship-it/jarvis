import os
import json
from threading import Lock
from datetime import datetime, timedelta


class MemoryManager:
    """
    Persistent key/value memory manager with conversation history and pruning.

    - Stores simple key/value pairs in the same JSON file.
    - Keeps a conversation history list (append-only) stored under the key "__conversations__".
    - Provides pruning by max items or TTL (days).
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
        else:
            self._data = {}

        # Ensure conversation history key exists
        if "__conversations__" not in self._data:
            self._data["__conversations__"] = []

    def _save(self):
        try:
            with self._lock:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Memory save error:", e)

    # Key/value methods
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
        self._data = {"__conversations__": []}
        self._save()

    # Conversation history methods
    def append_conversation(self, role, content):
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self._data.setdefault("__conversations__", []).append(entry)
        self._save()

    def get_conversations(self, limit=None):
        conv = self._data.get("__conversations__", [])
        if limit:
            return conv[-limit:]
        return conv

    def prune_conversations(self, max_items: int = 100, ttl_days: int = 30):
        conv = self._data.get("__conversations__", [])
        # Prune by TTL first
        cutoff = datetime.utcnow() - timedelta(days=ttl_days)
        pruned = [c for c in conv if datetime.fromisoformat(c["timestamp"].rstrip("Z")) >= cutoff]
        # If still too many, keep only the last max_items
        if len(pruned) > max_items:
            pruned = pruned[-max_items:]
        self._data["__conversations__"] = pruned
        self._save()

    # Utility to get a simple summary of memory keys
    def keys(self):
        return [k for k in self._data.keys() if k != "__conversations__"]

    def dump(self):
        return self._data
