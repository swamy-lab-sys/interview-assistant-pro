#!/bin/bash

echo "============================================================"
echo "System Audio Device Test"
echo "============================================================"
echo ""
echo "This script verifies that ONLY system audio devices are shown"
echo "and microphones are completely blocked."
echo ""

source venv/bin/activate

echo "Step 1: List ALL audio devices"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sounddevice as sd

print("\nAll input devices:")
devices = sd.query_devices()
for idx, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"  [{idx}] {device['name']} ({device['max_input_channels']} ch)")
EOF

echo ""
echo "Step 2: List SYSTEM AUDIO devices only (monitors/loopbacks)"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from audio_listener import list_audio_devices, is_system_audio_device

print("\nSystem audio devices (microphones filtered out):")
devices = list_audio_devices(system_audio_only=True)

if not devices:
    print("  ❌ NO SYSTEM AUDIO DEVICES FOUND")
    print("")
    print("  To enable system audio capture:")
    print("  1. Install: sudo apt install pavucontrol")
    print("  2. Run: pavucontrol")
    print("  3. Recording tab → Show: 'Monitor of...'")
    print("")
    print("  Or enable loopback:")
    print("  pactl load-module module-loopback")
else:
    for idx, name, channels in devices:
        status = "✓ SYSTEM AUDIO" if is_system_audio_device(name) else "✗ BLOCKED"
        print(f"  [{idx}] {name} - {status}")
EOF

echo ""
echo "Step 3: Verify microphone blocking"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from audio_listener import is_system_audio_device

test_devices = [
    "Built-in Microphone",
    "Monitor of Built-in Audio",
    "USB Microphone",
    "Loopback",
    "Stereo Mix",
    "Webcam Audio",
]

print("\nDevice classification test:")
for device in test_devices:
    result = is_system_audio_device(device)
    status = "✓ ALLOWED" if result else "🚫 BLOCKED"
    print(f"  {status}: {device}")
EOF

echo ""
echo "============================================================"
echo "Test Complete"
echo "============================================================"
echo ""
echo "Expected results:"
echo "  • Microphones are BLOCKED"
echo "  • Monitor/Loopback devices are ALLOWED"
echo "  • Only system audio appears in voice mode selection"
echo ""
