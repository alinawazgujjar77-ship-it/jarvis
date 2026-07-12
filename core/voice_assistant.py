"""Enhanced voice assistant with speech recognition and TTS."""

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
    """Handles voice input and output."""

    def __init__(self) -> None:
        self.recognizer = None
        self.mic_index = Config.voice.mic_device_index
        self._init_voice()

    def _init_voice(self) -> None:
        """Initialize voice components."""
        if sr:
            try:
                self.recognizer = sr.Recognizer()
                logger.info("Speech recognizer initialized")
            except Exception as e:
                logger.warning(f"Speech recognizer initialization failed: {e}")

        if pygame:
            try:
                pygame.mixer.init()
                logger.info("Audio mixer initialized")
            except Exception as e:
                logger.warning(f"Audio mixer initialization failed: {e}")

    def speak(self, text: str) -> None:
        """Convert text to speech."""
        if not text or not edge_tts or not pygame:
            if not edge_tts:
                logger.warning("edge_tts not available")
            if not pygame:
                logger.warning("pygame not available")
            return

        try:
            logger.info(f"Speaking: {text[:50]}...")
            asyncio.run(self._speak_async(text))
        except Exception as e:
            logger.error(f"Speech error: {e}")
        finally:
            if os.path.exists("voice.mp3"):
                try:
                    os.remove("voice.mp3")
                except Exception as e:
                    logger.warning(f"Failed to remove temp audio file: {e}")

    @staticmethod
    async def _speak_async(text: str) -> None:
        """Async TTS generation and playback."""
        try:
            communicate = edge_tts.Communicate(text, Config.voice.voice_name)
            await communicate.save("voice.mp3")

            if pygame and pygame.mixer:
                pygame.mixer.music.load("voice.mp3")
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.music.unload()
        except Exception as e:
            logger.error(f"Async speech error: {e}")

    def listen(self, timeout: int = 10, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for user input via microphone."""
        if not sr or not self.recognizer:
            logger.warning("Speech recognition not available")
            return None

        try:
            # Auto-detect microphone if not specified
            mic_index = self.mic_index if self.mic_index >= 0 else None
            
            with sr.Microphone(device_index=mic_index) as source:
                logger.info("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            try:
                command = self.recognizer.recognize_google(audio)
                logger.info(f"Recognized: {command}")
                return command
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Google API error: {e}")
                return None

        except sr.RequestError as e:
            logger.error(f"Microphone error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during listening: {e}")
            return None

    @staticmethod
    def list_microphones() -> list:
        """List available microphones."""
        if not sr:
            logger.warning("Speech recognition not available")
            return []

        try:
            mics = sr.Microphone.list_microphone_names()
            logger.info(f"Found {len(mics)} microphones")
            return list(enumerate(mics))
        except Exception as e:
            logger.error(f"Failed to list microphones: {e}")
            return []
