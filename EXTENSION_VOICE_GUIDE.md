# Voice Mode Chrome Extension - Installation & Usage Guide

## 🎯 Purpose

**Quick-access Chrome extension for the voice assistant during real interviews**

### Key Features:
- ✅ **Global Keyboard Shortcuts** - Access voice mode from any tab
- ✅ **Popup Mode** - Small window beside your interview
- ✅ **Tab Mode** - Full-screen voice interface
- ✅ **Server Status Check** - Know if backend is running
- ✅ **One-Click Access** - No typing URLs

---

## 📦 Installation

### 1. Load Extension in Chrome

```bash
# Extension is ready at:
~/InterviewVoiceAssistant/chrome_extension_voice/
```

**Steps:**
1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (top right)
4. Click **Load unpacked**
5. Select folder: `/home/venkat/InterviewVoiceAssistant/chrome_extension_voice`
6. Extension installed! 🎉

### 2. Pin the Extension

1. Click the puzzle icon (🧩) in Chrome toolbar
2. Find "Interview Voice Assistant"
3. Click the pin icon 📌
4. The microphone icon now appears in your toolbar

---

## 🎮 Usage During Interviews

### Method 1: Keyboard Shortcuts (FASTEST)

| Shortcut | Action |
|----------|--------|
| **Ctrl+Shift+V** | Open voice mode in new tab |
| **Ctrl+Shift+A** | Open voice mode in popup window |

**Best Practice:**
- Use **Ctrl+Shift+A** for popup mode during interviews
- Positions window on the right side of your screen
- Keep interview on left, voice assistant on right

### Method 2: Click Extension Icon

1. Click the 🎤 icon in Chrome toolbar
2. Beautiful popup appears showing:
   - Server status (online/offline)
   - "Open Voice Mode (Tab)" button
   - "Open Voice Mode (Popup)" button
   - "View All Answers" button
   - Keyboard shortcuts reference

3. Click your preferred option

---

## 🎬 Real Interview Workflow

### Setup (Before Interview)

1. **Start server:**
   ```bash
   cd ~/InterviewVoiceAssistant
   python3 web/server.py &
   ```

2. **Open popup voice assistant:**
   - Press **Ctrl+Shift+A**
   - Or click extension icon → "Open Voice Mode (Popup)"

3. **Position windows:**
   - Interview (Zoom/Meet) on left half of screen
   - Voice assistant popup on right half

4. **Test microphone:**
   - Hold SPACE in voice assistant
   - Say "Test microphone"
   - Verify transcription works

### During Interview

**Scenario: Interviewer Asks Technical Question**

```
📞 Interviewer (on Zoom): "Explain how async/await works in Python"

You:
  1. Click on voice assistant window
  2. Hold SPACE
  3. Say clearly: "Explain async await in Python"
  4. Release SPACE
  5. Review transcription (edit if needed)
  6. Click "Send Question"
  7. [Answer appears in 2-3 seconds]
  8. Answer verbally while reading from screen
```

**Scenario: Follow-up Question**

```
📞 Interviewer: "Can you give an example?"

You:
  1. Hold SPACE (voice window already open)
  2. Say: "Give an example of async await"
  3. Release, review, send
  4. [Code example appears]
  5. Type manually or explain from example
```

---

## 🖥️ Window Modes Comparison

### Tab Mode (Ctrl+Shift+V)
**When to use:**
- Full-screen voice interface
- Not during active video call
- Practice/testing
- Need maximum visibility

**Pros:**
- ✅ Large, easy to read
- ✅ Full conversation history
- ✅ Comfortable typing

**Cons:**
- ❌ Have to switch tabs during interview
- ❌ Less discreet

### Popup Mode (Ctrl+Shift+A) - RECOMMENDED
**When to use:**
- **During live interviews** ✅
- Side-by-side with video call
- Quick glances at answers

**Pros:**
- ✅ Stays on top of other windows
- ✅ Positioned on the side (right edge)
- ✅ Always visible
- ✅ Small footprint (500x800px)
- ✅ **Perfect for interviews!**

**Cons:**
- ⚠️ Smaller text (still readable)

---

## 💡 Pro Tips for Interviews

### 1. **Two Monitor Setup**
If you have 2 monitors:
- Monitor 1: Interview (Zoom/Meet)
- Monitor 2: Voice assistant (tab mode)
- Even better visibility!

### 2. **Test Before Interview**
```bash
# 5 minutes before interview:
1. Press Ctrl+Shift+A
2. Test: "What is Python?" 
3. Verify transcription works
4. Verify answer appears
5. Ready! ✅
```

### 3. **Keep Extension Pinned**
- Pin to Chrome toolbar
- Quick visual check: green dot = server online
- One-click access anytime

