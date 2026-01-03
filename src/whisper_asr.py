"""
Whisper ASR Module
Handles speech-to-text transcription using OpenAI's Whisper model.
"""

import whisper
import numpy as np
import torch
from pathlib import Path
import json
import ssl
import urllib.request


class WhisperASR:
    def __init__(self, config_path=None):
        """
        Initialize Whisper ASR.
        
        Args:
            config_path: Path to settings configuration file
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "settings.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        self.config = settings['whisper']
        self.sample_rate = settings['audio']['sample_rate']
        
        # Load Whisper model
        print(f"[INFO] Loading Whisper model ({self.config['model_size']})...")
        # SSL sertifika doğrulamasını devre dışı bırak
        ssl._create_default_https_context = ssl._create_unverified_context
        self.model = whisper.load_model(
            self.config['model_size'],
            device=self.config['device']
        )
        print("[OK] Whisper model loaded successfully!")
        
        # Set language
        self.language = self.config.get('language', 'tr')
    
    def transcribe(self, audio_data):
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio numpy array (float32, normalized to [-1, 1])
            
        Returns:
            str: Transcribed text
        """
        # Ensure audio is float32 and normalized
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Normalize if needed
        max_val = np.abs(audio_data).max()
        if max_val > 1.0:
            audio_data = audio_data / max_val
        
        # Transcribe with Whisper
        result = self.model.transcribe(
            audio_data,
            language=self.language,
            fp16=False,  # Use FP32 on CPU
            verbose=False,
            temperature=0.0,  # More deterministic
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            no_speech_threshold=0.6,
            condition_on_previous_text=False
        )
        
        text = result['text'].strip()
        return text
    
    def transcribe_file(self, audio_file):
        """
        Transcribe an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        result = self.model.transcribe(
            str(audio_file),
            language=self.language,
            fp16=False,
            verbose=False
        )
        
        return result['text'].strip()


if __name__ == "__main__":
    # Test the ASR
    print("[TEST] Testing Whisper ASR...\n")
    
    asr = WhisperASR()
    
    # Test with a simple message
    print("Whisper ASR is ready!")
    print(f"Model: {asr.config['model_size']}")
    print(f"Language: {asr.language}")
    print(f"Device: {asr.config['device']}")
