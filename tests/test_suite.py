import json
import os
from datetime import datetime, timedelta
from memory.memory import MemoryManager


def test_memory_basic():
    path = "test_memory.json"
    if os.path.exists(path):
        os.remove(path)
    m = MemoryManager(path=path)
    m.remember("a", 1)
    assert m.recall("a") == 1
    m.append_conversation("user", "hello")
    m.append_conversation("assistant", "hi")
    convs = m.get_conversations()
    assert len(convs) == 2
    m.prune_conversations(max_items=1, ttl_days=365)
    convs = m.get_conversations()
    assert len(convs) == 1
    os.remove(path)


def test_calculator():
    from tools.utils import calculator
    assert calculator("1+2") == 3
    assert "error" in str(calculator("__import__('os').system('ls')" )).lower()


def test_command_handler():
    from commands.handler import CommandHandler
    ch = CommandHandler()
    handled, resp = ch.handle("calculate 2 + 2")
    assert handled and "4" in resp
    handled, resp = ch.handle("find file *.py")
    assert handled
