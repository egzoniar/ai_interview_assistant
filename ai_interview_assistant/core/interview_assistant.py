"""Main Interview Assistant class."""

import os
import logging
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv

from ..config.settings import Settings
from ..services.speech_service import SpeechService
from ..services.ai_service import AIService
from ..services.conversation_service import ConversationService
from ..core.audio.audio_processor import AudioProcessor
from ..utils.environment import EnvironmentValidator


class InterviewAssistant:
    """Main AI Interview Assistant class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Interview Assistant.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load environment variables
        load_dotenv(config_path or Settings.ENV_FILE)
        
        # Validate environment
        self.env_validator = EnvironmentValidator()
        
        # Initialize logging
        self.logger = Settings.init_logging()
        
        # Load configuration from environment
        self._load_config()
        
        # Initialize services
        self._init_services()
        
        # Control flags
        self.is_running = False
        self.conversation_log: List[Dict[str, Any]] = []
    
    def _load_config(self):
        """Load configuration from environment variables."""
        self.sample_rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 4096))
        self.channels = int(os.getenv('CHANNELS', 1))
        self.min_audio_level = float(os.getenv('MIN_AUDIO_LEVEL', 0.005))
        self.user_speaker_label = int(os.getenv('USER_SPEAKER_LABEL', 1))
    
    def _init_services(self):
        """Initialize all services."""
        try:
            # Validate required environment variables
            if not self.env_validator.validate_environment():
                raise ValueError("Required environment variables are missing")
            
            # Initialize services
            self.speech_service = SpeechService(
                sample_rate=self.sample_rate,
                user_speaker_label=self.user_speaker_label
            )
            
            self.ai_service = AIService()
            
            self.conversation_service = ConversationService()
            
            # Initialize audio processor
            self.audio_processor = AudioProcessor(
                sample_rate=self.sample_rate,
                chunk_size=self.chunk_size,
                channels=self.channels,
                min_audio_level=self.min_audio_level
            )
            
            # Set audio callback
            self.audio_processor.set_audio_callback(self._process_audio_chunk)
            
            self.logger.info("Successfully initialized all services")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize services: {e}")
            raise
    
    def start_interview_session(self):
        """Start the interview assistant session."""
        if self.is_running:
            self.logger.warning("Interview session is already running")
            return
        
        try:
            self.is_running = True
            
            # Start audio processing
            self.audio_processor.start()
            
            self.logger.info("Interview assistant session started successfully")
            self._print_startup_message()
            
        except Exception as e:
            self.logger.error(f"Failed to start interview session: {e}")
            self.stop_interview_session()
            raise
    
    def stop_interview_session(self):
        """Stop the interview assistant session."""
        self.is_running = False
        
        # Stop audio processing
        if hasattr(self, 'audio_processor'):
            self.audio_processor.stop()
        
        self.logger.info("Interview assistant session stopped")
        
        # Save conversation log
        if self.conversation_log:
            self.conversation_service.save_conversation_log(self.conversation_log)
    
    def _process_audio_chunk(self, audio_data: bytes):
        """Process audio chunk through speech recognition.
        
        Args:
            audio_data: Raw audio data to process
        """
        try:
            # Process through speech service
            results = self.speech_service.recognize_speech(audio_data)
            
            for result in results:
                self._handle_recognition_result(result)
                
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    def _handle_recognition_result(self, result):
        """Handle speech recognition result.
        
        Args:
            result: Speech recognition result
        """
        try:
            transcript, speaker_info = self.speech_service.extract_transcript_and_speaker(result)
            
            if not transcript:
                return
            
            # Check if this is interviewer speech
            if not self.speech_service.is_interviewer_speech(speaker_info):
                return
            
            # Check if question is incomplete
            if self.speech_service.is_incomplete_question(transcript):
                self.logger.info(f"Incomplete question detected: '{transcript}' - waiting for continuation")
                self._print_partial_question(transcript)
                return
            
            # Process complete question
            self._process_interviewer_question(transcript, speaker_info)
            
        except Exception as e:
            self.logger.error(f"Error handling recognition result: {e}")
    
    def _process_interviewer_question(self, transcript: str, speaker_info: Dict[str, Any]):
        """Process a complete interviewer question.
        
        Args:
            transcript: The question transcript
            speaker_info: Speaker information from recognition
        """
        self.logger.info(f"Interviewer: {transcript}")
        self._print_interviewer_question(transcript)
        
        # Show processing message
        self._print_processing_message()
        
        # Generate AI response
        ai_response = self.ai_service.generate_response(transcript)
        
        if ai_response:
            self._print_ai_response(ai_response)
            
            # Log conversation
            self.conversation_log.extend([
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "interviewer_question",
                    "text": transcript,
                    "speaker_info": speaker_info
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "ai_response", 
                    "text": ai_response
                }
            ])
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the current conversation.
        
        Returns:
            Dictionary containing conversation statistics
        """
        questions_count = len([
            log for log in self.conversation_log 
            if log["type"] == "interviewer_question"
        ])
        responses_count = len([
            log for log in self.conversation_log 
            if log["type"] == "ai_response"
        ])
        
        return {
            "total_questions": questions_count,
            "total_responses": responses_count,
            "session_duration": "active" if self.is_running else "completed",
            "log_entries": len(self.conversation_log)
        }
    
    def _print_startup_message(self):
        """Print startup message."""
        print("\\n\\033[95m🎤 Interview Assistant is now listening...\\033[0m")
        print("\\033[97m💡 Speak naturally - I'll detect the interviewer's questions and provide responses\\033[0m")
        print("\\033[97m⏹️  Press Ctrl+C to stop the session\\n\\033[0m")
    
    def _print_partial_question(self, transcript: str):
        """Print partial question message."""
        print(f"\\n\\033[96m⏳ Partial question detected: {transcript}\\033[0m")
        print("\\033[96m   Waiting for completion...\\033[0m")
    
    def _print_interviewer_question(self, transcript: str):
        """Print interviewer question."""
        print(f"\\n\\033[94m🎙️  Interviewer: {transcript}\\033[0m")
    
    def _print_processing_message(self):
        """Print processing message."""
        print("\\033[93m🤖 AI is processing the response...\\033[0m")
    
    def _print_ai_response(self, response: str):
        """Print AI response."""
        print(f"\\033[92m🤖 AI Assistant: {response}\\033[0m\\n")
