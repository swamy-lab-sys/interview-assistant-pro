# 🎤 Voice Mode - Quick Reference

## Three Ways to Use the Interview Assistant

### 1. 🎤 **Voice Mode** (RECOMMENDED) - NEW!
**ChatGPT-style push-to-talk for real-time verbal interviews**

```bash
./start_voice_mode.sh
# Opens http://localhost:8000/voice
```

**How it works:**
1. Hold SPACE (or click mic button)
2. Speak your question clearly
3. Release to transcribe
4. Edit if needed
5. Send to get answer

**Perfect for:**
- ✅ Verbal interview questions
- ✅ Need high accuracy (90%+)
- ✅ Want control over recording
- ✅ Professional conversation UI

**See:** [VOICE_MODE_GUIDE.md](./VOICE_MODE_GUIDE.md) for complete guide

---

### 2. 🔊 **Always-On Mode** (Original)
**Automatic voice capture from system audio**

```bash
./run.sh
# Continuously listens to system audio
```

**How it works:**
- Automatically captures all system audio
- Transcribes and validates questions
- Shows answers on http://localhost:8000

**Perfect for:**
- ✅ Hands-free operation
- ⚠️ Lower accuracy (70-80%)
- ⚠️ Captures background noise

---

### 3. 🌐 **URL Mode** (Browser Extension)
**Automatic coding solutions on LeetCode/HackerRank**

```bash
# Install Chrome extension from chrome_extension_programiz/
```

**How it works:**
- Detects coding platform URLs
- Captures problem text
- Auto-types solution in editor

**Perfect for:**
- ✅ Coding challenges
- ✅ LeetCode, HackerRank, etc.
- ✅ Need code auto-typed

---

## Quick Comparison

| Feature | Voice (Push-to-Talk) | Always-On | URL/Extension |
|---------|---------------------|-----------|---------------|
| **Accuracy** | 90-95% ✅ | 70-80% ⚠️ | N/A |
| **Control** | Full ✅ | None ⚠️ | Medium ⚠️ |
| **UI** | ChatGPT-style ✅ | Terminal 📊 | Browser popup 🔧 |
| **Use Case** | Verbal Q&A ✅ | System audio 🔊 | Coding platforms 💻 |
| **Mobile** | Yes ✅ | No ❌ | No ❌ |
| **Editing** | Yes ✅ | No ❌ | No ❌ |

## Which Mode Should I Use?

### Use **Voice Mode** (Push-to-Talk) if:
- You're in a **real-time interview** (Zoom, Meet, Teams)
- Questions are **asked verbally** by interviewer
- You want **accurate transcription** (90%+)
- You need **control** over when to record
- You want a **professional UI**

### Use **Always-On Mode** if:
- You prefer **completely hands-free**
- You're okay with **lower accuracy**
- Questions come from **system audio/YouTube**

### Use **URL Mode** if:
- You're on a **coding platform** (LeetCode, etc.)
- Problem is **visible on screen**
- You need **code auto-typed** into editor

---

## Installation

### Quick Setup
```bash
# Clone repo
cd InterviewVoiceAssistant

# Install dependencies
pip install -r requirements.txt
pip install pydub  # For voice mode

# For audio conversion (voice mode)
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

### Start Voice Mode
```bash
chmod +x start_voice_mode.sh
./start_voice_mode.sh
```

### Start Always-On Mode  
```bash
chmod +x run.sh
./run.sh
```

---

## Documentation

- 📘 **[VOICE_MODE_GUIDE.md](./VOICE_MODE_GUIDE.md)** - Complete voice mode guide
- 📗 **[README.md](./README.md)** - Main documentation
- 📙 **[VOICE_MODE_IMPLEMENTATION.md](./VOICE_MODE_IMPLEMENTATION.md)** - Technical details
- 📕 **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues

---

## Screenshots

### Voice Mode Interface
![Voice Mode](/.gemini/antigravity/brain/6b5ac394-1596-4e4a-af3e-17cc24d769a2/voice_mode_interface_1770478448463.png)

*ChatGPT-style conversation view with push-to-talk controls*

---

## Key Features

### Voice Mode (NEW)
- ✅ **Push-to-Talk** - Hold SPACE or click button
- ✅ **High Accuracy** - 90%+ transcription  
- ✅ **Editable** - Fix mistakes before sending
- ✅ **Conversation View** - ChatGPT-style bubbles
- ✅ **Mobile Ready** - Touch support
- ✅ **Visual Feedback** - Waveforms, status updates
- ✅ **Code Highlighting** - Syntax-highlighted answers
- ✅ **No Background Noise** - Only records when you press

### Always-On Mode
- 🔊 Continuous system audio capture
- 🎯 Automatic question detection
- 📊 Real-time answer display
- 💾 Resume and JD context

### URL Mode
- 🌐 Works on coding platforms
- ⚡ Auto-detects problem text
- ⌨️ Auto-types solution
- 🎛️ Stealth mode controls

---

## Support

For issues or questions:
1. Check **[VOICE_MODE_GUIDE.md](./VOICE_MODE_GUIDE.md)** - Troubleshooting section
2. Review **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**
3. Verify dependencies installed
4. Test browser mic permissions

---

**Made with ❤️ for interview success** 🚀
