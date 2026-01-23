"""
Professional Audio Capture Engine - CONCURRENT EDITION
Using sounddevice for maximum compatibility with PipeWire/PulseAudio.
Maintains a persistent stream for zero-latency capture.
"""

import numpy as np
import sounddevice as sd
import queue
import time
from collections import deque
import os

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 480  # 30ms

class SharedAudioStream:
    """
    Singleton-style stream that stays open for the entire session.
    Prevents latency/glitches from constant start/stop.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedAudioStream, cls).__new__(cls)
            cls._instance.is_active = False
            cls._instance.audio_queue = queue.Queue(maxsize=10000)
            cls._instance.stream = None
            # Rely on PortAudio/PulseAudio default (respects PULSE_SOURCE)
            cls._instance.device = None 
        return cls._instance

    def _callback(self, indata, frames, time_info, status):
        """Streaming callback."""
        if self.is_active:
            try:
                self.audio_queue.put_nowait(indata.copy().flatten())
            except queue.Full:
                pass

    def start(self):
        if self.stream is not None:
            return
        
        try:
            self.is_active = True
            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                device=self.device, # None = System Default
                callback=self._callback,
                blocksize=CHUNK_SIZE
            )
            self.stream.start()
        except Exception as e:
            print(f"[CRITICAL] Could not start audio stream: {e}")
            self.stream = None

    def stop(self):
        self.is_active = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def get_chunk(self, timeout=0.1):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def flush(self):
        """Clear all pending audio."""
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except: break

# Global stream instance
_stream = SharedAudioStream()

class SmartVAD:
    """
    Ultra-sensitive adaptive Speech Detection.
    """
    def __init__(self):
        self.noise_floor = 0.0001
        self.speech_threshold = 0.0005
        self.history = deque(maxlen=100)
        
    def update(self, chunk):
        rms = np.sqrt(np.mean(chunk**2))
        self.history.append(rms)
        if len(self.history) >= 10:
            self.noise_floor = max(np.percentile(list(self.history), 10), 0.0001)
            self.speech_threshold = max(self.noise_floor * 2.5, 0.001)
            
    def is_speech(self, chunk):
        chunk_boosted = chunk * 100.0
        rms = np.sqrt(np.mean(chunk_boosted**2))
        self.update(chunk_boosted)
        return rms > 0.02

def capture_question(max_duration=6.0, silence_duration=1.2, verbose=False):
    """
    Capture a single question segment. 
    Uses the persistent global stream.
    """
    _stream.start()
    _stream.flush() # Start fresh for this segment
    
    vad = SmartVAD()
    audio_chunks = []
    lead_buffer = deque(maxlen=int(500 / 30))
    speech_detected = False
    silence_chunks = 0
    max_silence_chunks = int(silence_duration * 1000 / 30)
    max_chunks = int(max_duration * 1000 / 30)
    
    start_time = time.time()
    
    try:
        while (time.time() - start_time) < (max_duration + 2.0): # Safety timeout
            chunk = _stream.get_chunk(timeout=0.1)
            if chunk is None: continue
            
            if vad.is_speech(chunk):
                if not speech_detected:
                    if verbose: print("\n[SPEECH] Detected!")
                    audio_chunks.extend(list(lead_buffer))
                    lead_buffer.clear()
                    speech_detected = True
                silence_chunks = 0
                audio_chunks.append(chunk)
            else:
                if speech_detected:
                    silence_chunks += 1
                    audio_chunks.append(chunk)
                    if silence_chunks > max_silence_chunks:
                        if verbose: print(f"[SILENCE] {silence_duration}s detected.")
                        break
                else:
                    lead_buffer.append(chunk)
            
            if len(audio_chunks) >= max_chunks:
                break
                
        if not audio_chunks:
            return None
            
        full_audio = np.concatenate(audio_chunks)
        
        # Optimize for Whisper
        rms = np.sqrt(np.mean(full_audio**2))
        if rms > 0.00001:
            gain = 0.1 / rms
            full_audio = full_audio * gain
            
        return full_audio
        
    except Exception as e:
        if verbose: print(f"[ERROR] capture_question: {e}")
        return None

if __name__ == "__main__":
    print("Testing capture...")
    q = capture_question(verbose=True)
    if q is not None:
        print(f"Captured {len(q)} samples.")
