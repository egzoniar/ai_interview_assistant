#!/usr/bin/env python3
"""
Debug script for testing audio processing timing and speech detection.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from assistant_agent import InterviewAssistant


class DebugInterviewAssistant(InterviewAssistant):
    """Debug version with enhanced logging."""
    
    def __init__(self):
        # Set debug logging
        logging.basicConfig(level=logging.DEBUG)
        super().__init__()
    
    def _audio_capture_loop(self):
        """Enhanced debug version of audio capture loop."""
        self.logger.info("🔍 DEBUG: Starting audio capture loop")
        
        while self.is_running:
            try:
                # Collect audio chunks for processing
                audio_chunks = []
                start_time = time.time()
                last_speech_time = time.time()
                has_speech = False
                silence_start_time = None
                chunk_count = 0
                speech_chunk_count = 0
                
                self.logger.info("🎤 DEBUG: Starting new audio collection session")
                
                # Continuously collect and analyze audio
                while self.is_running:
                    current_time = time.time()
                    
                    # Check for maximum duration timeout
                    if current_time - start_time > self.max_speech_duration:
                        if has_speech:
                            self.logger.info(f"⏰ DEBUG: Max duration reached ({self.max_speech_duration}s) with {speech_chunk_count} speech chunks - processing")
                            break
                        else:
                            self.logger.info(f"⏰ DEBUG: Max duration reached but no speech detected in {chunk_count} chunks - resetting")
                            audio_chunks = []
                            start_time = current_time
                            chunk_count = 0
                            continue
                    
                    # Get audio chunk if available
                    if not self.audio_queue.empty():
                        chunk = self.audio_queue.get()
                        audio_chunks.append(chunk)
                        chunk_count += 1
                        
                        # Check if this chunk has speech
                        if self._has_audio_activity(chunk):
                            last_speech_time = current_time
                            has_speech = True
                            speech_chunk_count += 1
                            if silence_start_time is not None:
                                silence_duration = current_time - silence_start_time
                                self.logger.debug(f"🔊 DEBUG: Speech resumed after {silence_duration:.2f}s silence")
                            silence_start_time = None  # Reset silence timer
                        else:
                            # This chunk is silence
                            if silence_start_time is None and has_speech:
                                silence_start_time = current_time  # Start tracking silence
                                self.logger.debug(f"🔇 DEBUG: Silence started after {speech_chunk_count} speech chunks")
                    
                    # Check if we should process accumulated speech
                    if has_speech:
                        speech_duration = current_time - start_time
                        
                        if silence_start_time is not None:
                            silence_duration = current_time - silence_start_time
                            
                            # Log progress every second
                            if int(current_time) != int(current_time - 0.1):
                                self.logger.debug(f"📊 DEBUG: Speech={speech_duration:.1f}s, Silence={silence_duration:.1f}s, Chunks={chunk_count}, Speech chunks={speech_chunk_count}")
                            
                            # Process if we have enough speech and sufficient final silence
                            if (speech_duration >= self.min_speech_duration and 
                                silence_duration >= self.final_silence_threshold):
                                self.logger.info(f"✅ DEBUG: Processing - {speech_duration:.1f}s speech, {silence_duration:.1f}s silence, {speech_chunk_count} speech chunks")
                                break
                    
                    time.sleep(0.05)  # Small delay to prevent excessive CPU usage
                
                # Process the collected audio if we have speech
                if audio_chunks and has_speech:
                    self.logger.info(f"🎯 DEBUG: Processing {len(audio_chunks)} total chunks ({speech_chunk_count} with speech)")
                    audio_data = b''.join(audio_chunks)
                    self._process_audio_chunk(audio_data)
                else:
                    self.logger.info(f"❌ DEBUG: Skipping processing - chunks={len(audio_chunks)}, has_speech={has_speech}")
                    
            except Exception as e:
                self.logger.error(f"❌ DEBUG: Error in audio capture loop: {e}")
                time.sleep(1)


def main():
    """Run the debug version."""
    print("🐛 DEBUG: AI Interview Assistant - Audio Processing Debug Mode")
    print("=" * 60)
    print("This version includes detailed logging to help diagnose timing issues.")
    print("Watch for DEBUG messages showing speech detection and timing.\n")
    
    load_dotenv()
    
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set")  
        return
    
    try:
        assistant = DebugInterviewAssistant()
        assistant.start_interview_session()
        
        # Keep running
        while assistant.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ DEBUG: Stopping debug session...")
        if 'assistant' in locals():
            assistant.stop_interview_session()
    except Exception as e:
        print(f"❌ DEBUG: Error: {e}")
        if 'assistant' in locals():
            assistant.stop_interview_session()


if __name__ == "__main__":
    main() 