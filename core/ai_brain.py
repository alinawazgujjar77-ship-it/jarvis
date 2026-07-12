"""Advanced multi-model AI brain for JARVIS."""

import copy
from typing import List, Dict, Optional
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)

try:
    from google import genai
except ImportError:
    genai = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import requests
except ImportError:
    requests = None


class AIBrain:
    """Multi-model AI with Gemini (primary), OpenAI (backup), and Ollama (offline)."""

    def __init__(self) -> None:
        self.history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": f"You are {Config.assistant_name}, a helpful digital assistant for {Config.user_name}. Keep responses clear, polite, and useful."
            }
        ]
        self.gemini_client = self._init_gemini()
        self.openai_client = self._init_openai()
        self.ollama_available = self._check_ollama()
        logger.info("AIBrain initialized")

    @staticmethod
    def _init_gemini() -> Optional[object]:
        """Initialize Gemini client."""
        if not genai or not Config.api.gemini_key:
            logger.debug("Gemini not available")
            return None
        try:
            genai.configure(api_key=Config.api.gemini_key)
            logger.info("Gemini client initialized")
            return genai
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return None

    @staticmethod
    def _init_openai() -> Optional[OpenAI]:
        """Initialize OpenAI client."""
        if not OpenAI or not Config.api.openai_key:
            logger.debug("OpenAI not available")
            return None
        try:
            client = OpenAI(api_key=Config.api.openai_key)
            logger.info("OpenAI client initialized")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return None

    @staticmethod
    def _check_ollama() -> bool:
        """Check if Ollama is available."""
        if not requests:
            return False
        try:
            response = requests.get(f"{Config.ai.ollama_url}/api/tags", timeout=2)
            available = response.status_code == 200
            if available:
                logger.info("Ollama is available")
            return available
        except Exception:
            logger.debug("Ollama not available")
            return False

    def ask(self, prompt: str) -> str:
        """Ask the AI a question."""
        if not prompt or not prompt.strip():
            return "Please say something so I can help."

        self.history.append({"role": "user", "content": prompt.strip()})
        response = self._generate_response()
        self.history.append({"role": "assistant", "content": response})

        # Keep history manageable
        if len(self.history) > Config.ai.max_history:
            self.history = self.history[:1] + self.history[-(Config.ai.max_history - 1):]

        return response

    def _generate_response(self) -> str:
        """Generate response using available models."""
        try:
            # Try Gemini first
            if self.gemini_client:
                return self._ask_gemini()

            # Fall back to OpenAI
            if self.openai_client:
                return self._ask_openai()

            # Fall back to Ollama
            if self.ollama_available:
                return self._ask_ollama()

            return "AI is not configured. Please set up API keys or Ollama."
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"Error: {e}"

    def _ask_gemini(self) -> str:
        """Query Gemini API."""
        try:
            model = self.gemini_client.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                self.history[-1]["content"],
                generation_config={
                    "max_output_tokens": 1000,
                    "temperature": 0.7,
                }
            )
            text = response.text if response else "No response"
            logger.debug("Gemini response generated")
            return text.strip()
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")
            raise

    def _ask_openai(self) -> str:
        """Query OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.history[-5:],  # Use last 5 messages for context
                max_tokens=1000,
                temperature=0.7,
            )
            text = response.choices[0].message.content
            logger.debug("OpenAI response generated")
            return text.strip()
        except Exception as e:
            logger.warning(f"OpenAI failed: {e}")
            raise

    def _ask_ollama(self) -> str:
        """Query Ollama (offline mode)."""
        try:
            # Get last user message
            user_message = self.history[-1]["content"]
            
            response = requests.post(
                f"{Config.ai.ollama_url}/api/generate",
                json={
                    "model": "mistral",
                    "prompt": user_message,
                    "stream": False,
                },
                timeout=Config.ai.model_timeout,
            )
            data = response.json()
            text = data.get("response", "No response")
            logger.debug("Ollama response generated")
            return text.strip()
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
            raise

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = self.history[:1]  # Keep system message
        logger.debug("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return copy.deepcopy(self.history[1:])  # Exclude system message
