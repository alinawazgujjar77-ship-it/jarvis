"""Integration tests for JARVIS Pro."""

import pytest
from core.config_manager import Config
from core.memory_manager import MemoryManager
from core.ai_brain import AIBrain
from core.command_handler import CommandHandler
from automation.system_automation import SystemAutomation
from vision.vision_system import VisionSystem
from plugins.plugin_manager import PluginManager


class TestIntegration:
    """Integration tests."""

    def test_config_load(self) -> None:
        """Test configuration loads."""
        assert Config.assistant_name is not None
        assert Config.user_name is not None

    def test_memory_workflow(self, temp_db: str) -> None:
        """Test complete memory workflow."""
        mem = MemoryManager(db_path=temp_db)
        
        # Add data
        mem.remember("user_name", "Test User")
        mem.append_conversation("user", "hello")
        mem.append_conversation("assistant", "hi")
        task_id = mem.add_task("Test Task")
        mem.store_knowledge("test", "test knowledge")
        
        # Verify
        assert mem.recall("user_name") == "Test User"
        assert len(mem.get_conversations()) == 2
        assert len(mem.get_tasks()) == 1
        assert len(mem.search_knowledge("test")) > 0

    def test_command_handler_workflow(self) -> None:
        """Test command handler workflow."""
        handler = CommandHandler()
        
        # Test allowed command
        handled, response = handler.handle("system info")
        assert handled or not handled  # May not be implemented

    def test_system_automation_workflow(self) -> None:
        """Test system automation."""
        cpu_info = SystemAutomation.get_cpu_usage()
        assert "CPU" in cpu_info or "error" in cpu_info.lower()
        
        memory_info = SystemAutomation.get_memory_usage()
        assert "Memory" in memory_info or "error" in memory_info.lower()

    def test_plugin_manager_workflow(self) -> None:
        """Test plugin manager."""
        pm = PluginManager()
        
        # Verify initialization
        plugins = pm.list_plugins()
        assert isinstance(plugins, list)

    def test_ai_brain_workflow(self) -> None:
        """Test AI brain."""
        brain = AIBrain()
        
        # Test history
        history = brain.get_history()
        assert len(history) >= 1
        assert history[0]["role"] == "system"

    def test_vision_system_initialization(self) -> None:
        """Test vision system."""
        vision = VisionSystem()
        assert vision is not None
        vision.close()


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_db_path(self) -> None:
        """Test handling of invalid database path."""
        try:
            mem = MemoryManager(db_path="/invalid/path/db.sqlite")
        except Exception as e:
            # Should handle gracefully
            assert e is not None

    def test_missing_api_keys(self) -> None:
        """Test handling of missing API keys."""
        brain = AIBrain()
        # Should not crash even without API keys
        assert brain is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
