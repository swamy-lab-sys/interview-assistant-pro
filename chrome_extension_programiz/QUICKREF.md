# Quick Reference Card

## 🚀 Installation (3 Steps)

1. **Chrome Extensions**: `chrome://extensions/` → Enable Developer Mode
2. **Load Extension**: Click "Load unpacked" → Select `chrome_extension_programiz/`
3. **Start Backend**: `cd /home/venkat/InterviewVoiceAssistant && ./web_ui_v2_quickstart.sh`

## 🎯 Usage Commands

| Command | Action |
|---------|--------|
| `1#` | Type code #1 |
| `2#` | Type code #2 |
| `3#` | Type code #3 |
| `##stop` | Abort typing |

## 📊 Status Indicators

Click extension icon to see:

| Indicator | Meaning |
|-----------|---------|
| Backend: **Connected** 🟢 | Backend is running |
| Backend: **Disconnected** 🔴 | Backend is down |
| State: **IDLE** ⚪ | Waiting for trigger |
| State: **ARMED** 🟡 | Requesting code |
| State: **TYPING** 🔵 | Actively typing |
| Codes: **3 ready (1#-3#)** | 3 codes available |
| Polling: **Active** 🟢 | Monitoring for updates |

## ⚡ Speed Settings

| WPM | Speed | Delay/Char |
|-----|-------|------------|
| 5 | Very Slow | 2400ms |
| 10 | Slow | 1200ms |
| 20 | Medium | 600ms |
| 40 | Fast | 300ms |
| 60 | Very Fast | 200ms |

## 🔧 Troubleshooting

### Extension Not Working?
```bash
# Check backend
curl http://localhost:8000/api/code_payloads

# Restart backend
cd /home/venkat/InterviewVoiceAssistant
./web_ui_v2_quickstart.sh

# Reload extension
chrome://extensions/ → Click reload icon
```

### Code Not Typing?
1. Click extension icon
2. Check "Codes" shows > 0
3. Refresh Programiz page
4. Try `1#` again

### Check Console
- Press F12 in Chrome
- Look for `[CodeTyper]` messages
- Check for errors in red

## 📁 File Locations

```
Extension: /home/venkat/InterviewVoiceAssistant/chrome_extension_programiz/
Backend:   /home/venkat/InterviewVoiceAssistant/
Docs:      chrome_extension_programiz/README.md
```

## 🌐 Supported Sites

- https://www.programiz.com/python-programming/online-compiler
- https://www.programiz.com/python-programming/online-compiler/*

## 🎨 Features

✅ Human-like typing with randomization
✅ Auto-detects CodeMirror, Ace, Monaco editors
✅ Auto-clicks Run button after typing
✅ Pauses when you press keys
✅ Adjustable speed (5-60 WPM)
✅ State machine for reliability
✅ Dual-mode editor access (bridge + fallback)

## 📝 API Endpoint

```
GET http://localhost:8000/api/code_payloads

Response:
{
  "codes": [
    {
      "index": 1,
      "code_id": "abc123",
      "language": "python",
      "lines": ["def is_even(num):", "    return num % 2 == 0"],
      "question": "Write a function to find even number",
      "timestamp": "2026-02-03T15:04:45"
    }
  ]
}
```

## 🎯 Workflow

```
1. Start backend (localhost:8000)
2. Open Programiz compiler
3. Type trigger (e.g., 1#)
4. Wait 2-3 seconds
5. Watch code type automatically
6. Code auto-executes
```

## 💡 Tips

- **Speed**: Start with 10 WPM, increase gradually
- **Triggers**: Type trigger and wait, don't delete it
- **Abort**: Use `##stop` to stop typing immediately
- **Status**: Click extension icon to monitor
- **Console**: Keep F12 open to see logs

## 🆘 Support

- Full docs: `README.md`
- Install guide: `INSTALL.md`
- Summary: `SUMMARY.md`
- This card: `QUICKREF.md`
