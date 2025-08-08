"""Speech recognition implementation using Google Cloud Speech-to-Text."""

import logging
from typing import List, Any

from google.cloud import speech


class SpeechRecognizer:
    """Google Cloud Speech-to-Text recognizer."""
    
    def __init__(self, sample_rate: int = 16000):
        """Initialize speech recognizer.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Cloud Speech client
        self.client = speech.SpeechClient()
        
        self.logger.info("Speech recognizer initialized successfully")
    
    def recognize(self, audio_data: bytes) -> List[Any]:
        """Recognize speech from audio data.
        
        Args:
            audio_data: Raw audio data as bytes
            
        Returns:
            List of recognition results
        """
        try:
            # Configure recognition with speaker diarization
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=1,
                max_speaker_count=2
            )
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code="en-US",
                diarization_config=diarization_config,
                enable_automatic_punctuation=True,
                use_enhanced=True,
                model="latest_long",
                enable_word_time_offsets=True,
                enable_word_confidence=True,
                profanity_filter=False,
                speech_contexts=[
                    speech.SpeechContext(
                        phrases=[
                            "JavaScript", "Python", "algorithm", "data structure",
                            "API", "database", "framework", "object oriented",
                            "functional programming", "difference between"
                        ],
                        boost=10.0
                    )
                ]
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            response = self.client.recognize(config=config, audio=audio)
            
            return response.results
            
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return []
