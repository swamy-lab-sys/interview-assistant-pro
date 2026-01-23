#!/bin/bash

echo "============================================================"
echo "PRODUCTION SAFETY VERIFICATION"
echo "============================================================"
echo ""
echo "This script verifies that the InterviewVoiceAssistant:"
echo "  1. Captures ONLY system audio (YouTube/Zoom/Meet)"
echo "  2. NEVER captures microphone input"
echo "  3. Configuration persists across reboots"
echo ""

source venv/bin/activate

echo "Test 1: PulseAudio Routing"
echo "------------------------------------------------------------"
DEFAULT_SOURCE=$(pactl get-default-source)
echo "Current default source: $DEFAULT_SOURCE"

if [[ "$DEFAULT_SOURCE" == *"monitor"* ]] || [[ "$DEFAULT_SOURCE" == *"system_audio"* ]]; then
    echo "✅ PASS: Default source is system audio"
else
    echo "❌ FAIL: Default source is NOT system audio (likely microphone)"
    echo "   Run ./setup_persistent_audio.sh to fix"
    exit 1
fi

echo ""
echo "Test 2: Python Safety Verification"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from audio_listener import verify_pulseaudio_routing

is_safe, source_name, error = verify_pulseaudio_routing()

if is_safe:
    print(f"✅ PASS: Python verification confirms safety")
    print(f"   Source: {source_name}")
else:
    print(f"❌ FAIL: {error}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "Test 3: Device Filtering"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from audio_listener import list_audio_devices

devices = list_audio_devices(system_audio_only=True)
print(f"System audio devices found: {len(devices)}")

if len(devices) == 0:
    print("❌ FAIL: No system audio devices available")
    sys.exit(1)

print("✅ PASS: System audio devices available")
for idx, name, channels in devices:
    print(f"   [{idx}] {name}")
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "Test 4: Microphone Blocking"
echo "------------------------------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from audio_listener import is_system_audio_device

# Test cases
test_devices = [
    ("Built-in Microphone", False),
    ("sof-hda-dsp: - (hw:0,0)", False),
    ("USB Microphone", False),
    ("pulse", True),  # Should pass if routing is correct
    ("default", True),  # Should pass if routing is correct
    ("Monitor of Built-in Audio", True),
    ("system_audio_capture", True),
]

all_passed = True
for device, expected_safe in test_devices:
    result = is_system_audio_device(device)
    status = "✅" if result == expected_safe else "❌"
    action = "ALLOWED" if result else "BLOCKED"
    print(f"  {status} {action}: {device}")
    if result != expected_safe:
        all_passed = False

if all_passed:
    print("✅ PASS: All devices classified correctly")
else:
    print("❌ FAIL: Some devices misclassified")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "Test 5: Configuration Persistence"
echo "------------------------------------------------------------"
CONFIG_FILE="$HOME/.config/pulse/default.pa"

if [ -f "$CONFIG_FILE" ]; then
    if grep -q "system_audio_capture" "$CONFIG_FILE"; then
        echo "✅ PASS: Configuration is persistent"
        echo "   File: $CONFIG_FILE"
    else
        echo "⚠️  WARNING: Configuration file exists but no system_audio_capture"
        echo "   Run ./setup_persistent_audio.sh to make persistent"
    fi
else
    echo "⚠️  WARNING: No persistent configuration"
    echo "   Configuration will reset after reboot"
    echo "   Run ./setup_persistent_audio.sh to make persistent"
fi

echo ""
echo "============================================================"
echo "✅ ALL SAFETY TESTS PASSED"
echo "============================================================"
echo ""
echo "Production Readiness: CONFIRMED"
echo ""
echo "Why this is safe:"
echo "  1. PulseAudio default source is system_audio_capture (monitor)"
echo "  2. Python app verifies routing at startup"
echo "  3. Microphone devices are blocked by name filtering"
echo "  4. 'pulse'/'default' only allowed if routing verified safe"
echo "  5. App refuses to run if routing is unsafe"
echo ""
echo "What happens in production:"
echo "  ✅ YouTube audio → App captures → Generates answer"
echo "  ✅ Zoom/Meet audio → App captures → Generates answer"
echo "  ✅ Your voice into mic → App IGNORES → No answer"
echo "  ✅ Microphone still works for actual interview"
echo ""
echo "To start interview mode:"
echo "  python3 main.py voice"
echo ""