### 4. **Practice Shortcuts**
- Get muscle memory for Ctrl+Shift+A
- No fumbling during real interview
- Smooth, natural workflow

### 5. **Second Device Option**
Can't use popup on same screen?
- Open http://\<your-ip\>:8000/voice on phone/tablet
- Place beside laptop
- Glance down for answers

---

## 🎨 Extension Popup Preview

When you click the extension icon, you see:

```
┌──────────────────────────────┐
│  🎤 Voice Assistant          │
│  ● Server Online             │
├──────────────────────────────┤
│                              │
│  [🎤 Open Voice Mode (Tab)]  │
│                              │
│  [📱 Open Voice Mode (Popup)]│
│                              │
│  [📊 View All Answers]       │
│                              │
│  Keyboard Shortcuts          │
│  Voice Mode (Tab)   Ctrl+V   │
│  Voice Mode (Popup) Ctrl+A   │
│                              │
│  💡 Pro Tip:                 │
│  Use popup mode during       │
│  interviews!                 │
└──────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Extension Not Working?

**Problem:** "Server Offline" in popup
**Solution:**
```bash
cd ~/InterviewVoiceAssistant
python3 web/server.py
# Wait 2-3 seconds, popup dot turns green
```

**Problem:** Keyboard shortcuts don't work
**Solution:**
1. Go to `chrome://extensions/shortcuts`
2. Scroll to "Interview Voice Assistant"
3. Verify shortcuts are set:
   - Open voice mode: `Ctrl+Shift+V`
   - Open popup: `Ctrl+Shift+A`
4. Change if conflicts exist

**Problem:** Extension icon not visible
**Solution:**
1. Click puzzle icon 🧩 in Chrome
2. Pin "Interview Voice Assistant"

**Problem:** Popup appears in wrong position
**Solution:**
- Extension positions it at right edge
- Adjust your screen layout
- Or use tab mode instead

---

## 🎓 Interview Best Practices

### ✅ DO:
- Test everything 5 minutes before interview
- Use popup mode for discretion
- Have voice assistant ready but hidden
- Speak clearly into mic when recording
- Review transcription before sending
- Keep answers brief and natural

### ❌ DON'T:
- Don't test during interview introduction
- Don't have voice window visible on screen share
- Don't rely 100% on answers (understand them!)
- Don't record interviewer's audio
- Don't panic if server goes down (have backup)

---

## 📊 Quick Reference Card

### Interview Checklist

**Before Interview:**
- [ ] Server running: `python3 web/server.py`
- [ ] Extension installed and pinned
- [ ] Test shortcut: Ctrl+Shift+A works
- [ ] Test recording: Hold SPACE, say "test"
- [ ] Test answer: Verify response appears
- [ ] Position popup window (if using)

**During Interview:**
- [ ] Popup/tab ready but minimized
- [ ] When question asked:
  - [ ] Ctrl+Shift+A (if closed)
  - [ ] Hold SPACE
  - [ ] Speak question clearly
  - [ ] Release SPACE
  - [ ] Edit transcription if needed
  - [ ] Send question
  - [ ] Answer verbally from screen

**After Each Question:**
- [ ] Minimize voice window (Ctrl+W or minimize button)
- [ ] Focus back on interview

---

## 🆚 Extension vs Manual URL

| Method | Speed | Convenience | During Interview |
|--------|-------|-------------|------------------|
| **Extension (Ctrl+Shift+A)** | ⚡ Instant | ✅ One key | ✅ Perfect |
| Type URL manually | Slow | ❌ Multi-step | ❌ Awkward |

**Winner: Extension** 🏆

---

## 🔮 Advanced Usage

### Custom Shortcut Keys

Don't like Ctrl+Shift+A?

1. `chrome://extensions/shortcuts`
2. Click "Interview Voice Assistant"
3. Click in shortcut field
4. Press your preferred keys
5. Save

Suggestions:
- `Alt+V` (if available)
- `Ctrl+Q` (quick access)
- `F12` (dedicated function key)

### Multiple Instances

Want voice assistant on 2 screens?
- Use extension to open tab mode on monitor 1
- Manually open popup on monitor 2
- Both connect to same server
- All answers appear in both!

---

## 📞 Support

**Extension not in toolbar?**
- Click puzzle icon 🧩, pin it

**Shortcuts not working?**
- Check chrome://extensions/shortcuts
- Resolve conflicts
- Restart Chrome

**Server offline?**
- Start: `python3 web/server.py`
- Check port 8000 not in use
- Wait 3-5 seconds for startup

**Need help?**
- See: [VOICE_MODE_GUIDE.md](./VOICE_MODE_GUIDE.md)
- See: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

**Master the shortcuts, ace the interview! 🚀**
