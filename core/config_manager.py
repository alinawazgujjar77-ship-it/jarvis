"""Type-safe configuration manager for JARVIS."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API configuration."""
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    search_key: str = os.getenv("SEARCH_API_KEY", "")


@dataclass
class VoiceConfig:
    """Voice configuration."""
    wake_word: str = os.getenv("WAKE_WORD", "jarvis")
    enable_wake_word: bool = os.getenv("ENABLE_WAKE_WORD", "1") == "1"
    voice_name: str = os.getenv("VOICE_NAME", "en-US-GuyNeural")
    mic_device_index: int = int(os.getenv("MIC_DEVICE_INDEX", "-1"))  # -1 = auto


@dataclass
class MemoryConfig:
    """Memory configuration."""
    db_path: str = os.getenv("MEMORY_DB_PATH", "data/jarvis.db")
    max_items: int = int(os.getenv("MEMORY_MAX_ITEMS", "100"))
    ttl_days: int = int(os.getenv("MEMORY_TTL_DAYS", "30"))


@dataclass
class CommandConfig:
    """Command safety configuration."""
    allowlist: list = None
    denylist: list = None

    def __post_init__(self) -> None:
        if self.allowlist is None:
            allowlist_str = os.getenv("COMMAND_ALLOWLIST", "")
            self.allowlist = [x.strip() for x in allowlist_str.split(",") if x.strip()]
        if self.denylist is None:
            denylist_str = os.getenv("COMMAND_DENYLIST", "rm,format,shutdown,reboot,del,wipe")
            self.denylist = [x.strip() for x in denylist_str.split(",") if x.strip()]


@dataclass
class AIConfig:
    """AI configuration."""
    auto_web_search: bool = os.getenv("AUTO_WEB_SEARCH_ENABLE", "1") == "1"
    model_timeout: int = int(os.getenv("MODEL_TIMEOUT", "30"))
    max_history: int = int(os.getenv("MAX_HISTORY", "20"))
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")


class Config:
    """Central configuration manager."""

    api: APIConfig = APIConfig()
    voice: VoiceConfig = VoiceConfig()
    memory: MemoryConfig = MemoryConfig()
    command: CommandConfig = CommandConfig()
    ai: AIConfig = AIConfig()

    # Application settings
    assistant_name: str = os.getenv("ASSISTANT_NAME", "Jarvis")
    user_name: str = os.getenv("USER_NAME", "User")
    debug_mode: bool = os.getenv("DEBUG_MODE", "0") == "1"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Ensure all required directories exist."""
        Path(cls.memory.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
