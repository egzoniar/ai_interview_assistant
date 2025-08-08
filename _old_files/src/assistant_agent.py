import asyncio
import json
import logging
import os
import re
import threading
import time
from datetime import datetime
from queue import Queue
from typing import Optional, Dict, List

import pyaudio
from google.cloud import speech
from openai import OpenAI
from dotenv import load_dotenv


class InterviewAssistant:
    """
    AI Interview Assistant that captures audio, performs speech recognition with speaker diarization,
    filters interviewer questions, and provides AI-generated responses using OpenAI.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Load environment variables
        load_dotenv(config_path)
        
        # Initialize logging
        self._setup_logging()
        
        # Audio configuration
        self.sample_rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 4096))
        self.channels = int(os.getenv('CHANNELS', 1))
        
        # Speech detection configuration - optimized for responsiveness
        self.min_speech_duration = float(os.getenv('MIN_SPEECH_DURATION', 1.5))  # Minimum speech before processing
        self.max_speech_duration = float(os.getenv('MAX_SPEECH_DURATION', 30.0))  # Reasonable max duration
        self.final_silence_threshold = float(os.getenv('FINAL_SILENCE_THRESHOLD', 2.5))  # Reduced silence for faster response
        
        # Voice activity detection - more sensitive
        self.min_audio_level = float(os.getenv('MIN_AUDIO_LEVEL', 0.005))  # More sensitive detection
        
        # Speaker configuration
        self.user_speaker_label = int(os.getenv('USER_SPEAKER_LABEL', 1))
        
        # Initialize clients
        self._init_clients()
        
        # Audio stream components
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_queue = Queue()
        
        # Control flags
        self.is_running = False
        self.conversation_log = []
        
        # Threading
        self.audio_thread = None
        self.processing_thread = None
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('interview_assistant.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_clients(self):
        """Initialize Google Cloud Speech and OpenAI clients."""
        try:
            # Initialize Google Cloud Speech client
            if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
            self.speech_client = speech.SpeechClient()
            
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.openai_client = OpenAI(api_key=openai_api_key)
            
            self.logger.info("Successfully initialized Google Cloud Speech and OpenAI clients")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {e}")
            raise
    
    def start_interview_session(self):
        """Start the interview assistant session."""
        if self.is_running:
            self.logger.warning("Interview session is already running")
            return
        
        try:
            self.is_running = True
            self._start_audio_stream()
            
            # Start audio capture thread
            self.audio_thread = threading.Thread(target=self._audio_capture_loop)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            # Start speech processing thread
            self.processing_thread = threading.Thread(target=self._speech_processing_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.logger.info("Interview assistant session started successfully")
            print("\n\033[95m🎤 Interview Assistant is now listening...\033[0m")  # Magenta for system status
            print("\033[97m💡 Speak naturally - I'll detect the interviewer's questions and provide responses\033[0m")  # White for instructions
            print("\033[97m⏹️  Press Ctrl+C to stop the session\n\033[0m")
            
        except Exception as e:
            self.logger.error(f"Failed to start interview session: {e}")
            self.stop_interview_session()
            raise
    
    def stop_interview_session(self):
        """Stop the interview assistant session."""
        self.is_running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        self.logger.info("Interview assistant session stopped")
        
        # Save conversation log
        self._save_conversation_log()
    
    def _start_audio_stream(self):
        """Initialize and start the audio stream."""
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            
        except Exception as e:
            self.logger.error(f"Failed to start audio stream: {e}")
            raise
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream."""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _has_audio_activity(self, audio_chunk: bytes) -> bool:
        """Enhanced voice activity detection based on audio level and frequency."""
        try:
            import numpy as np
            # Convert bytes to numpy array
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            
            if len(audio_data) == 0:
                return False
            
            # Calculate RMS (Root Mean Square) energy
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            normalized_rms = rms / 32767.0
            
            # Calculate zero crossing rate (indicates speech vs noise)
            zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
            zcr = zero_crossings / len(audio_data)
            
            # Speech typically has energy above threshold AND reasonable zero crossing rate
            has_energy = normalized_rms > self.min_audio_level
            has_speech_pattern = 0.01 < zcr < 0.3  # Speech typically in this range
            
            # Log detailed info occasionally for debugging
            if hasattr(self, '_debug_counter'):
                self._debug_counter += 1
            else:
                self._debug_counter = 0
                
            if self._debug_counter % 100 == 0:  # Log every 100 chunks
                self.logger.debug(f"Audio analysis: RMS={normalized_rms:.4f}, ZCR={zcr:.3f}, Energy={has_energy}, Pattern={has_speech_pattern}")
            
            return has_energy and has_speech_pattern
            
        except ImportError:
            # Simpler fallback without numpy
            import struct
            # Simple energy calculation without numpy
            if len(audio_chunk) >= 2:
                samples = struct.unpack(f'<{len(audio_chunk)//2}h', audio_chunk)
                avg_energy = sum(abs(s) for s in samples) / len(samples)
                return avg_energy > (self.min_audio_level * 32767)
            return False
        except Exception as e:
            self.logger.error(f"Error in voice activity detection: {e}")
            return False  # Changed to False for safer behavior
    
    def _audio_capture_loop(self):
        """Continuous audio capture loop with intelligent speech detection."""
        while self.is_running:
            try:
                # Collect audio chunks for processing
                audio_chunks = []
                start_time = time.time()
                last_speech_time = time.time()
                has_speech = False
                silence_start_time = None
                
                # Continuously collect and analyze audio
                while self.is_running:
                    current_time = time.time()
                    
                    # Check for maximum duration timeout
                    if current_time - start_time > self.max_speech_duration:
                        if has_speech:
                            self.logger.info(f"Max speech duration ({self.max_speech_duration}s) reached - processing speech")
                            break
                        else:
                            # No speech detected in max duration, reset and continue
                            audio_chunks = []
                            start_time = current_time
                            continue
                    
                    # Get audio chunk if available
                    if not self.audio_queue.empty():
                        chunk = self.audio_queue.get()
                        audio_chunks.append(chunk)
                        
                        # Check if this chunk has speech
                        if self._has_audio_activity(chunk):
                            last_speech_time = current_time
                            has_speech = True
                            silence_start_time = None  # Reset silence timer
                        else:
                            # This chunk is silence
                            if silence_start_time is None and has_speech:
                                silence_start_time = current_time  # Start tracking silence
                    
                    # Check if we should process accumulated speech
                    if has_speech:
                        speech_duration = current_time - start_time
                        
                        if silence_start_time is not None:
                            silence_duration = current_time - silence_start_time
                            
                            # Process if we have enough speech and sufficient final silence
                            if (speech_duration >= self.min_speech_duration and 
                                silence_duration >= self.final_silence_threshold):
                                self.logger.info(f"Speech complete: {speech_duration:.1f}s speech, {silence_duration:.1f}s silence - processing")
                                break
                    
                    time.sleep(0.05)  # Small delay to prevent excessive CPU usage
                
                # Process the collected audio if we have speech
                if audio_chunks and has_speech:
                    audio_data = b''.join(audio_chunks)
                    self._process_audio_chunk(audio_data)
                    
            except Exception as e:
                self.logger.error(f"Error in audio capture loop: {e}")
                time.sleep(1)
    
    def _process_audio_chunk(self, audio_data: bytes):
        """Process audio chunk with Google Cloud Speech-to-Text."""
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
            
            # Process results
            self._process_recognition_results(response)
            
        except Exception as e:
            self.logger.error(f"Error processing audio chunk: {e}")
    
    def _process_recognition_results(self, response):
        """Process speech recognition results and handle speaker diarization."""
        try:
            for result in response.results:
                if not result.alternatives:
                    continue
                
                transcript = result.alternatives[0].transcript.strip()
                if not transcript:
                    continue
                
                # Process speaker diarization
                speaker_info = self._extract_speaker_info(result)
                
                # Filter out user's speech - only process interviewer's questions
                if self._is_interviewer_speech(speaker_info):
                    # Check if this looks like an incomplete question
                    if self._is_incomplete_question(transcript):
                        self.logger.info(f"Incomplete question detected: '{transcript}' - waiting for continuation")
                        print(f"\n\033[96m⏳ Partial question detected: {transcript}\033[0m")  # Cyan for partial
                        print("\033[96m   Waiting for completion...\033[0m")
                        return  # Don't process incomplete questions
                    
                    self.logger.info(f"Interviewer: {transcript}")
                    print(f"\n\033[94m🎙️  Interviewer: {transcript}\033[0m")  # Blue for interviewer
                    
                    # Show processing message
                    print("\033[93m🤖 AI is processing the response...\033[0m")  # Yellow for processing
                    
                    # Generate and display AI response
                    ai_response = self._generate_ai_response(transcript)
                    if ai_response:
                        print(f"\033[92m🤖 AI Assistant: {ai_response}\033[0m\n")  # Green for AI response
                        
                        # Log conversation
                        self.conversation_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "type": "interviewer_question",
                            "text": transcript,
                            "speaker_info": speaker_info
                        })
                        self.conversation_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "type": "ai_response",
                            "text": ai_response
                        })
                
        except Exception as e:
            self.logger.error(f"Error processing recognition results: {e}")
    
    def _is_incomplete_question(self, text: str) -> bool:
        """Detect if a question appears to be incomplete."""
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
    
    def _extract_speaker_info(self, result) -> Dict:
        """Extract speaker information from recognition result."""
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
                confidences = [word.confidence for word in alternative.words if hasattr(word, 'confidence')]
                if confidences:
                    speaker_info["confidence"] = sum(confidences) / len(confidences)
        
        return speaker_info
    
    def _is_interviewer_speech(self, speaker_info: Dict) -> bool:
        """Determine if the speech is from the interviewer (not the user)."""
        speaker_tag = speaker_info.get("speaker_tag")
        
        # If no speaker tag, assume it's worth processing
        if speaker_tag is None:
            return True
        
        # Filter out user's speech (configured speaker label)
        return speaker_tag != self.user_speaker_label
    
    def _generate_ai_response(self, question: str) -> Optional[str]:
        """Generate AI response using OpenAI for the interviewer's question."""
        try:
            # Create a focused prompt for interview questions
            system_prompt = """You are an AI assistant helping someone during a technical interview. 
            The user will provide you with interviewer questions, and you should give concise, 
            professional answers that demonstrate technical knowledge. Keep responses brief but 
            comprehensive, suitable for a live interview setting. Focus on clarity and accuracy."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Interview question: {question}"}
                ],
                max_tokens=300,  # Keep responses concise for real-time use
                temperature=0.7
            )
            
            if response.choices:
                ai_answer = response.choices[0].message.content.strip()
                self.logger.info(f"Generated AI response for question: {question[:50]}...")
                return ai_answer
            
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            return "I'm having trouble processing that question. Could you please repeat it?"
        
        return None
    
    def _speech_processing_loop(self):
        """Main processing loop for handling speech recognition."""
        while self.is_running:
            try:
                time.sleep(0.5)  # Prevent excessive CPU usage
            except Exception as e:
                self.logger.error(f"Error in speech processing loop: {e}")
    
    def _save_conversation_log(self):
        """Save the conversation log to a file."""
        if not self.conversation_log:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interview_log_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_log, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Conversation log saved to {filename}")
            print(f"\033[95m💾 Conversation log saved to {filename}\033[0m")  # Magenta for system messages
            
        except Exception as e:
            self.logger.error(f"Error saving conversation log: {e}")
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation."""
        questions_count = len([log for log in self.conversation_log if log["type"] == "interviewer_question"])
        responses_count = len([log for log in self.conversation_log if log["type"] == "ai_response"])
        
        return {
            "total_questions": questions_count,
            "total_responses": responses_count,
            "session_duration": "active" if self.is_running else "completed",
            "log_entries": len(self.conversation_log)
        }


def main():
    """Main function to run the interview assistant."""
    assistant = InterviewAssistant()
    
    try:
        assistant.start_interview_session()
        
        # Keep the main thread alive
        while assistant.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n\033[93m⏹️  Stopping interview assistant...\033[0m")  # Yellow for stopping
        assistant.stop_interview_session()
        
        # Display session summary
        summary = assistant.get_conversation_summary()
        print(f"\n\033[95m📊 Session Summary:\033[0m")  # Magenta for headers
        print(f"\033[97m   Questions processed: {summary['total_questions']}\033[0m")
        print(f"\033[97m   AI responses generated: {summary['total_responses']}\033[0m")
        print(f"\033[97m   Total log entries: {summary['log_entries']}\033[0m")
        
    except Exception as e:
        print(f"\033[91m❌ Error: {e}\033[0m")  # Red for errors
        assistant.stop_interview_session()


if __name__ == "__main__":
    main()
