#!/usr/bin/env python3
"""
Auto-detect which sink has actual audio and use that
"""

import subprocess
import time
import numpy as np
import sys

def get_all_monitors():
    """Get all available monitor sources."""
    result = subprocess.run(
        ['pactl', 'list', 'short', 'sources'],
        capture_output=True,
        text=True
    )
    
    monitors = []
    for line in result.stdout.split('\n'):
        if 'monitor' in line.lower():
            parts = line.split()
            if len(parts) >= 2:
                monitors.append(parts[1])
    
    return monitors

def test_monitor_for_audio(monitor, duration=3):
    """Test if a monitor has actual audio."""
    print(f"Testing: {monitor}...")
    
    cmd = f"timeout {duration} parec -d {monitor} --format=s16le --rate=16000 --channels=1"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=duration + 1
        )
        
        if result.stdout:
            audio_int16 = np.frombuffer(result.stdout, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32768.0
            
            # Check if there's actual audio (not just zeros)
            rms = np.sqrt(np.mean(audio_float**2))
            max_val = np.max(np.abs(audio_float))
            non_zero = np.count_nonzero(audio_float)
            
            print(f"  RMS: {rms:.6f}, Max: {max_val:.6f}, Non-zero: {non_zero}/{len(audio_float)}")
            
            # Consider it "has audio" if RMS > 0.0001 and has non-zero samples
            has_audio = rms > 0.0001 and non_zero > 100
            
            if has_audio:
                print(f"  ✅ HAS AUDIO!")
                return True, monitor
            else:
                print(f"  ❌ Silent/noise only")
                return False, None
                
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, None
    
    return False, None

print("=" * 70)
print("AUDIO SOURCE AUTO-DETECTION")
print("=" * 70)
print()
print("🎵 Please start playing YouTube audio NOW...")
print()
input("Press Enter when audio is playing...")
print()

# Get all monitors
monitors = get_all_monitors()
print(f"Found {len(monitors)} monitor sources:\n")

# Test each one
active_monitor = None
for monitor in monitors:
    has_audio, source = test_monitor_for_audio(monitor, duration=2)
    if has_audio:
        active_monitor = source
        break
    print()

print()
print("=" * 70)

if active_monitor:
    print(f"✅ FOUND ACTIVE AUDIO SOURCE!")
    print(f"   {active_monitor}")
    print()
    print("Updating config...")
    
    # Update the professional_audio.py to use this device
    config_line = f'DEFAULT_MONITOR = "{active_monitor}"'
    
    print()
    print("Add this line to professional_audio.py at the top:")
    print(f"  {config_line}")
    print()
    print("Or run:")
    print(f'  echo \'{config_line}\' >> professional_audio.py')
    
else:
    print("❌ NO ACTIVE AUDIO SOURCE FOUND!")
    print()
    print("Possible issues:")
    print("1. YouTube is not actually playing")
    print("2. Browser audio is muted")
    print("3. Audio is going to headphones/external device")
    print()
    print("Try:")
    print("  - Unmute browser tab")
    print("  - Check system volume")
    print("  - Use built-in speakers (not headphones)")
    print("  - Run: pavucontrol  (to see audio routing)")

sys.exit(0 if active_monitor else 1)
