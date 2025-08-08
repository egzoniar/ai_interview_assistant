"""Audio processing functionality."""

import logging
import threading
import time
from queue import Queue
from typing import Callable, Optional

import pyaudio

from .voice_activity_detector import VoiceActivityDetector


class AudioProcessor:
    """Handles audio capture and processing."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_size: int = 4096,
        channels: int = 1,
        min_audio_level: float = 0.005
    ):
        """Initialize audio processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_size: Size of audio chunks to process
            channels: Number of audio channels
            min_audio_level: Minimum audio level for voice detection
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        
        self.logger = logging.getLogger(__name__)
        self.voice_detector = VoiceActivityDetector(min_audio_level)
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_queue = Queue()
        
        # Control flags
        self.is_running = False
        self.audio_thread = None
        
        # Callback for processed audio
        self.audio_callback: Optional[Callable[[bytes], None]] = None
    
    def set_audio_callback(self, callback: Callable[[bytes], None]):
        """Set callback function for processed audio chunks."""
        self.audio_callback = callback
    
    def start(self):
        """Start audio capture."""
        if self.is_running:
            self.logger.warning("Audio processor is already running")
            return
        
        try:
            self.is_running = True
            self._start_audio_stream()
            
            # Start audio capture thread
            self.audio_thread = threading.Thread(target=self._audio_capture_loop)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            
            self.logger.info("Audio processor started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start audio processor: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop audio capture."""
        self.is_running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        self.logger.info("Audio processor stopped")
    
    def _start_audio_stream(self):
        """Initialize and start the audio stream."""
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._stream_callback
            )
            self.stream.start_stream()
            
        except Exception as e:
            self.logger.error(f"Failed to start audio stream: {e}")
            raise
    
    def _stream_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream."""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _audio_capture_loop(self):
        """Main audio capture and processing loop."""
        while self.is_running:
            try:
                # Collect audio chunks for processing
                audio_chunks = []
                start_time = time.time()
                last_speech_time = time.time()
                has_speech = False
                silence_start_time = None
                
                min_speech_duration = 1.5
                max_speech_duration = 30.0
                final_silence_threshold = 2.5
                
                # Continuously collect and analyze audio
                while self.is_running:
                    current_time = time.time()
                    
                    # Check for maximum duration timeout
                    if current_time - start_time > max_speech_duration:
                        if has_speech:
                            self.logger.info(
                                f"Max speech duration ({max_speech_duration}s) reached - processing speech"
                            )
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
                        if self.voice_detector.has_voice_activity(chunk):
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
                            if (speech_duration >= min_speech_duration and 
                                silence_duration >= final_silence_threshold):
                                self.logger.info(
                                    f"Speech complete: {speech_duration:.1f}s speech, "
                                    f"{silence_duration:.1f}s silence - processing"
                                )
                                break
                    
                    time.sleep(0.05)  # Small delay to prevent excessive CPU usage
                
                # Process the collected audio if we have speech
                if audio_chunks and has_speech and self.audio_callback:
                    audio_data = b''.join(audio_chunks)
                    self.audio_callback(audio_data)
                    
            except Exception as e:
                self.logger.error(f"Error in audio capture loop: {e}")
                time.sleep(1)
