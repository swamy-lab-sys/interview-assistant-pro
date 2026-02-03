"""
STT Engine 2.0: Faster-Whisper + Noisereduce Robustness
Optimized for high-noise YouTube/Video environments.
"""

import numpy as np
import warnings
import time
import os
import torch
from faster_whisper import WhisperModel

warnings.filterwarnings("ignore", category=UserWarning)

import config

# Global model
model = None
model_name = None

# Default to config setting
DEFAULT_MODEL = config.STT_MODEL

def load_model(model_size=None):
    """Load Faster-Whisper model."""
    global model, model_name
    
    if model_size is None:
        model_size = DEFAULT_MODEL
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Use int8 on CPU or float16 on GPU for speed
    compute_type = "float16" if device == "cuda" else "int8"
    
    if model is None or model_name != model_size:
        print(f"  [STT] Loading Faster-Whisper '{model_size}' on {device}/{compute_type}...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        model_name = model_size
        
    return model

def transcribe(audio_array):
    """
    Transcribe with high robustness.
    Returns (text, confidence)
    """
    global model
    if model is None:
        load_model()
        
    # faster-whisper expects float32
    if audio_array.dtype != np.float32:
        audio_array = audio_array.astype(np.float32)

    # Transcription parameters - CPU OPTIMIZED
    segments, info = model.transcribe(
        audio_array,
        beam_size=3,  # Speed over deep search
        best_of=1,
        temperature=0.0,
        word_timestamps=False,
        # Performance/Robustness
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=300,
            threshold=0.4
        ),
        # Strong multi-topic bias
        initial_prompt="Python, Django, SQL, JavaScript, React interview. Key terms: tuple, decorator, generator, orm, middleware, join, select, promise, closure, prime number, fizzbuzz, recursion, inheritance."
    )
    
    segments = list(segments)
    text = " ".join([seg.text for seg in segments]).strip()
    
    # Calculate confidence from avg logprob
    if not segments:
        return "", 0.0
        
    avg_logprob = sum(seg.avg_logprob for seg in segments) / len(segments)
    # Map logprob to 0-1 (more generous mapping for YouTube)
    confidence = min(1.0, np.exp(avg_logprob + 1.5))
    
    return text, confidence

def get_model_info():
    return {
        'name': model_name,
        'backend': 'faster-whisper',
        'device': 'gpu' if torch.cuda.is_available() else 'cpu'
    }
