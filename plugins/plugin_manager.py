"""Plugin system for JARVIS extensibility."""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Optional, Type, List
from core.logger import Logger

logger = Logger.get(__name__)


class PluginBase:
    """Base class for all plugins."""

    def __init__(self) -> None:
        self.name: str = self.__class__.__name__
        self.version: str = "1.0.0"
        self.enabled: bool = True
        self.description: str = ""

    def on_load(self) -> None:
        """Called when plugin is loaded."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        pass

    def on_enable(self) -> None:
        """Called when plugin is enabled."""
        self.enabled = True

    def on_disable(self) -> None:
        """Called when plugin is disabled."""
        self.enabled = False

    def execute(self, command: str, *args, **kwargs):
        """Execute plugin command."""
        raise NotImplementedError(f"{self.name} does not implement execute()")


class PluginManager:
    """Manages plugin loading and execution."""

    def __init__(self, plugins_dir: str = "plugins") -> None:
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.plugins: Dict[str, PluginBase] = {}
        self._load_builtin_plugins()

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        try:
            # Example: Add built-in plugins here
            logger.info("Built-in plugins loaded")
        except Exception as e:
            logger.error(f"Failed to load built-in plugins: {e}")

    def load_plugin(self, plugin_path: str) -> Optional[PluginBase]:
        """Load a plugin from file."""
        try:
            path = Path(plugin_path)
            if not path.exists():
                logger.error(f"Plugin file not found: {plugin_path}")
                return None

            spec = importlib.util.spec_from_file_location(path.stem, path)
            if not spec or not spec.loader:
                logger.error(f"Failed to load plugin spec: {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find PluginBase subclass
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                    plugin_class = obj
                    break

            if not plugin_class:
                logger.error(f"No PluginBase subclass found in {plugin_path}")
                return None

            plugin = plugin_class()
            plugin.on_load()
            self.plugins[plugin.name] = plugin
            logger.info(f"Plugin loaded: {plugin.name}")
            return plugin

        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return None

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        try:
            if name not in self.plugins:
                logger.warning(f"Plugin not found: {name}")
                return False

            plugin = self.plugins[name]
            plugin.on_unload()
            del self.plugins[name]
            logger.info(f"Plugin unloaded: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False

    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        if name not in self.plugins:
            logger.warning(f"Plugin not found: {name}")
            return False

        try:
            plugin = self.plugins[name]
            plugin.on_enable()
            logger.info(f"Plugin enabled: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enable plugin {name}: {e}")
            return False

    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        if name not in self.plugins:
            logger.warning(f"Plugin not found: {name}")
            return False

        try:
            plugin = self.plugins[name]
            plugin.on_disable()
            logger.info(f"Plugin disabled: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable plugin {name}: {e}")
            return False

    def execute_plugin(self, name: str, command: str, *args, **kwargs):
        """Execute plugin command."""
        if name not in self.plugins:
            logger.warning(f"Plugin not found: {name}")
            return None

        plugin = self.plugins[name]
        if not plugin.enabled:
            logger.warning(f"Plugin is disabled: {name}")
            return None

        try:
            return plugin.execute(command, *args, **kwargs)
        except Exception as e:
            logger.error(f"Plugin execution error: {e}")
            return None

    def list_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self.plugins.keys())

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get plugin by name."""
        return self.plugins.get(name)
