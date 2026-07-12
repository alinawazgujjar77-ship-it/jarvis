#!/usr/bin/env python3
"""Main application entry point for JARVIS Pro."""

import sys
import argparse
from pathlib import Path
from core.logger import Logger
from core.config_manager import Config
from core.memory_manager import MemoryManager
from core.ai_brain import AIBrain
from core.voice_assistant import VoiceAssistant
from core.command_handler import CommandHandler
from gui.gui import JARVSGUI

logger = Logger.get(__name__)


class JARVISApplication:
    """Main JARVIS Pro application."""

    def __init__(self, use_gui: bool = True) -> None:
        self.use_gui = use_gui
        self.memory = MemoryManager(Config.memory.db_path)
        self.ai_brain = AIBrain()
        self.voice = VoiceAssistant()
        self.command_handler = CommandHandler()
        self.gui = None
        logger.info(f"JARVIS Pro initialized (GUI: {use_gui})")

    def _process_input(self, user_input: str) -> str:
        """Process user input and return response."""
        if not user_input or not user_input.strip():
            return "Please provide input."

        command = user_input.strip()
        logger.info(f"Processing: {command}")

        # Store in memory
        self.memory.append_conversation("user", command)

        # Try command handler first
        handled, response = self.command_handler.handle(command)
        if handled:
            self.memory.append_conversation("assistant", response)
            logger.info(f"Command handled: {response[:50]}")
            return response

        # Fall back to AI
        try:
            response = self.ai_brain.ask(command)
            self.memory.append_conversation("assistant", response)
            logger.info(f"AI response: {response[:50]}")
            return response
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            error_msg = f"I encountered an error: {str(e)}"
            self.memory.append_conversation("assistant", error_msg)
            return error_msg

    def run_gui(self) -> None:
        """Run GUI mode."""
        logger.info("Starting GUI mode")
        self.gui = JARVSGUI(on_submit=self._process_input)
        
        # Welcome message
        welcome = f"Welcome {Config.user_name}! I'm {Config.assistant_name}."
        self.gui._display_message(Config.assistant_name, welcome)
        
        try:
            self.gui.run()
        except Exception as e:
            logger.error(f"GUI error: {e}")
            self.run_cli()

    def run_cli(self) -> None:
        """Run CLI mode."""
        logger.info("Starting CLI mode")
        print(f"\n{Config.assistant_name} Pro CLI")
        print(f"Welcome {Config.user_name}!\n")

        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in {"exit", "quit", "bye"}:
                    print(f"{Config.assistant_name}: Goodbye!")
                    self.memory.append_conversation("assistant", "Goodbye!")
                    break

                if not user_input:
                    continue

                response = self._process_input(user_input)
                print(f"{Config.assistant_name}: {response}\n")

            except KeyboardInterrupt:
                print(f"\n{Config.assistant_name}: Goodbye!")
                break
            except Exception as e:
                logger.error(f"CLI error: {e}")
                print(f"Error: {e}")

    def run_voice(self) -> None:
        """Run voice mode."""
        logger.info("Starting voice mode")
        print(f"{Config.assistant_name} Voice Mode")
        print(f"Say '{Config.voice.wake_word}' to start\n")

        while True:
            try:
                # Listen for input
                user_input = self.voice.listen()
                if not user_input:
                    continue

                # Check for wake word
                if Config.voice.enable_wake_word:
                    if Config.voice.wake_word.lower() not in user_input.lower():
                        continue
                    # Remove wake word
                    user_input = user_input.lower().replace(
                        Config.voice.wake_word.lower(), ""
                    ).strip()

                if not user_input:
                    self.voice.speak("Yes?")
                    continue

                if user_input.lower() in {"exit", "quit", "bye"}:
                    self.voice.speak(f"Goodbye {Config.user_name}!")
                    break

                # Process and respond
                response = self._process_input(user_input)
                self.voice.speak(response)

            except KeyboardInterrupt:
                self.voice.speak("Goodbye!")
                break
            except Exception as e:
                logger.error(f"Voice mode error: {e}")
                self.voice.speak(f"Error: {str(e)}")

    def run(self) -> None:
        """Run application."""
        Config.ensure_dirs()
        
        if self.use_gui:
            self.run_gui()
        else:
            self.run_cli()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="JARVIS Pro - Advanced AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Run GUI mode
  python main.py --cli        # Run CLI mode
  python main.py --voice      # Run voice mode
  python main.py --debug      # Run with debug logging
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode instead of GUI"
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Run in voice mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    try:
        if args.debug:
            Config.debug_mode = True
            logger.info("Debug mode enabled")
        
        app = JARVISApplication(use_gui=not args.cli and not args.voice)
        
        if args.voice:
            app.run_voice()
        elif args.cli:
            app.run_cli()
        else:
            app.run_gui()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
