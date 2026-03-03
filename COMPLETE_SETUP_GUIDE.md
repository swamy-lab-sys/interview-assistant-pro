# 🚀 Complete Setup Guide - Voice Mode for Interviews

## Quick Installation (5 Minutes)

### Step 1: Install Chrome Extension

1. **Open Chrome** and go to: `chrome://extensions/`

2. **Enable Developer Mode** (toggle in top-right corner)

3. **Load Extension:**
   - Click "Load unpacked"
   - Navigate to: `/home/venkat/InterviewVoiceAssistant/chrome_extension_voice`
   - Click "Select Folder"

4. **Pin Extension:**
   - Click puzzle icon (🧩) in Chrome toolbar
   - Find "Interview Voice Assistant"
   - Click pin icon 📌

5. **Verify:**
   - 🎤 icon should appear in Chrome toolbar
   - Click it to see purple popup with status

✅ Extension installed!

---

### Step 2: Start Server

```bash
cd ~/InterviewVoiceAssistant
python3 web/server.py
```

**You should see:**
```
============================================================
Interview Voice Assistant - Web UI Server
============================================================

Server: http://0.0.0.0:8000
Mobile: http://<your-ip>:8000
```

✅ Server running!

---

### Step 3: Test Voice Mode

#### Option A: Using Extension (Recommended)
1. Press **Ctrl+Shift+A** in Chrome
2. Small popup window opens on right side

#### Option B: Direct URL
1. Open browser
2. Go to: `http://localhost:8000/voice`

**You should see:**
- Green "PUSH-TO-TALK" badge
- Large green microphone button
- "Press and hold to speak" text

✅ Voice mode loaded!

---

### Step 4: Test Recording

1. **Click "Allow"** when browser asks for microphone access

2. **Hold SPACE** (or click the mic button)
   - Button turns red
   - Waveform animation appears
   - Status shows "🔴 Recording..."

3. **Speak clearly:** "What is Python?"

4. **Release SPACE**
   - Status shows "⏳ Transcribing..."
   - Transcription box appears with text

5. **Click "Send Question"**
   - Status shows "🤔 Generating answer..."
   - Answer appears in conversation view

✅ Voice mode working!

---

## 🎯 Interview Mode Setup (Recommended)

### Best Setup for Real Interviews

**Layout:**
```
┌─────────────────────┬──────────────┐
│                     │              │
│   Zoom / Google     │   Voice      │
│   Meet Interview    │   Assistant  │
│                     │   (Popup)    │
│                     │              │
│   [Video Call]      │   🎤         │
│   [Your Face]       │              │
│                     │   [Answer]   │
│                     │              │
└─────────────────────┴──────────────┘
   Left Half (70%)      Right (30%)
```

**Steps:**

1. **Before interview starts:**
   ```bash
   # In terminal:
   cd ~/InterviewVoiceAssistant
   python3 web/server.py &
   ```

2. **Open interview platform:**
   - Join Zoom/Meet call
   - Position window on left 70% of screen

3. **Open voice assistant:**
   - Press **Ctrl+Shift+A** in Chrome
   - Popup appears on right side automatically
   - Resize to comfortable width (500px recommended)

4. **Test everything:**
   - Hold SPACE in voice window
   - Say "test microphone"
   - Verify it transcribes correctly
   - Click Send, verify answer appears

5. **Ready for interview!** ✅

---

## 🎤 During Interview Workflow

### When Interviewer Asks Question

**Example: Technical Question**

```
📞 Interviewer: "Explain the difference between a list and tuple in Python"

Your Actions:
┌──────────────────────────────────────┐
│ 1. Click voice assistant window      │
│ 2. Hold SPACE                        │
│ 3. Say: "Explain list vs tuple"     │
│ 4. Release SPACE                     │
│ 5. Quick review transcription        │
│ 6. Click "Send Question"             │
│ 7. [Answer appears in 2-3 seconds]  │
│ 8. Read answer while explaining      │
│    verbally to interviewer           │
└──────────────────────────────────────┘

Interview continues naturally ✓
```

