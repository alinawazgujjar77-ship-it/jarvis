"""Advanced AI brain supporting multiple models with fallback."""

import copy
from typing import Optional, List, Dict
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
    """Multi-model AI system with automatic fallback."""

    def __init__(self) -> None:
        self.history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": f"You are {Config.assistant_name}, a helpful digital assistant for {Config.user_name}. Keep responses clear, polite, and useful."
            }
        ]
        self.gemini_client = None
        self.openai_client = None
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize AI clients."""
        if genai and Config.api.gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=Config.api.gemini_key)
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")

        if OpenAI and Config.api.openai_key:
            try:
                self.openai_client = OpenAI(api_key=Config.api.openai_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")

    def ask(self, prompt: str) -> str:
        """Process user prompt and return response."""
        if not prompt or not prompt.strip():
            return "Please say something so I can help."

        self.history.append({"role": "user", "content": prompt.strip()})
        
        try:
            response = self._generate_response()
            self.history.append({"role": "assistant", "content": response})
            
            # Keep history manageable
            if len(self.history) > Config.ai.max_history:
                self.history = self.history[:1] + self.history[-(Config.ai.max_history - 1):]
            
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)}"

    def _generate_response(self) -> str:
        """Generate response using available AI models."""
        # Try Gemini first
        if self.gemini_client:
            try:
                response = self._ask_gemini(self.history)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Gemini error: {e}")

        # Fall back to OpenAI
        if self.openai_client:
            try:
                response = self._ask_openai(self.history)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"OpenAI error: {e}")

        # Try Ollama for offline mode
        if requests:
            try:
                response = self._ask_ollama(self.history)
                if response:
                    return response
            except Exception as e:
                logger.warning(f"Ollama error: {e}")

        return "I'm not configured properly. Please set up API keys or Ollama."

    @staticmethod
    def _ask_gemini(history: List[Dict[str, str]]) -> Optional[str]:
        """Query Gemini API."""
        try:
            if not genai:
                return None
            
            # Build prompt from history
            recent = history[-6:]
            prompt_parts = []
            for m in recent:
                prompt_parts.append(f"{m['role'].upper()}: {m['content']}")
            prompt = "\n".join(prompt_parts)

            response = genai.Client().models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            text = getattr(response, "text", None)
            return str(text).strip() if text else None
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    @staticmethod
    def _ask_openai(history: List[Dict[str, str]]) -> Optional[str]:
        """Query OpenAI API."""
        try:
            if not OpenAI:
                return None

            client = OpenAI(api_key=Config.api.openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=history,
                max_tokens=600,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None

    @staticmethod
    def _ask_ollama(history: List[Dict[str, str]]) -> Optional[str]:
        """Query Ollama API for offline mode."""
        try:
            if not requests:
                return None

            url = f"{Config.ai.ollama_url}/api/chat"
            payload = {
                "model": "mistral",
                "messages": history,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=Config.ai.model_timeout)
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = self.history[:1]  # Keep system message
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        return copy.deepcopy(self.history)
