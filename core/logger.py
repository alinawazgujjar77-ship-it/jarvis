"""Professional logging system for JARVIS."""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class Logger:
    """Centralized logging manager with file rotation and colored output."""

    _instance: Optional['Logger'] = None
    _loggers: dict = {}

    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize logging system."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._setup_root_logger()

    def _setup_root_logger(self) -> None:
        """Setup root logger with console and file handlers."""
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root.addHandler(console_handler)

        # File handler with rotation
        log_file = self.log_dir / f"jarvis_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

    @staticmethod
    def get(name: str) -> logging.Logger:
        """Get or create a logger for the given name."""
        if name not in Logger._loggers:
            Logger._loggers[name] = logging.getLogger(name)
        return Logger._loggers[name]
