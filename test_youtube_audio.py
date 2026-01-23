#!/usr/bin/env python3
"""
Test if we can capture YouTube audio
"""

import subprocess
import time
import numpy as np

print("=" * 60)
print("YOUTUBE AUDIO CAPTURE TEST")
print("=" * 60)
print()
print("Instructions:")
print("1. Make sure YouTube is playing in your browser")
print("2. This will record 10 seconds of system audio")
print("3. We'll check if we can hear anything")
print()
input("Press Enter when YouTube is playing...")

# Get default sink monitor
result = subprocess.run(
    ['pactl', 'get-default-sink'],
    capture_output=True,
    text=True
)
sink = result.stdout.strip()
monitor = f"{sink}.monitor"

print(f"\nCapturing from: {monitor}")
print("Recording 10 seconds...")

# Record using parec
cmd = f"parec -d {monitor} --format=s16le --rate=16000 --channels=1 --latency-msec=30"
process = subprocess.Popen(
    cmd,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

# Capture for 10 seconds
time.sleep(10)
process.terminate()

# Read the data
raw_data = process.stdout.read()
print(f"Captured {len(raw_data)} bytes")

# Convert to numpy
audio_int16 = np.frombuffer(raw_data, dtype=np.int16)
audio_float = audio_int16.astype(np.float32) / 32768.0

# Apply gain
audio_float = audio_float * 250.0

# Stats
rms = np.sqrt(np.mean(audio_float**2))
max_val = np.max(np.abs(audio_float))

print(f"\nAudio Stats:")
print(f"  Samples: {len(audio_float)}")
print(f"  Duration: {len(audio_float)/16000:.2f}s")
print(f"  RMS: {rms:.5f}")
print(f"  Max: {max_val:.5f}")

# Save
import soundfile as sf
sf.write('/tmp/youtube_test.wav', audio_float, 16000)
print(f"\nSaved to: /tmp/youtube_test.wav")

# Try to transcribe
print("\nTranscribing...")
from stt import transcribe

text, conf = transcribe(audio_float)
print(f"\nResult: \"{text}\"")
print(f"Confidence: {conf:.2f}")

if not text:
    print("\n⚠️  NO SPEECH DETECTED!")
    print("\nPossible issues:")
    print("1. YouTube audio is not playing through the default sink")
    print("2. Browser audio is muted")
    print("3. Audio is going to a different output device")
    print("\nTry:")
    print("  - Check browser volume")
    print("  - Play the audio file: aplay /tmp/youtube_test.wav")
    print("  - Check: pactl list sink-inputs")
else:
    print("\n✅ SUCCESS! Audio is being captured correctly!")
