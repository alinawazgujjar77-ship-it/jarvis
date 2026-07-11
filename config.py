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

ASSISTANT_NAME = "Jarvis"
USER_NAME = os.getenv("USER_NAME", "Fizan")
VOICE_NAME = "en-US-GuyNeural"
MIC_DEVICE_INDEX = int(os.getenv("MIC_DEVICE_INDEX", "1"))
