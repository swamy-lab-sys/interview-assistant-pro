# Interview Voice Assistant - Complete Setup Guide

This document provides comprehensive instructions for setting up the Interview Voice Assistant from scratch, including Docker deployment, driver fixes, and troubleshooting.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [System Dependencies](#system-dependencies)
3. [Python Environment Setup](#python-environment-setup)
4. [Environment Variables](#environment-variables)
5. [Audio Configuration](#audio-configuration)
6. [Docker Setup](#docker-setup)
7. [Running the Application](#running-the-application)
8. [Troubleshooting](#troubleshooting)
9. [Driver Fixes](#driver-fixes)

---

## System Requirements

### Minimum
- **OS**: Ubuntu 20.04+ / Debian 11+ / Similar Linux distro
- **Python**: 3.10 or higher
- **RAM**: 2GB (3-4GB with GPU)
- **Storage**: 5GB (for models and dependencies)
- **Audio**: PulseAudio or PipeWire audio system
- **Network**: Internet connection (for Claude API)

### Recommended
- **GPU**: NVIDIA CUDA-capable GPU (4x speed boost for Whisper)
- **RAM**: 4GB+
- **Storage**: SSD for faster model loading

---

## System Dependencies

### Install Required System Packages

```bash
# Update package lists
sudo apt update

# Audio libraries (PortAudio for sounddevice/pyaudio)
sudo apt install -y portaudio19-dev python3-pyaudio

# PulseAudio utilities (for system audio capture)
sudo apt install -y pulseaudio-utils pulseaudio

# Build essentials (for compiling some Python packages)
sudo apt install -y build-essential python3-dev

# FFmpeg (for audio processing)
sudo apt install -y ffmpeg

# Git (if cloning from repository)
sudo apt install -y git
```

### For NVIDIA GPU Support (Optional but Recommended)

```bash
# Install NVIDIA drivers (if not already installed)
sudo apt install -y nvidia-driver-535  # Or latest version

# Install CUDA toolkit
sudo apt install -y nvidia-cuda-toolkit

# Verify CUDA installation
nvidia-smi
nvcc --version
```

---

## Python Environment Setup

### Step 1: Clone/Copy Project

```bash
cd /home/venkat
# If cloning from git:
# git clone <repository-url> InterviewVoiceAssistant

cd InterviewVoiceAssistant
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
anthropic          # Claude API client
sounddevice        # Audio I/O (PortAudio wrapper)
numpy              # Numerical processing
pyaudio            # Alternative audio backend
webrtcvad          # Voice Activity Detection
pyannote.audio     # Speaker diarization (optional)
torch              # PyTorch ML framework
whisperx           # Optimized Whisper STT
flask              # Web UI framework
soundfile          # Audio file I/O
```

### Step 4: Verify Installation

```bash
# Check PyTorch and CUDA
python3 -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

# Check Whisper
python3 -c "import whisperx; print('WhisperX imported successfully')"

# Check Anthropic
python3 -c "import anthropic; print('Anthropic client ready')"

# Check audio
python3 -c "import sounddevice; print('Audio devices:', sounddevice.query_devices())"
```

### Alternative: Use setup.sh

```bash
chmod +x setup.sh
./setup.sh
```

---

## Environment Variables

### Required

```bash
# Anthropic Claude API Key (REQUIRED)
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxx"

# Get your key from: https://console.anthropic.com/
```

### Optional

```bash
# Hugging Face token (for advanced speaker diarization)
export HUGGINGFACE_TOKEN="hf_xxxxxxxxxxxxx"
# Get from: https://huggingface.co/settings/tokens

# Speaker volume threshold (auto-calibrated by default)
export SPEAKER_VOLUME_THRESHOLD="0.02"

# PulseAudio source (auto-configured by run.sh)
export PULSE_SOURCE="alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"
```

### Persist Environment Variables

Add to `~/.bashrc` or `~/.profile`:

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Audio Configuration

### PulseAudio Setup (Default on Ubuntu)

```bash
# Check PulseAudio is running
pulseaudio --check
pulseaudio --start  # Start if not running

# List audio sources
pactl list short sources

# Get default sink (for monitoring system audio)
pactl get-default-sink

# The monitor source will be: <default-sink>.monitor
# Example: alsa_output.pci-0000_00_1f.3.analog-stereo.monitor
```

### PipeWire Setup (Newer Systems)

```bash
# Check if PipeWire is running
systemctl --user status pipewire pipewire-pulse

# List sources (PipeWire uses same pactl commands)
pactl list short sources

# PipeWire should work seamlessly as a PulseAudio replacement
```

### Verify Audio Capture

```bash
# Test recording from monitor source
parecord --device=$(pactl get-default-sink).monitor test.wav

# Play something and record for 5 seconds
# Then verify the recording
paplay test.wav
```

---

## Docker Setup

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    pulseaudio-utils \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /root/.interview_assistant

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONWARNINGS=ignore

# Expose web UI port
EXPOSE 8000

# Default command
CMD ["python", "main.py", "voice"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  interview-assistant:
    build: .
    container_name: interview-voice-assistant
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN:-}
      - PULSE_SERVER=unix:/run/user/1000/pulse/native
    volumes:
      # Mount PulseAudio socket for audio access
      - /run/user/1000/pulse:/run/user/1000/pulse
      - ~/.config/pulse/cookie:/root/.config/pulse/cookie:ro
      # Persist answers
      - ~/.interview_assistant:/root/.interview_assistant
      # Mount resume file
      - ./resume.txt:/app/resume.txt:ro
    ports:
      - "8000:8000"
    devices:
      # Pass through audio devices (optional)
      - /dev/snd:/dev/snd
    group_add:
      - audio
    restart: unless-stopped
    network_mode: host  # For easier audio access

  # Optional: GPU support
  interview-assistant-gpu:
    build: .
    container_name: interview-voice-assistant-gpu
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN:-}
      - PULSE_SERVER=unix:/run/user/1000/pulse/native
    volumes:
      - /run/user/1000/pulse:/run/user/1000/pulse
      - ~/.config/pulse/cookie:/root/.config/pulse/cookie:ro
      - ~/.interview_assistant:/root/.interview_assistant
      - ./resume.txt:/app/resume.txt:ro
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    network_mode: host
    profiles:
      - gpu
```

### Build and Run with Docker

```bash
# Create .env file for Docker
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Build image
docker-compose build

# Run (CPU version)
docker-compose up -d interview-assistant

# Run (GPU version)
docker-compose --profile gpu up -d interview-assistant-gpu

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Audio Troubleshooting

If audio doesn't work in Docker:

```bash
# Option 1: Use host network and mount PulseAudio
# (Already configured in docker-compose.yml)

# Option 2: Run PulseAudio in TCP mode
# On host:
pactl load-module module-native-protocol-tcp auth-anonymous=1

# In container, set:
export PULSE_SERVER=tcp:host.docker.internal:4713

# Option 3: Use privileged mode (not recommended for production)
docker run --privileged ...
```

---

## Running the Application

### Using run.sh (Recommended)

```bash
# Make executable
chmod +x run.sh

# Run in voice mode (default)
./run.sh

# Or with explicit mode
./run.sh voice
./run.sh text
./run.sh streaming
```

### Manual Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export ANTHROPIC_API_KEY="your-key"

# Configure audio source
export PULSE_SOURCE="$(pactl get-default-sink).monitor"

# Run
python main.py voice
```

### Available Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `voice` | Real-time audio capture | Production/Interviews |
| `text` | Keyboard input | Testing without audio |
| `streaming` | Streaming responses | Experimental |

### Access Web UI

After starting, open: **http://localhost:8000**

---

## Troubleshooting

### Issue: "No module named 'sounddevice'"

```bash
# Install PortAudio development files
sudo apt install -y portaudio19-dev

# Reinstall sounddevice
pip uninstall sounddevice
pip install sounddevice
```

### Issue: "ALSA lib pcm.c:xxx Broken configuration"

```bash
# Create/edit ALSA config
sudo nano /etc/asound.conf

# Add:
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}

# Restart PulseAudio
pulseaudio -k
pulseaudio --start
```

### Issue: "Connection refused" on PulseAudio

```bash
# Check PulseAudio status
systemctl --user status pulseaudio

# Start PulseAudio
pulseaudio --start

# If using PipeWire
systemctl --user restart pipewire pipewire-pulse
```

### Issue: "ANTHROPIC_API_KEY not set"

```bash
# Set the key
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxx"

# Verify
echo $ANTHROPIC_API_KEY
```

### Issue: Whisper model download fails

```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface/hub/models--*whisper*
rm -rf ~/.cache/whisper

# Set HuggingFace token if needed
export HUGGINGFACE_TOKEN="hf_xxxxx"

# Retry
python -c "import whisperx; whisperx.load_model('tiny.en')"
```

### Issue: CUDA out of memory

```bash
# Use smaller model in config.py
# Change STT_MODEL from "small" to "tiny.en"

# Or disable GPU
export CUDA_VISIBLE_DEVICES=""
```

### Issue: No audio captured

```bash
# List audio sources
pactl list short sources

# Find the monitor source (ends with .monitor)
# Set it explicitly
export PULSE_SOURCE="alsa_output.pci-0000_00_1f.3.analog-stereo.monitor"

# Test capture
python -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## Driver Fixes

### PortAudio Driver Issues

```bash
# Reinstall PortAudio
sudo apt remove --purge portaudio19-dev
sudo apt install portaudio19-dev

# Rebuild PyAudio
pip uninstall pyaudio
pip install --no-cache-dir pyaudio
```

### ALSA Driver Issues

```bash
# Check ALSA version
aplay --version

# Reinstall ALSA
sudo apt install --reinstall alsa-base alsa-utils

# Reload ALSA
sudo alsa force-reload
```

### PulseAudio Driver Issues

```bash
# Remove and reinstall PulseAudio
sudo apt remove --purge pulseaudio
sudo apt install pulseaudio pulseaudio-utils

# Remove user config
rm -rf ~/.config/pulse

# Restart
pulseaudio -k
pulseaudio --start
```

### NVIDIA Driver Updates

```bash
# Check current driver
nvidia-smi

# List available drivers
ubuntu-drivers devices

# Install recommended driver
sudo ubuntu-drivers autoinstall

# Or specific version
sudo apt install nvidia-driver-535

# Reboot required
sudo reboot
```

### PyTorch CUDA Version Mismatch

```bash
# Check CUDA version
nvcc --version

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio

# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

### WebRTC VAD Issues

```bash
# Reinstall webrtcvad
pip uninstall webrtcvad
pip install --no-cache-dir webrtcvad

# If compilation fails, install from wheel
pip install webrtcvad-wheels
```

---

## Quick Reference Commands

```bash
# Start application
./run.sh

# Check audio devices
pactl list short sources

# Monitor system audio
export PULSE_SOURCE="$(pactl get-default-sink).monitor"

# Check GPU
nvidia-smi

# Check Python environment
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Clear Whisper cache
rm -rf ~/.cache/whisper

# View logs
tail -f ~/.interview_assistant/answer_history.jsonl

# Test audio capture
python -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## File Locations

| File/Directory | Purpose |
|----------------|---------|
| `main.py` | Main application entry point |
| `config.py` | Configuration settings |
| `resume.txt` | Your resume content |
| `requirements.txt` | Python dependencies |
| `~/.interview_assistant/` | Answer storage directory |
| `~/.cache/whisper/` | Whisper model cache |
| `venv/` | Python virtual environment |

---

## Support

If you encounter issues not covered here:

1. Check the existing documentation files (QUICKSTART.md, PRODUCTION_READY.md)
2. Review logs for error messages
3. Ensure all environment variables are set correctly
4. Verify audio capture is working with `parecord`

---

*Last updated: January 2026*
