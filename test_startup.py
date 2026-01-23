#!/usr/bin/env python3
"""Test startup without entering voice loop"""

import os
import sys

# Set dummy API key
os.environ["ANTHROPIC_API_KEY"] = "test-key"

# Mock stdin for device selection
from io import StringIO
sys.stdin = StringIO("1\n")

print("="*60)
print("TESTING APP STARTUP")
print("="*60)
print()

# Now run the startup portion
import audio_listener
import sounddevice as sd

print("Step 1: Device selection")
selected = audio_listener.select_audio_device_interactive()
print(f"✓ Selected device: {selected}")
print()

print("Step 2: Get device name")
device_name = "Unknown Device"
try:
    device_info = sd.query_devices(audio_listener.SELECTED_AUDIO_DEVICE)
    device_name = device_info['name']
    print(f"✓ Device name: {device_name}")
except Exception as e:
    print(f"⚠️  Error getting device name: {e}")
    try:
        devices = sd.query_devices()
        if audio_listener.SELECTED_AUDIO_DEVICE is not None and audio_listener.SELECTED_AUDIO_DEVICE < len(devices):
            device_name = devices[audio_listener.SELECTED_AUDIO_DEVICE]['name']
            print(f"✓ Device name (fallback): {device_name}")
    except:
        device_name = f"Device #{audio_listener.SELECTED_AUDIO_DEVICE}"
        print(f"✓ Device name (final fallback): {device_name}")

print()
print("="*60)
print("✅ STARTUP TEST PASSED")
print(f"   Device: {device_name}")
print("="*60)
