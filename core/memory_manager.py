"""Advanced SQLite-based memory manager for JARVIS."""

import sqlite3
import json
from pathlib import Path
from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta
from threading import Lock
from core.logger import Logger

logger = Logger.get(__name__)


class MemoryManager:
    """Persistent memory system using SQLite."""

    def __init__(self, db_path: str = "data/jarvis.db") -> None:
        self.db_path = db_path
        self._lock = Lock()
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Key-value store
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keyvalues (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME
                )
            """)

            # Knowledge base
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    # Key-Value Methods
    def remember(self, key: str, value: Any) -> None:
        """Store a key-value pair."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                value_json = json.dumps(value) if not isinstance(value, str) else value
                cursor.execute(
                    "INSERT OR REPLACE INTO keyvalues (key, value) VALUES (?, ?)",
                    (key, value_json)
                )
                conn.commit()
                conn.close()
                logger.debug(f"Remembered key: {key}")
        except Exception as e:
            logger.error(f"Failed to remember key {key}: {e}")

    def recall(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM keyvalues WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            if row:
                try:
                    return json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    return row[0]
            return default
        except Exception as e:
            logger.error(f"Failed to recall key {key}: {e}")
            return default

    def forget(self, key: str) -> None:
        """Delete a key."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM keyvalues WHERE key = ?", (key,))
                conn.commit()
                conn.close()
                logger.debug(f"Forgot key: {key}")
        except Exception as e:
            logger.error(f"Failed to forget key {key}: {e}")

    # Conversation Methods
    def append_conversation(self, role: str, content: str) -> None:
        """Add a conversation entry."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO conversations (role, content) VALUES (?, ?)",
                    (role, content)
                )
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Failed to append conversation: {e}")

    def get_conversations(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve conversation history."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT role, content, timestamp FROM conversations ORDER BY id DESC"
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in reversed(rows)]
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []

    def prune_conversations(self, max_items: int = 100, ttl_days: int = 30) -> None:
        """Remove old conversations."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Remove by TTL
                cutoff = datetime.utcnow() - timedelta(days=ttl_days)
                cursor.execute(
                    "DELETE FROM conversations WHERE timestamp < ?",
                    (cutoff.isoformat(),)
                )

                # Keep only latest max_items
                cursor.execute(
                    "DELETE FROM conversations WHERE id NOT IN (SELECT id FROM conversations ORDER BY id DESC LIMIT ?)",
                    (max_items,)
                )

                conn.commit()
                conn.close()
                logger.info(f"Pruned conversations (max_items={max_items}, ttl_days={ttl_days})")
        except Exception as e:
            logger.error(f"Failed to prune conversations: {e}")

    # Task Management
    def add_task(self, title: str, description: str = "") -> int:
        """Add a new task."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (title, description) VALUES (?, ?)",
                    (title, description)
                )
                task_id = cursor.lastrowid
                conn.commit()
                conn.close()
                logger.debug(f"Added task: {title}")
                return task_id
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return -1

    def get_tasks(self, status: str = "pending") -> List[Dict]:
        """Get tasks by status."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, status FROM tasks WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []

    def complete_task(self, task_id: int) -> None:
        """Mark a task as completed."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (task_id,)
                )
                conn.commit()
                conn.close()
                logger.debug(f"Completed task: {task_id}")
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")

    # Knowledge Base
    def store_knowledge(self, topic: str, content: str) -> None:
        """Store knowledge in the knowledge base."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO knowledge (topic, content) VALUES (?, ?)",
                    (topic, content)
                )
                conn.commit()
                conn.close()
                logger.debug(f"Stored knowledge: {topic}")
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")

    def search_knowledge(self, query: str) -> List[Dict]:
        """Search the knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT topic, content FROM knowledge WHERE topic LIKE ? OR content LIKE ? LIMIT 10",
                (f"%{query}%", f"%{query}%")
            )
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return []

    def clear(self) -> None:
        """Clear all data."""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM conversations")
                cursor.execute("DELETE FROM keyvalues")
                cursor.execute("DELETE FROM preferences")
                cursor.execute("DELETE FROM tasks")
                cursor.execute("DELETE FROM knowledge")
                conn.commit()
                conn.close()
                logger.info("Memory cleared")
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
