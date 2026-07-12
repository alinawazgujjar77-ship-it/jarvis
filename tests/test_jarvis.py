"""Unit tests for JARVIS Pro."""

import os
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta

# Import core modules
from core.logger import Logger
from core.memory_manager import MemoryManager
from core.ai_brain import AIBrain
from core.search_engine import SearchEngine
from core.voice_assistant import VoiceAssistant
from core.command_handler import CommandHandler
from core.config_manager import Config


class TestLogger:
    """Test logging system."""

    def test_logger_singleton(self) -> None:
        """Test logger is a singleton."""
        logger1 = Logger.get("test1")
        logger2 = Logger.get("test1")
        assert logger1 is logger2

    def test_logger_creates_log_dir(self) -> None:
        """Test logger creates log directory."""
        assert Path("logs").exists()


class TestMemoryManager:
    """Test memory management system."""

    @pytest.fixture
    def temp_db(self) -> str:
        """Create temporary database for testing."""
        db_path = "test_memory.db"
        yield db_path
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_remember_recall(self, temp_db: str) -> None:
        """Test storing and retrieving values."""
        mem = MemoryManager(db_path=temp_db)
        mem.remember("test_key", "test_value")
        assert mem.recall("test_key") == "test_value"
        assert mem.recall("nonexistent") is None

    def test_forget(self, temp_db: str) -> None:
        """Test deleting values."""
        mem = MemoryManager(db_path=temp_db)
        mem.remember("test_key", "test_value")
        mem.forget("test_key")
        assert mem.recall("test_key") is None

    def test_conversation_history(self, temp_db: str) -> None:
        """Test conversation history management."""
        mem = MemoryManager(db_path=temp_db)
        mem.append_conversation("user", "hello")
        mem.append_conversation("assistant", "hi there")
        
        conversations = mem.get_conversations()
        assert len(conversations) == 2
        assert conversations[0]["role"] == "user"
        assert conversations[1]["role"] == "assistant"

    def test_task_management(self, temp_db: str) -> None:
        """Test task management."""
        mem = MemoryManager(db_path=temp_db)
        task_id = mem.add_task("Test Task", "This is a test")
        assert task_id > 0
        
        tasks = mem.get_tasks("pending")
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Test Task"
        
        mem.complete_task(task_id)
        tasks = mem.get_tasks("pending")
        assert len(tasks) == 0

    def test_knowledge_base(self, temp_db: str) -> None:
        """Test knowledge base storage and search."""
        mem = MemoryManager(db_path=temp_db)
        mem.store_knowledge("Python", "Python is a programming language")
        
        results = mem.search_knowledge("Python")
        assert len(results) > 0
        assert results[0]["topic"] == "Python"

    def test_clear(self, temp_db: str) -> None:
        """Test clearing memory."""
        mem = MemoryManager(db_path=temp_db)
        mem.remember("key1", "value1")
        mem.append_conversation("user", "hello")
        mem.clear()
        
        assert mem.recall("key1") is None
        assert len(mem.get_conversations()) == 0


class TestAIBrain:
    """Test AI brain system."""

    def test_ai_brain_initialization(self) -> None:
        """Test AI brain initializes."""
        brain = AIBrain()
        assert brain.history is not None
        assert len(brain.history) >= 1  # System message

    def test_clear_history(self) -> None:
        """Test clearing conversation history."""
        brain = AIBrain()
        brain.history.append({"role": "user", "content": "test"})
        brain.clear_history()
        assert len(brain.history) == 1  # Only system message

    def test_get_history(self) -> None:
        """Test retrieving history."""
        brain = AIBrain()
        history = brain.get_history()
        assert isinstance(history, list)
        assert len(history) >= 1


class TestSearchEngine:
    """Test search engine."""

    def test_search_engine_initialization(self) -> None:
        """Test search engine initializes."""
        engine = SearchEngine()
        assert engine.base_url is not None
        assert engine.weather_url is not None


class TestCommandHandler:
    """Test command handler."""

    def test_command_handler_initialization(self) -> None:
        """Test command handler initializes."""
        handler = CommandHandler()
        assert handler.allowlist is not None
        assert handler.denylist is not None

    def test_denylist_check(self) -> None:
        """Test denied command is blocked."""
        handler = CommandHandler()
        allowed, reason = handler._is_allowed("rm -rf /")
        assert not allowed
        assert "denied" in reason.lower()

    def test_allowlist_enforcement(self) -> None:
        """Test allowlist enforcement when set."""
        handler = CommandHandler()
        if handler.allowlist:
            # With allowlist, only allowed commands work
            allowed, _ = handler._is_allowed("any random command")
            assert not allowed


class TestVoiceAssistant:
    """Test voice assistant."""

    def test_voice_assistant_initialization(self) -> None:
        """Test voice assistant initializes."""
        assistant = VoiceAssistant()
        assert assistant.mic_index is not None


class TestConfig:
    """Test configuration system."""

    def test_config_values_loaded(self) -> None:
        """Test configuration values are loaded."""
        assert Config.assistant_name is not None
        assert Config.user_name is not None
        assert Config.api is not None
        assert Config.voice is not None
        assert Config.memory is not None

    def test_dirs_creation(self) -> None:
        """Test directory creation."""
        Config.ensure_dirs()
        assert Path("logs").exists()
        assert Path("data").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
