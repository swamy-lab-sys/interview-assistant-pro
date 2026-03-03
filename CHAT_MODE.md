# 💬 Chat-Based Interview Mode

## Overview

The Interview Assistant now supports **chat-based coding questions** from Google Meet, Zoom, and Microsoft Teams. This is additive to existing URL-mode and voice-mode features.

## 🎯 When to Use

Use chat mode when:
- Interviewer posts a coding question in Google Meet/Zoom/Teams chat
- No coding platform URL is provided
- You need to solve the problem and answer verbally or type manually

## 🚀 How It Works

### **Detection**
The extension auto-detects when you're on:
- Google Meet (`meet.google.com`)
- Zoom (`zoom.us`)
- Microsoft Teams (`teams.microsoft.com`)

### **Activation**
1. Interviewer posts question in chat
2. You press `Ctrl + Alt + A` (or click ▶ on localhost:8000)
3. Extension captures the **most recent chat message**
4. Sends to server for solution generation
5. Solution appears **ONLY on http://localhost:8000**

### **IMPORTANT: Chat Mode is ALWAYS View-Only**
- **NEVER types into chat**
- **NEVER types into any editor**
- Solution shows **ONLY on localhost:8000**
- You answer verbally or type manually

## 🎮 Controls (Same as Stealth Mode)

| Shortcut | localhost:8000 UI by viewing the code on your phone or second monitor.

### Manual Typing
```
1. Press Ctrl+Alt+A
2. View solution on localhost:8000 (phone/second screen)
3. Type answer manually while viewing
```

## 🔒 Safety Features

### Auto-Stop Triggers
- Interviewer starts speaking
- New chat message arrives
- Chat panel changes
- Proctoring warning
- Camera/mic/screen share request

### Privacy
- No visible UI on Google Meet/Zoom/Teams
- No scrolling or highlighting in chat
- No selection of messages
- Silent capture (console logs only for debugging)

## 📋 Examples

### Example 1: Google Meet Text Question
```
Interviewer: "Write a function to reverse a linked list"

You:
1. Press Ctrl+Alt+A
2. Check localhost:8000 for solution
3. Answer verbally OR type code manually
```

### Example 2: Zoom Code Challenge
```
Interviewer: "Implement binary search in Python"

You:
1. Press Ctrl+Alt+A
2. View solution on phone (localhost:8000)
3. Explain approach verbally while referring to solution
```

## 🧪 Testing

### Test Chat Capture
1. Start server: `python3 main.py voice`
2. Open Google Meet (or Zoom test page)
3. Send yourself a test message: "Write a function to find fibonacci"
4. Press `Ctrl+Alt+A`
5. Check console (F12): Should see "CHAT MODE: Capturing question..."
6. Check localhost:8000: Solution appears

### Test View-Only Enforcement
- Chat mode should ALWAYS show "VIEW" mode
- Toggling mode (`Ctrl+Alt+M`) should NOT enable typing in chat mode
- Solution should ONLY appear on localhost

## 📊 Status Indicators (localhost:8000)

| Status | Meaning |
|--------|---------|
| `STOPPED` | Idle, waiting for trigger |
| `RUNNING (CHAT)` | Currently solving chat question |
| `PAUSED` | Generation paused |

## 🔧 Troubleshooting

**Chat message not captured?**
- Check if you're on a supported platform (Meet/Zoom/Teams)
- Ensure message is visible in chat panel
- Try pressing `Ctrl+Alt+A` again
- Check console for "No valid chat message found"

**Solution not appearing?**
- Verify server is running (`python3 main.py voice`)
- Check localhost:8000 is accessible
- Look for network errors in browser console

**Chat capture too short?**
- Minimum message length is 10 characters
- Ensure question is complete before capturing

## 🎓 Best Practices

### During Interview
1. **Stay calm**: Wait for full question before capturing
2. **Use second device**: View localhost:8000 on phone/tablet
3. **Manual typing**: Type answer yourself (more natural)
4. **Verbal explanation**: Solution helps you explain approach

### After Capture
- Don't capture again immediately (may duplicate)
- If question changes, use Stop (`Ctrl+Alt+S`) first
- Always verify solution makes sense before answering

## ⚠️ Limitations

- **No multi-message support**: Captures ONLY latest message
- **No code formatting**: Chat text is treated as plain problem statement
- **No editor detection**: If you open a coding platform mid-interview, use URL mode instead
- **View-only enforced**: Cannot be changed to auto-type for chat

## 🔄 Integration with Other Modes

| Scenario | Mode Used | Behavior |
|----------|-----------|----------|
| Chat question on Meet | **CHAT** | View-only, localhost display |
| LeetCode shared link | **URL** | Auto-type or view (your choice) |
| Voice interview | **VOICE** | Full voice assistant features |
| Chat + coding platform open | **URL** | URL mode takes precedence |

## 📖 Key Differences: Chat vs URL Mode

| Feature | Chat Mode | URL Mode |
|---------|-----------|----------|
| **Platform** | Meet/Zoom/Teams | LeetCode/HackerRank/Codewars |
| **Trigger** | `Ctrl+Alt+A` | `Ctrl+Alt+A` |
| **Input** | Chat message | Editor content + DOM problem text |
| **Output** | localhost ONLY | localhost + optional editor typing |
| **Mode Toggle** | Disabled (always VIEW) | Enabled (AUTO/VIEW) |
| **Typing** | NEVER | Optional (if AUTO mode) |

---

**Chat mode is safe, stealth, and completely invisible to interviewers.** 💬🕵️
