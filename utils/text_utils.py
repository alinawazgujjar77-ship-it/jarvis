"""Utility functions for JARVIS."""

import string
import re
from typing import List, Optional
from core.logger import Logger

logger = Logger.get(__name__)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially harmful characters
    dangerous_chars = "<>|&;$()\n\r"
    for char in dangerous_chars:
        text = text.replace(char, "")
    
    return text


def is_command(text: str) -> bool:
    """Check if input looks like a command."""
    command_prefixes = ("open", "search", "calculate", "find", "take", "get", "set")
    return any(text.lower().startswith(prefix) for prefix in command_prefixes)


def extract_numbers(text: str) -> List[float]:
    """Extract numbers from text."""
    pattern = r"[-+]?\d*\.?\d+"
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r"https?://[^\s]+"
    matches = re.findall(url_pattern, text)
    return matches


def format_response(text: str, max_length: int = 500) -> str:
    """Format response for display."""
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text


def is_question(text: str) -> bool:
    """Check if text is a question."""
    question_words = ("what", "how", "why", "when", "where", "who", "which")
    return any(text.lower().startswith(word) for word in question_words) or text.endswith("?")


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (basic)."""
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def get_keywords(text: str, num_keywords: int = 5) -> List[str]:
    """Extract keywords from text."""
    # Remove common stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'am', 'in', 'on', 'at',
        'for', 'to', 'of', 'with', 'by', 'from', 'as', 'be', 'been', 'being'
    }
    
    words = text.lower().split()
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    
    return keywords[:num_keywords]
