"""Voice assistant with speech recognition and text-to-speech."""

import asyncio
import os
from typing import Optional
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pygame
except ImportError:
    pygame = None


class VoiceAssistant:
    """Handle voice input and output with wake word detection."""

    def __init__(self) -> None:
        self.recognizer: Optional[sr.Recognizer] = sr.Recognizer() if sr else None
        self.wake_word = Config.voice.wake_word.lower()
        self.enable_wake_word = Config.voice.enable_wake_word
        self.voice_name = Config.voice.voice_name
        self.mic_device_index = Config.voice.mic_device_index

        if pygame:
            pygame.mixer.init()
        logger.info("VoiceAssistant initialized")

    async def _speak_async(self, text: str) -> None:
        """Generate speech asynchronously."""
        if not edge_tts:
            logger.warning("edge_tts not installed")
            return

        try:
            communicate = edge_tts.Communicate(text, self.voice_name)
            await communicate.save("voice.mp3")
        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")

    def speak(self, text: str) -> None:
        """Speak text using text-to-speech."""
        if not text:
            return

        logger.info(f"{Config.assistant_name}: {text}")
        print(f"{Config.assistant_name}: {text}")

        if not edge_tts or not pygame:
            logger.warning("Text-to-speech dependencies not available")
            return

        try:
            asyncio.run(self._speak_async(text))
            pygame.mixer.music.load("voice.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
        except Exception as e:
            logger.error(f"Speech playback failed: {e}")
        finally:
            if os.path.exists("voice.mp3"):
                os.remove("voice.mp3")

    def listen(self, timeout: int = 10) -> str:
        """Listen for voice input."""
        if not self.recognizer or not sr:
            logger.warning("Speech recognition not available")
            return ""

        try:
            # Auto-detect microphone if not specified
            device_index = None if self.mic_device_index == -1 else self.mic_device_index

            with sr.Microphone(device_index=device_index) as source:
                logger.debug("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=timeout
                )
        except sr.RequestError as e:
            logger.error(f"Microphone error: {e}")
            return ""
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return ""

        try:
            command = self.recognizer.recognize_google(audio)
            logger.info(f"You: {command}")
            print(f"You: {command}")
            return command
        except sr.RequestError as e:
            logger.error(f"Google API error: {e}")
            return ""
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return ""

    def process_wake_word(self, text: str) -> Optional[str]:
        """Check for wake word and return the command without it."""
        if not self.enable_wake_word or not self.wake_word:
            return text

        text_lower = text.lower()
        if self.wake_word in text_lower:
            # Remove wake word
            idx = text_lower.find(self.wake_word)
            command = (text[:idx] + text[idx + len(self.wake_word):]).strip()
            return command if command else None
        return None
