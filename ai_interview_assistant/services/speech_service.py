"""Speech recognition service using Google Cloud Speech-to-Text."""

import logging
from typing import List, Tuple, Dict, Any

from google.cloud import speech

from ..core.speech.question_analyzer import QuestionAnalyzer


class SpeechService:
    """Service for speech recognition and analysis."""
    
    def __init__(self, sample_rate: int = 16000, user_speaker_label: int = 1):
        """Initialize speech service.
        
        Args:
            sample_rate: Audio sample rate in Hz
            user_speaker_label: Speaker label for the user to filter out
        """
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Cloud Speech client
        self.speech_client = speech.SpeechClient()
        
        # Initialize question analyzer
        self.question_analyzer = QuestionAnalyzer(user_speaker_label)
        
        self.logger.info("Speech service initialized successfully")
    
    def recognize_speech(self, audio_data: bytes) -> List[Any]:
        """Recognize speech from audio data.
        
        Args:
            audio_data: Raw audio data as bytes
            
        Returns:
            List of recognition results
        """
        try:
            # Configure recognition
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=2  # Assume interviewer + interviewee
            )
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code="en-US",
                diarization_config=diarization_config,
                enable_automatic_punctuation=True,
                use_enhanced=True,
                model="latest_long",
                # Additional settings for better conversational speech recognition
                enable_word_time_offsets=True,
                enable_word_confidence=True,
                profanity_filter=False,  # Don't filter technical terms
                speech_contexts=[
                    speech.SpeechContext(
                        phrases=[
                            "var let const", "JavaScript", "Python", "algorithm", 
                            "data structure", "API", "database", "framework",
                            "object oriented", "functional programming", "difference between"
                        ],
                        boost=10.0
                    )
                ]
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            return response.results
            
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return []
    
    def extract_transcript_and_speaker(self, result) -> Tuple[str, Dict[str, Any]]:
        """Extract transcript and speaker information from recognition result.
        
        Args:
            result: Google Cloud Speech recognition result
            
        Returns:
            Tuple of (transcript, speaker_info)
        """
        if not result.alternatives:
            return "", {}
        
        transcript = result.alternatives[0].transcript.strip()
        speaker_info = self.question_analyzer.extract_speaker_info(result)
        
        return transcript, speaker_info
    
    def is_interviewer_speech(self, speaker_info: Dict[str, Any]) -> bool:
        """Check if speech is from interviewer.
        
        Args:
            speaker_info: Speaker information dictionary
            
        Returns:
            True if speech is from interviewer
        """
        return self.question_analyzer.is_interviewer_speech(speaker_info)
    
    def is_incomplete_question(self, text: str) -> bool:
        """Check if question appears to be incomplete.
        
        Args:
            text: The transcript text to analyze
            
        Returns:
            True if question appears incomplete
        """
        return self.question_analyzer.is_incomplete_question(text)
