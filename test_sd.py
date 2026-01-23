import sounddevice as sd
import numpy as np
import time

print("Recording 5 seconds from 'default' using sounddevice...")
duration = 5  # seconds
fs = 16000
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
sd.wait()
rms = np.sqrt(np.mean(recording**2))
non_zero = np.count_nonzero(recording)
print(f"RMS: {rms:.6f}, Non-zero samples: {non_zero}")

if rms > 0.001:
    print("SUCCESS: Audio detected!")
else:
    print("FAILURE: Silence detected.")
