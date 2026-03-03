# Quick Installation Guide

## Chrome Extension Installation Steps

### 1. Open Chrome Extensions Page
- Open Google Chrome
- Navigate to: `chrome://extensions/`
- Or click: Menu (⋮) → Extensions → Manage Extensions

### 2. Enable Developer Mode
- Look for "Developer mode" toggle in the top-right corner
- Click to enable it

### 3. Load the Extension
- Click "Load unpacked" button
- Navigate to: `/home/venkat/InterviewVoiceAssistant/chrome_extension_programiz/`
- Click "Select Folder"

### 4. Verify Installation
✓ Extension should appear in the list as "Programiz Code Typer"
✓ Icon should be visible in Chrome toolbar
✓ Version: 1.0.0

## Testing the Extension

### 1. Start Backend Server
```bash
cd /home/venkat/InterviewVoiceAssistant
./web_ui_v2_quickstart.sh
```

### 2. Open Programiz
Navigate to: https://www.programiz.com/python-programming/online-compiler

### 3. Test Trigger
- Type `1#` in the editor
- Wait 2-3 seconds
- Code should start typing automatically

### 4. Check Status
- Click extension icon in toolbar
- Verify:
  - Backend: Connected ✓
  - State: Shows current state
  - Codes: Shows number available
  - Polling: Active when typing

## Troubleshooting

### Extension Not Loading
- Make sure you selected the correct folder
- Check that manifest.json exists in the folder
- Look for error messages in red

### Backend Not Connected
- Ensure backend is running on http://localhost:8000
- Check terminal for any errors
- Try restarting the backend

### Code Not Typing
- Click extension icon to check status
- Ensure "Codes" shows a number > 0
- Try refreshing the Programiz page
- Check browser console (F12) for errors

## Uninstallation

1. Go to `chrome://extensions/`
2. Find "Programiz Code Typer"
3. Click "Remove"
4. Confirm removal

## Files Included

```
chrome_extension_programiz/
├── manifest.json       ✓ Extension config
├── background.js       ✓ Service worker
├── content.js          ✓ Main logic
├── page_bridge.js      ✓ Editor access
├── typewriter.js       ✓ Typing engine
├── popup.html          ✓ UI
├── popup.js            ✓ UI logic
├── icons/              ✓ Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md           ✓ Full documentation
```

All files are properly formatted with correct indentation and no unnecessary comments.
