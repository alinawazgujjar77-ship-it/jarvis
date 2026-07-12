"""Enhanced command handler for system operations."""

import re
import os
import platform
import subprocess
from typing import Tuple, Optional
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)

try:
    import psutil
except ImportError:
    psutil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None


class CommandHandler:
    """Handles system commands with safety checks."""

    def __init__(self) -> None:
        self.allowlist = Config.command.allowlist
        self.denylist = Config.command.denylist

    def _is_allowed(self, command: str) -> Tuple[bool, str]:
        """Check if command is allowed."""
        lc = command.lower()
        
        # Check denylist
        for denied in self.denylist:
            if denied.lower() in lc:
                return False, f"Command contains denied pattern: '{denied}'"
        
        # Check allowlist if present
        if self.allowlist:
            for allowed in self.allowlist:
                if allowed.lower() in lc:
                    return True, ""
            return False, "Command not in allowlist"
        
        return True, ""

    def handle(self, command: str) -> Tuple[bool, str]:
        """Process system command."""
        if not command or not command.strip():
            return True, "No command provided."

        # Safety check
        allowed, reason = self._is_allowed(command)
        if not allowed:
            logger.warning(f"Command blocked: {reason}")
            return True, f"Command blocked: {reason}"

        c = command.strip()
        lc = c.lower()

        # Open application
        if re.match(r"open\s+(app\s+)?(.+)", lc):
            app = re.match(r"open\s+(?:app\s+)?(.+)", lc).group(1)
            return self._open_app(app)

        # Open URL
        if re.match(r"(?:open|visit|go to)\s+(.+)", lc):
            url = re.match(r"(?:open|visit|go to)\s+(.+)", lc).group(1)
            return self._open_url(url)

        # System info
        if "system info" in lc or "system information" in lc:
            return self._system_info()

        # Battery status
        if "battery" in lc:
            return self._battery_status()

        # Clipboard operations
        if "copy" in lc:
            text = re.sub(r"copy\s+", "", lc)
            return self._copy_to_clipboard(text)

        if "paste" in lc:
            return self._paste_from_clipboard()

        # No command matched
        return False, ""

    def _open_app(self, app_name: str) -> Tuple[bool, str]:
        """Open an application."""
        try:
            if os.path.exists(app_name):
                if platform.system() == "Windows":
                    os.startfile(app_name)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", app_name])
                else:
                    subprocess.Popen(["xdg-open", app_name])
                return True, f"Opened {app_name}"
            else:
                proc = subprocess.Popen(
                    app_name.split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, f"Started {app_name} (PID: {proc.pid})"
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return True, f"Failed to open {app_name}: {str(e)}"

    def _open_url(self, url: str) -> Tuple[bool, str]:
        """Open a URL in default browser."""
        try:
            if not url.startswith(("http://", "https://", "www.")):
                url = f"https://{url}"
            
            if platform.system() == "Windows":
                os.startfile(url)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
            
            return True, f"Opening {url}"
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            return True, f"Failed to open URL: {str(e)}"

    def _system_info(self) -> Tuple[bool, str]:
        """Get system information."""
        try:
            if not psutil:
                return True, "psutil not installed"
            
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            
            info = f"CPU: {cpu}% | Memory: {memory.percent}% | Disk: {disk.percent}%"
            return True, info
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return True, f"Error getting system info: {str(e)}"

    def _battery_status(self) -> Tuple[bool, str]:
        """Get battery status."""
        try:
            if not psutil:
                return True, "psutil not installed"
            
            battery = psutil.sensors_battery()
            if battery:
                status = "charging" if battery.power_plugged else "discharging"
                return True, f"Battery: {battery.percent}% ({status})"
            return True, "No battery information available"
        except Exception as e:
            logger.error(f"Failed to get battery status: {e}")
            return True, f"Error getting battery status: {str(e)}"

    def _copy_to_clipboard(self, text: str) -> Tuple[bool, str]:
        """Copy text to clipboard."""
        try:
            if not pyperclip:
                return True, "pyperclip not installed"
            
            pyperclip.copy(text)
            return True, f"Copied to clipboard: {text[:50]}"
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return True, f"Error copying to clipboard: {str(e)}"

    def _paste_from_clipboard(self) -> Tuple[bool, str]:
        """Paste from clipboard."""
        try:
            if not pyperclip:
                return True, "pyperclip not installed"
            
            content = pyperclip.paste()
            return True, f"Clipboard: {content[:100]}"
        except Exception as e:
            logger.error(f"Failed to paste from clipboard: {e}")
            return True, f"Error pasting from clipboard: {str(e)}"
