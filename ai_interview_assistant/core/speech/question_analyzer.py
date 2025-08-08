"""Question analysis functionality."""

import re
from typing import Dict, Any


class QuestionAnalyzer:
    """Analyzes speech transcripts to determine if questions are complete."""
    
    def __init__(self, user_speaker_label: int = 1):
        """Initialize question analyzer.
        
        Args:
            user_speaker_label: Speaker label for the user to filter out
        """
        self.user_speaker_label = user_speaker_label
    
    def is_incomplete_question(self, text: str) -> bool:
        """Detect if a question appears to be incomplete.
        
        Args:
            text: The transcribed text to analyze
            
        Returns:
            True if the question appears incomplete, False otherwise
        """
        text_lower = text.lower().strip()
        
        # Common incomplete question patterns
        incomplete_patterns = [
            # Questions ending with prepositions or conjunctions
            r'\b(between|and|or|of|for|with|in|on|about|what\'s|whats|how|why|when|where)\s*\??\s*$',
            # Questions with hanging "the"
            r'\bthe\s*\??\s*$',
            # Very short questions (less than 3 words)
            r'^\s*\w{1,2}(\s+\w{1,2}){0,1}\s*\??\s*$',
            # Questions ending with "um", "uh", "er"
            r'\b(um|uh|er|umm|uhh)\s*\??\s*$',
        ]
        
        for pattern in incomplete_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check for very short questions that might be incomplete
        word_count = len(text_lower.split())
        if word_count <= 3 and not text_lower.endswith('?'):
            return True
            
        return False
    
    def extract_speaker_info(self, result) -> Dict[str, Any]:
        """Extract speaker information from recognition result.
        
        Args:
            result: Google Cloud Speech recognition result
            
        Returns:
            Dictionary containing speaker information
        """
        speaker_info = {"speaker_tag": None, "confidence": 0}
        
        if hasattr(result, 'alternatives') and result.alternatives:
            alternative = result.alternatives[0]
            if hasattr(alternative, 'words') and alternative.words:
                # Get speaker tag from the first word (speaker diarization info)
                for word in alternative.words:
                    if hasattr(word, 'speaker_tag'):
                        speaker_info["speaker_tag"] = word.speaker_tag
                        break
                
                # Calculate average confidence
                confidences = [
                    word.confidence for word in alternative.words 
                    if hasattr(word, 'confidence')
                ]
                if confidences:
                    speaker_info["confidence"] = sum(confidences) / len(confidences)
        
        return speaker_info
    
    def is_interviewer_speech(self, speaker_info: Dict[str, Any]) -> bool:
        """Determine if the speech is from the interviewer (not the user).
        
        Args:
            speaker_info: Dictionary containing speaker information
            
        Returns:
            True if speech is from interviewer, False if from user
        """
        speaker_tag = speaker_info.get("speaker_tag")
        
        # If no speaker tag, assume it's worth processing
        if speaker_tag is None:
            return True
        
        # Filter out user's speech (configured speaker label)
        return speaker_tag != self.user_speaker_label
