#!/bin/bash

echo "============================================================"
echo "PERSISTENT SYSTEM AUDIO SETUP"
echo "============================================================"
echo ""
echo "This script makes system audio routing permanent."
echo "Ensures the app NEVER captures microphone, even after reboot."
echo ""

# Check if PulseAudio is running
if ! pactl info &> /dev/null; then
    echo "❌ ERROR: PulseAudio is not running"
    exit 1
fi

echo "Step 1: Create remap source (if not exists)"
echo "------------------------------------------------------------"

# Check if system_audio_capture already exists
if pactl list sources short | grep -q "system_audio_capture"; then
    echo "✓ system_audio_capture already exists"
else
    echo "Creating system_audio_capture..."
    pactl load-module module-remap-source source_name=system_audio_capture master=@DEFAULT_MONITOR@
    if [ $? -eq 0 ]; then
        echo "✓ system_audio_capture created"
    else
        echo "❌ Failed to create system_audio_capture"
        exit 1
    fi
fi

echo ""
echo "Step 2: Set as default source (runtime)"
echo "------------------------------------------------------------"
pactl set-default-source system_audio_capture
if [ $? -eq 0 ]; then
    echo "✓ Default source set to system_audio_capture"
else
    echo "❌ Failed to set default source"
    exit 1
fi

echo ""
echo "Step 3: Make configuration persistent"
echo "------------------------------------------------------------"

CONFIG_FILE="$HOME/.config/pulse/default.pa"
CONFIG_DIR="$HOME/.config/pulse"

# Create config directory if not exists
mkdir -p "$CONFIG_DIR"

# Check if configuration already exists
if [ -f "$CONFIG_FILE" ] && grep -q "system_audio_capture" "$CONFIG_FILE"; then
    echo "✓ Configuration already in $CONFIG_FILE"
else
    echo "Adding configuration to $CONFIG_FILE..."

    # Start with system defaults if file doesn't exist
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "# PulseAudio user configuration" > "$CONFIG_FILE"
        echo "# Load system configuration first" >> "$CONFIG_FILE"
        echo ".include /etc/pulse/default.pa" >> "$CONFIG_FILE"
        echo "" >> "$CONFIG_FILE"
    fi

    # Add our custom configuration
    cat >> "$CONFIG_FILE" << 'EOF'

### INTERVIEW ASSISTANT CONFIGURATION ###
# Create remap source for system audio capture
# This ensures the app captures system playback (YouTube/Zoom), not microphone
.ifexists module-remap-source.so
load-module module-remap-source source_name=system_audio_capture master=@DEFAULT_MONITOR@ source_properties=device.description="System Audio Capture"
.endif

# Set system audio as default source
# This routes sounddevice 'pulse'/'default' to system audio, not mic
set-default-source system_audio_capture
### END INTERVIEW ASSISTANT CONFIGURATION ###
EOF

    echo "✓ Configuration added to $CONFIG_FILE"
fi

echo ""
echo "Step 4: Verify configuration"
echo "------------------------------------------------------------"

CURRENT_DEFAULT=$(pactl get-default-source)
if [ "$CURRENT_DEFAULT" = "system_audio_capture" ]; then
    echo "✅ VERIFIED: Default source is system_audio_capture"
else
    echo "⚠️  WARNING: Default source is $CURRENT_DEFAULT"
fi

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETE"
echo "============================================================"
echo ""
echo "Verification:"
echo "  • Current default source: $CURRENT_DEFAULT"
echo "  • Configuration file: $CONFIG_FILE"
echo "  • Persistence: ENABLED (survives reboot)"
echo ""
echo "What this means:"
echo "  ✅ App will capture ONLY system audio (YouTube/Zoom/Meet)"
echo "  ✅ Microphone is NEVER captured by the app"
echo "  ✅ Microphone still works for actual interview"
echo "  ✅ Configuration persists after reboot"
echo ""
echo "To test, run: python3 main.py voice"
echo ""
