"""Voice Activity Detection for audio processing."""

import logging
import struct
from typing import Tuple

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class VoiceActivityDetector:
    """Detects voice activity in audio chunks."""
    
    def __init__(self, min_audio_level: float = 0.005):
        """Initialize voice activity detector.
        
        Args:
            min_audio_level: Minimum audio level to detect as speech (0.0-1.0)
        """
        self.min_audio_level = min_audio_level
        self.logger = logging.getLogger(__name__)
        self._debug_counter = 0
    
    def has_voice_activity(self, audio_chunk: bytes) -> bool:
        """Enhanced voice activity detection based on audio level and frequency.
        
        Args:
            audio_chunk: Raw audio data as bytes
            
        Returns:
            True if voice activity is detected, False otherwise
        """
        try:
            if HAS_NUMPY:
                return self._detect_with_numpy(audio_chunk)
            else:
                return self._detect_simple(audio_chunk)
                
        except Exception as e:
            self.logger.error(f"Error in voice activity detection: {e}")
            return False
    
    def _detect_with_numpy(self, audio_chunk: bytes) -> bool:
        """Voice activity detection using numpy for better accuracy."""
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
        self._debug_counter += 1
        if self._debug_counter % 100 == 0:  # Log every 100 chunks
            self.logger.debug(
                f"Audio analysis: RMS={normalized_rms:.4f}, ZCR={zcr:.3f}, "
                f"Energy={has_energy}, Pattern={has_speech_pattern}"
            )
        
        return has_energy and has_speech_pattern
    
    def _detect_simple(self, audio_chunk: bytes) -> bool:
        """Simple fallback voice activity detection without numpy."""
        if len(audio_chunk) >= 2:
            samples = struct.unpack(f'<{len(audio_chunk)//2}h', audio_chunk)
            avg_energy = sum(abs(s) for s in samples) / len(samples)
            return avg_energy > (self.min_audio_level * 32767)
        return False
