"""
Voice Activity Detection Module
Detects speech in audio streams using Silero VAD.
"""

import torch
import numpy as np
from pathlib import Path
import json


class VoiceActivityDetector:
    def __init__(self, config_path=None):
        """
        Initialize Voice Activity Detector.
        
        Args:
            config_path: Path to settings configuration file
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "settings.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        self.config = settings['vad']
        self.sample_rate = settings['audio']['sample_rate']
        
        # Use simple energy-based VAD (more reliable)
        print("[INFO] Loading VAD (energy-based)...")
        self.model = None
        print("[OK] VAD ready (energy-based detection)!")
        
        self.threshold = self.config.get('threshold', 0.5)
        self.min_speech_duration_ms = self.config.get('min_speech_duration_ms', 250)
        self.min_silence_duration_ms = self.config.get('min_silence_duration_ms', 500)
    
    def is_speech(self, audio_chunk):
        """
        Detect if audio chunk contains speech.
        
        Args:
            audio_chunk: Audio numpy array (float32)
            
        Returns:
            bool: True if speech detected
        """
        # Use energy-based detection
        return self._energy_based_detection(audio_chunk)
    
    def get_speech_timestamps_from_audio(self, audio_array):
        """
        Get timestamps of speech segments in audio.
        
        Args:
            audio_array: Full audio numpy array
            
        Returns:
            list: List of dict with 'start' and 'end' keys (in samples)
        """
        if self.model is None:
            return [{'start': 0, 'end': len(audio_array)}]
        
        # Ensure correct format
        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)
        
        # Normalize
        max_val = np.abs(audio_array).max()
        if max_val > 0:
            audio_array = audio_array / max_val
        
        # Convert to tensor
        audio_tensor = torch.from_numpy(audio_array)
        
        # Get speech timestamps
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor,
            self.model,
            sampling_rate=self.sample_rate,
            threshold=self.threshold,
            min_speech_duration_ms=self.min_speech_duration_ms,
            min_silence_duration_ms=self.min_silence_duration_ms
        )
        
        return speech_timestamps
    
    def _energy_based_detection(self, audio_chunk):
        """Simple energy-based speech detection fallback."""
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk**2))
        
        # Adaptive threshold based on recent audio
        energy_threshold = 0.02  # Increased sensitivity
        
        return rms > energy_threshold


if __name__ == "__main__":
    # Test the VAD
    print("[TEST] Testing Voice Activity Detector...\n")
    
    vad = VoiceActivityDetector()
    
    print("VAD is ready!")
    print(f"Threshold: {vad.threshold}")
    print(f"Sample rate: {vad.sample_rate}")
