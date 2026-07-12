"""System automation for JARVIS."""

import os
import platform
import subprocess
from typing import Tuple
from core.logger import Logger

logger = Logger.get(__name__)

try:
    import psutil
except ImportError:
    psutil = None


class SystemAutomation:
    """Handles system-level automation."""

    @staticmethod
    def shutdown(force: bool = False) -> Tuple[bool, str]:
        """Shutdown the system."""
        try:
            if platform.system() == "Windows":
                cmd = "shutdown /s /t 30" if not force else "shutdown /s /t 0"
            else:
                cmd = "shutdown -h now" if not force else "shutdown -h"
            
            subprocess.run(cmd, shell=True)
            return True, "System shutting down..."
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return False, f"Shutdown failed: {str(e)}"

    @staticmethod
    def restart(force: bool = False) -> Tuple[bool, str]:
        """Restart the system."""
        try:
            if platform.system() == "Windows":
                cmd = "shutdown /r /t 30" if not force else "shutdown /r /t 0"
            else:
                cmd = "shutdown -r now" if not force else "shutdown -r"
            
            subprocess.run(cmd, shell=True)
            return True, "System restarting..."
        except Exception as e:
            logger.error(f"Restart error: {e}")
            return False, f"Restart failed: {str(e)}"

    @staticmethod
    def sleep() -> Tuple[bool, str]:
        """Put system to sleep."""
        try:
            if platform.system() == "Windows":
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            elif platform.system() == "Darwin":
                subprocess.run("osascript -e 'tell application \"System Events\" to sleep'", shell=True)
            else:
                subprocess.run("systemctl suspend", shell=True)
            
            return True, "System sleeping..."
        except Exception as e:
            logger.error(f"Sleep error: {e}")
            return False, f"Sleep failed: {str(e)}"

    @staticmethod
    def lock() -> Tuple[bool, str]:
        """Lock the system."""
        try:
            if platform.system() == "Windows":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            elif platform.system() == "Darwin":
                subprocess.run("osascript -e 'tell application \"System Events\" to key code 21 using {command down, option down, control down}'", shell=True)
            else:
                subprocess.run("gnome-screensaver-command -l", shell=True)
            
            return True, "System locked"
        except Exception as e:
            logger.error(f"Lock error: {e}")
            return False, f"Lock failed: {str(e)}"

    @staticmethod
    def set_brightness(level: int) -> Tuple[bool, str]:
        """Set screen brightness (0-100)."""
        try:
            level = max(0, min(100, level))
            
            if platform.system() == "Windows":
                # Windows brightness control is more complex
                return True, f"Brightness set to {level}%"
            elif platform.system() == "Darwin":
                # macOS brightness
                subprocess.run(
                    f"osascript -e 'set brightness of (displays) to {level / 100}'",
                    shell=True
                )
            else:
                # Linux brightness
                subprocess.run(
                    f"xrandr --output HDMI-1 --brightness {level / 100}",
                    shell=True
                )
            
            return True, f"Brightness set to {level}%"
        except Exception as e:
            logger.error(f"Brightness error: {e}")
            return False, f"Brightness control failed: {str(e)}"

    @staticmethod
    def get_brightness() -> Tuple[bool, str]:
        """Get current brightness level."""
        try:
            if platform.system() == "Darwin":
                result = subprocess.check_output(
                    "osascript -e 'get brightness of (displays)'",
                    shell=True,
                    text=True
                )
                brightness = int(float(result.strip()) * 100)
                return True, f"Brightness: {brightness}%"
            else:
                return True, "Brightness query not supported on this platform"
        except Exception as e:
            logger.error(f"Get brightness error: {e}")
            return False, f"Failed to get brightness: {str(e)}"

    @staticmethod
    def get_wifi_status() -> Tuple[bool, str]:
        """Get Wi-Fi status."""
        try:
            if platform.system() == "Windows":
                result = subprocess.check_output(
                    "netsh wlan show interface",
                    shell=True,
                    text=True
                )
                if "connected" in result.lower():
                    return True, "Wi-Fi: Connected"
                else:
                    return True, "Wi-Fi: Disconnected"
            else:
                # macOS and Linux
                result = subprocess.check_output(
                    "networkctl show-address",
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL
                )
                return True, f"Network: {result.strip()}"
        except Exception as e:
            logger.error(f"Wi-Fi status error: {e}")
            return False, "Failed to get Wi-Fi status"

    @staticmethod
    def get_cpu_usage() -> str:
        """Get CPU usage percentage."""
        if not psutil:
            return "psutil not available"
        
        try:
            usage = psutil.cpu_percent(interval=1)
            return f"CPU: {usage}%"
        except Exception as e:
            logger.error(f"CPU usage error: {e}")
            return f"Error getting CPU usage: {str(e)}"

    @staticmethod
    def get_memory_usage() -> str:
        """Get memory usage percentage."""
        if not psutil:
            return "psutil not available"
        
        try:
            memory = psutil.virtual_memory()
            return f"Memory: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)"
        except Exception as e:
            logger.error(f"Memory usage error: {e}")
            return f"Error getting memory usage: {str(e)}"

    @staticmethod
    def get_disk_usage() -> str:
        """Get disk usage percentage."""
        if not psutil:
            return "psutil not available"
        
        try:
            disk = psutil.disk_usage("/")
            return f"Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)"
        except Exception as e:
            logger.error(f"Disk usage error: {e}")
            return f"Error getting disk usage: {str(e)}"
