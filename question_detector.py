"""
Real-time Question Detection
Listens to audio stream and only captures when a question is being asked
"""

import numpy as np
from professional_audio import DirectAudioCapture, SmartVAD, SAMPLE_RATE
import time
from collections import deque

# Question trigger words (must appear in audio to start capture)
QUESTION_TRIGGERS = [
    'what', 'why', 'how', 'explain', 'define', 'describe',
    'difference', 'compare', 'tell me', 'can you',
    'could you', 'would you', 'show me'
]

class QuestionDetector:
    """
    Intelligent question detector that only captures when questions are asked.
    Uses real-time STT to detect question words before full capture.
    """
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.capturer = DirectAudioCapture()
        self.vad = SmartVAD()
        
    def wait_for_question(self, timeout=300):
        """
        Wait for a question to be asked, then capture it.
        
        Returns:
            numpy array of captured question audio
        """
        try:
            self.capturer.start()
            
            if self.verbose:
                print("[WAITING] Listening for questions...")
            
            buffer = deque(maxlen=int(3.0 * SAMPLE_RATE / 480))  # 3 second rolling buffer
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                chunk = self.capturer.get_chunk(timeout=0.1)
                
                if chunk is None:
                    continue
                
                # Add to rolling buffer
                buffer.append(chunk)
                
                # Check for speech
                if self.vad.is_speech(chunk):
                    # Every 1 second of speech, check if it's a question
                    if len(buffer) >= int(1.0 * SAMPLE_RATE / 480):
                        # Quick transcription of last 1 second
                        recent_audio = np.concatenate(list(buffer)[-int(1.0 * SAMPLE_RATE / 480):])
                        
                        # Apply gain for transcription
                        current_rms = np.sqrt(np.mean(recent_audio**2))
                        if current_rms > 0.00001:
                            gain = 0.1 / current_rms
                            recent_audio = recent_audio * gain
                        
                        # Quick transcription
                        text = self._quick_transcribe(recent_audio)
                        
                        if text and self._contains_question_word(text):
                            if self.verbose:
                                print(f"\n[QUESTION DETECTED] '{text[:50]}...'")
                            
                            # Capture the full question
                            return self._capture_full_question(buffer)
            
            if self.verbose:
                print("[TIMEOUT] No question detected")
            return np.array([], dtype=np.float32)
            
        finally:
            self.capturer.stop()
    
    def _quick_transcribe(self, audio):
        """Quick transcription for question detection."""
        try:
            from stt import transcribe
            text, _ = transcribe(audio)
            return text.lower()
        except:
            return ""
    
    def _contains_question_word(self, text):
        """Check if text contains question trigger words."""
        text_lower = text.lower()
        for trigger in QUESTION_TRIGGERS:
            if trigger in text_lower:
                return True
        return False
    
    def _capture_full_question(self, initial_buffer):
        """Capture the complete question after detection."""
        audio_chunks = list(initial_buffer)
        
        silence_chunks = 0
        max_silence_chunks = int(0.8 * 1000 / 30)  # 0.8s silence
        max_chunks = int(6.0 * 1000 / 30)  # 6s max
        
        if self.verbose:
            print("[CAPTURING] Full question...")
        
        while len(audio_chunks) < max_chunks:
            chunk = self.capturer.get_chunk(timeout=0.05)
            
            if chunk is None:
                break
            
            if self.vad.is_speech(chunk):
                silence_chunks = 0
                audio_chunks.append(chunk)
            else:
                silence_chunks += 1
                audio_chunks.append(chunk)
                
                if silence_chunks > max_silence_chunks:
                    break
        
        # Concatenate and normalize
        full_audio = np.concatenate(audio_chunks)
        
        # Auto-gain
        current_rms = np.sqrt(np.mean(full_audio**2))
        if current_rms > 0.00001:
            target_rms = 0.1
            gain = target_rms / current_rms
            full_audio = full_audio * gain
            
            if self.verbose:
                print(f"[GAIN] Applied {gain:.1f}x gain")
        
        if self.verbose:
            duration = len(full_audio) / SAMPLE_RATE
            print(f"[CAPTURED] {duration:.2f}s question")
        
        return full_audio


def capture_question_smart(max_wait=300, verbose=True):
    """
    Smart question capture - waits for a question, then captures it.
    
    Args:
        max_wait: Maximum time to wait for a question (seconds)
        verbose: Print debug info
    
    Returns:
        numpy array of captured question audio
    """
    detector = QuestionDetector(verbose=verbose)
    return detector.wait_for_question(timeout=max_wait)


if __name__ == "__main__":
    print("Smart Question Detector - Test")
    print("Play a video with questions...")
    
    audio = capture_question_smart(max_wait=60, verbose=True)
    
    if len(audio) > 0:
        print(f"\nSuccess! Captured {len(audio)/16000:.2f}s")
        
        # Transcribe
        from stt import transcribe
        text, conf = transcribe(audio)
        print(f"Question: {text}")
        print(f"Confidence: {conf:.2f}")
    else:
        print("\nNo question detected")
