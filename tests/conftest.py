"""Test utilities and fixtures for JARVIS Pro."""

import os
import sqlite3
from pathlib import Path
from typing import Generator
import pytest


@pytest.fixture
def temp_db() -> Generator[str, None, None]:
    """Create temporary test database."""
    db_path = "test_temp.db"
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create temporary test file."""
    file_path = "test_temp.txt"
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary test directory."""
    dir_path = Path("test_temp_dir")
    dir_path.mkdir(exist_ok=True)
    yield dir_path
    if dir_path.exists():
        import shutil
        shutil.rmtree(dir_path)


class MockAI:
    """Mock AI for testing."""

    def ask(self, prompt: str) -> str:
        return f"Mock response to: {prompt[:20]}"

    def clear_history(self) -> None:
        pass


class MockVoice:
    """Mock voice assistant for testing."""

    def __init__(self) -> None:
        self.last_spoken = ""

    def speak(self, text: str) -> None:
        self.last_spoken = text

    def listen(self) -> str:
        return "test input"


class MockMemory:
    """Mock memory for testing."""

    def __init__(self) -> None:
        self.data = {}

    def remember(self, key: str, value) -> None:
        self.data[key] = value

    def recall(self, key: str, default=None):
        return self.data.get(key, default)

    def append_conversation(self, role: str, content: str) -> None:
        pass

    def get_conversations(self):
        return []
