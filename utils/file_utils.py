"""File utilities for JARVIS."""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from core.logger import Logger

logger = Logger.get(__name__)


def find_files(pattern: str, path: str = ".", max_results: int = 10) -> List[str]:
    """Find files matching pattern."""
    try:
        results = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if pattern.lower() in file.lower():
                    results.append(os.path.join(root, file))
                    if len(results) >= max_results:
                        return results
        return results
    except Exception as e:
        logger.error(f"File search error: {e}")
        return []


def read_file(path: str, encoding: str = "utf-8") -> Optional[str]:
    """Read file contents."""
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"File read error: {e}")
        return None


def write_file(path: str, content: str, encoding: str = "utf-8") -> bool:
    """Write to file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.info(f"File written: {path}")
        return True
    except Exception as e:
        logger.error(f"File write error: {e}")
        return False


def delete_file(path: str) -> bool:
    """Delete a file."""
    try:
        os.remove(path)
        logger.info(f"File deleted: {path}")
        return True
    except Exception as e:
        logger.error(f"File delete error: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """Copy a file."""
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.info(f"File copied: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"File copy error: {e}")
        return False


def get_file_size(path: str) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return os.path.getsize(path)
    except Exception as e:
        logger.error(f"Failed to get file size: {e}")
        return None


def create_directory(path: str) -> bool:
    """Create directory."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory created: {path}")
        return True
    except Exception as e:
        logger.error(f"Directory creation error: {e}")
        return False