**Example: Coding Question**

```
📞 Interviewer: "Write a function to reverse a linked list"

Your Actions:
┌──────────────────────────────────────┐
│ 1. Hold SPACE                        │
│ 2. Say: "Reverse a linked list"     │
│ 3. Release, review, send             │
│ 4. [Code solution appears]          │
│ 5. Type code manually                │
│    OR explain approach verbally      │
└──────────────────────────────────────┘

You: "So I'd use three pointers: prev, current, next..."
(reading from answer while coding)
```

---

## ⌨️ Keyboard Shortcuts (Master These!)

| Shortcut | Action | When to Use |
|----------|--------|-------------|
| **Ctrl+Shift+A** | Open popup window | **Start of interview** |
| **SPACE** (hold) | Record audio | **Every question** |
| **Ctrl+Enter** | Send question | After editing transcription |
| **Ctrl+Shift+V** | Open full tab | Practice/testing |
| **Ctrl+W** | Close popup | After answering |

**Muscle Memory Practice:**
```
Before interview, practice 5 times:
1. Ctrl+Shift+A (open)
2. Hold SPACE
3. Say test question
4. Release SPACE
5. Send

Goal: < 5 seconds total
```

---

## 🔍 Extension Features

### Popup Interface

Click the 🎤 icon to see:

```
╔══════════════════════════════╗
║  🎤 Voice Assistant          ║
║  ● Server Online             ║  ← Green = Good!
╠══════════════════════════════╣
║                              ║
║  [🎤 Open Voice Mode (Tab)]  ║
║                              ║
║  [📱 Open Voice Mode (Popup)]║  ← Click this
║                              ║                for interview
║  [📊 View All Answers]       ║
║                              ║
║  Keyboard Shortcuts          ║
║  Voice Mode (Tab)   Ctrl+V   ║
║  Voice Mode (Popup) Ctrl+A   ║  ← Fastest way
║                              ║
║  💡 Pro Tip:                 ║
║  Use popup mode during       ║
║  interviews!                 ║
╚══════════════════════════════╝
```

### Server Status Indicator

- **Green dot** = Server online ✅
- **Red dot** = Server offline ❌ (start it!)
- Auto-refreshes every 3 seconds

---

## 📱 Alternative: Mobile Second Screen

**Don't want popup on main screen?**

1. **Find your IP:**
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. **On your phone/tablet:**
   - Open browser
   - Go to: `http://<your-ip>:8000/voice`
   - (Replace <your-ip> with actual IP, e.g., 192.168.1.100)

3. **During interview:**
   - Phone beside laptop
   - Hold SPACE on laptop (mic)
   - Glance down at phone for answers

**Pros:**
- ✅ Nothing visible on main screen
- ✅ Can't accidentally share in screen share
- ✅ Very discreet

**Cons:**
- ⚠️ Have to look down
- ⚠️ Smaller screen

---

## 🎓 Best Practices

### ✅ DO:

1. **Practice before interview**
   - Test full workflow 3-4 times
   - Get comfortable with shortcuts
   - Verify transcription accuracy

2. **Position windows properly**
   - Interview left, voice assistant right
   - Or use phone as second screen
   - Test visibility and readability

3. **Speak clearly when recording**
   - Close mic to mouth
   - Quiet environment
   - Enunciate technical terms

4. **Review transcriptions**
   - Check for errors before sending
   - Edit if needed
   - Better question = better answer

5. **Keep calm**
   - Have backup plan if tech fails
   - Don't rely 100% on answers
   - Understand the concepts

### ❌ DON'T:

1. **Don't have voice window in screen share**
   - Keep it outside share area
   - Or use phone/second monitor

2. **Don't test during interview intro**
   - Test 5 minutes BEFORE joining
   - Have it ready but hidden

