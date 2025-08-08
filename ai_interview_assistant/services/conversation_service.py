"""Conversation service for logging and management."""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any

from ..config.settings import Settings


class ConversationService:
    """Service for managing conversation logs."""
    
    def __init__(self):
        """Initialize conversation service."""
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        Settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Conversation service initialized successfully")
    
    def save_conversation_log(self, conversation_log: List[Dict[str, Any]]) -> str:
        """Save conversation log to a timestamped JSON file.
        
        Args:
            conversation_log: List of conversation entries
            
        Returns:
            Filename of the saved log
        """
        if not conversation_log:
            self.logger.info("No conversation data to save")
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interview_log_{timestamp}.json"
            filepath = Settings.DATA_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_log, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Conversation log saved to {filename}")
            print(f"\\033[95m💾 Conversation log saved to {filename}\\033[0m")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving conversation log: {e}")
            return ""
    
    def load_conversation_log(self, filename: str) -> List[Dict[str, Any]]:
        """Load conversation log from file.
        
        Args:
            filename: Name of the log file to load
            
        Returns:
            List of conversation entries
        """
        try:
            filepath = Settings.DATA_DIR / filename
            
            if not filepath.exists():
                self.logger.error(f"Conversation log file not found: {filename}")
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation_log = json.load(f)
            
            self.logger.info(f"Loaded conversation log from {filename}")
            return conversation_log
            
        except Exception as e:
            self.logger.error(f"Error loading conversation log: {e}")
            return []
    
    def list_conversation_logs(self) -> List[str]:
        """List all available conversation log files.
        
        Returns:
            List of log filenames
        """
        try:
            log_files = [
                f.name for f in Settings.DATA_DIR.glob("interview_log_*.json")
            ]
            log_files.sort(reverse=True)  # Most recent first
            return log_files
            
        except Exception as e:
            self.logger.error(f"Error listing conversation logs: {e}")
            return []
