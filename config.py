import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")

# Wake word configuration
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")
ENABLE_WAKE_WORD = os.getenv("ENABLE_WAKE_WORD", "1") == "1"

# Memory pruning defaults
MEMORY_MAX_ITEMS = int(os.getenv("MEMORY_MAX_ITEMS", "100"))
MEMORY_TTL_DAYS = int(os.getenv("MEMORY_TTL_DAYS", "30"))

# Command allowlist/denylist safety
# If COMMAND_ALLOWLIST is non-empty, only commands containing one of these substrings are allowed to run.
COMMAND_ALLOWLIST = os.getenv("COMMAND_ALLOWLIST", "").split(",") if os.getenv("COMMAND_ALLOWLIST", "") else []
# Commands containing any of these substrings will be rejected.
COMMAND_DENYLIST = os.getenv("COMMAND_DENYLIST", "rm ,format ,shutdown ,reboot ,del ,wipe ").split(",")

# Auto web search behavior
AUTO_WEB_SEARCH_ENABLE = os.getenv("AUTO_WEB_SEARCH_ENABLE", "1") == "1"

ASSISTANT_NAME = "Jarvis"
USER_NAME = os.getenv("USER_NAME", "Fizan")
VOICE_NAME = "en-US-GuyNeural"
MIC_DEVICE_INDEX = int(os.getenv("MIC_DEVICE_INDEX", "1"))