3. **Don't rush**
   - Take natural pauses
   - Don't speak too fast
   - Be deliberate, not suspicious

4. **Don't memorize verbatim**
   - Understand the answer
   - Rephrase in your own words
   - Sound natural

5. **Don't panic if it fails**
   - Have backup knowledge
   - Think through the problem
   - Tech is aid, not crutch

---

## 🔧 Quick Troubleshooting

### Issue: Extension shows "Server Offline"

**Fix:**
```bash
cd ~/InterviewVoiceAssistant
python3 web/server.py
```
Wait 3 seconds, click extension icon again.

---

### Issue: Ctrl+Shift+A doesn't work

**Fix:**
1. `chrome://extensions/shortcuts`
2. Find "Interview Voice Assistant"
3. Set shortcut manually
4. Test again

---

### Issue: Microphone not working

**Fix:**
1. Click padlock icon in address bar
2. Microphone → Allow
3. Refresh page
4. Try again

---

### Issue: Transcription is garbled

**Fix:**
- Speak slower and clearer
- Move closer to mic
- Reduce background noise
- Edit transcription before sending

---

### Issue: Answers take too long

**Check:**
```bash
# Is Anthropic API key set?
echo $ANTHROPIC_API_KEY

# If empty, set it:
export ANTHROPIC_API_KEY="your-key-here"
```

---

## 📊 Success Checklist

Before your interview, verify:

- [ ] ✅ Server running (`python3 web/server.py`)
- [ ] ✅ Extension installed and pinned
- [ ] ✅ Ctrl+Shift+A opens popup
- [ ] ✅ Microphone access allowed
- [ ] ✅ Test recording with SPACE works
- [ ] ✅ Transcription appears correctly
- [ ] ✅ Sending question generates answer
- [ ] ✅ Window positioned properly
- [ ] ✅ Interview platform ready (Zoom/Meet)
- [ ] ✅ Practiced workflow 3+ times

**All checked? You're ready! 🚀**

---

## 💡 Pro Tips for Success

### 1. Two Monitor Advantage
- Monitor 1: Interview (fullscreen)
- Monitor 2: Voice assistant (tab mode)
- Best visibility, no awkward positioning

### 2. The "Thinking Pause"
```
Interviewer asks question
↓
You: "That's a great question. Let me think..."
↓
[Use 5-10 seconds to record/send question]
↓
Answer appears
↓
You: "So here's how I'd approach this..."
```
Natural! No suspicion!

### 3. Answer Quality Check
- Don't just read verbatim
- Scan answer for key points
- Rephrase in your own words
- Add your own examples

### 4. Backup Plan Ready
If tech fails:
- Know fundamentals yourself
- Have notes as fallback
- Think through problem logically
- Don't freeze up

### 5. Practice Smooth Workflow
```
Question → Click → SPACE → Speak → Release → Send
         └────────── < 8 seconds total ───────────┘

Goal: So smooth interviewer doesn't notice
```

---

## 🎬 Final Check

**5 Minutes Before Interview:**

```bash
# Terminal 1: Start server
cd ~/InterviewVoiceAssistant
python3 web/server.py

# Terminal 2: Test everything
./test_voice_setup.sh
```

**In Browser:**
1. Press Ctrl+Shift+A
2. Test: "What is Python?"
3. Verify answer appears
4. Ready!

---

## 📞 Support Resources

- **📘 VOICE_MODE_GUIDE.md** - Detailed usage guide
- **📗 EXTENSION_VOICE_GUIDE.md** - Extension specifics
- **📙 VOICE_MODE_IMPLEMENTATION.md** - Technical details
- **📕 TROUBLESHOOTING.md** - Common issues

---

**You're all set! Good luck with your interviews! 🚀**

*Remember: This is a tool to help you succeed, but understanding the concepts is what really matters. Use it wisely!*
