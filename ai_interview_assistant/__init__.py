"""
AI Interview Assistant - A real-time AI assistant for technical interviews.

This package provides:
- Real-time speech recognition with speaker diarization
- AI-powered response generation for interview questions
- Audio processing and conversation logging
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core imports for easy access
from .core.interview_assistant import InterviewAssistant
from .config.settings import Settings

__all__ = [
    "InterviewAssistant",
    "Settings",
]
