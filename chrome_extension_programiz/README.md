# Programiz Code Typer - Chrome Extension

A Chrome extension that automatically types code into the Programiz online Python compiler with human-like typing speed and behavior.

## Features

- **Automatic Code Typing**: Types code character-by-character with realistic human-like delays
- **Multiple Editor Support**: Works with CodeMirror 5/6, Ace, Monaco, and textarea editors
- **Adjustable Speed**: Control typing speed from 5 to 60 WPM (words per minute)
- **Smart Trigger System**: Use simple commands like `1#`, `2#` to trigger code typing
- **Auto-Execute**: Automatically clicks the Run button after typing completes
- **State Management**: IDLE → ARMED → TYPING state machine for reliable operation
- **Pause Detection**: Pauses typing when user interacts with the keyboard
- **Bridge Architecture**: Dual-mode access (page context + content script fallback)

## Installation

1. **Download the Extension**
   - The extension files are located in: `/home/venkat/InterviewVoiceAssistant/chrome_extension_programiz/`

2. **Load in Chrome**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)
   - Click "Load unpacked"
   - Select the `chrome_extension_programiz` folder

3. **Verify Installation**
   - You should see "Programiz Code Typer" in your extensions list
   - The extension icon will appear in your Chrome toolbar

## Usage

### Step 1: Start the Backend Server

The extension requires the Interview Assistant backend to be running:

```bash
cd /home/venkat/InterviewVoiceAssistant
python web_ui_v2_quickstart.sh
```

The backend should be running on `http://localhost:8000`

### Step 2: Navigate to Programiz

Open the Programiz Python online compiler:
- https://www.programiz.com/python-programming/online-compiler

### Step 3: Trigger Code Typing

In the Programiz editor, type one of these commands:

- **`1#`** - Types code #1 from your interview session
- **`2#`** - Types code #2 from your interview session
- **`3#`** - Types code #3 from your interview session
- **`##stop`** - Aborts typing immediately

### Step 4: Monitor Status

Click the extension icon to see:
- **Backend**: Connection status to localhost:8000
- **State**: Current state (IDLE/ARMED/TYPING)
- **Codes**: Number of available code snippets
- **Polling**: Whether actively polling for code
- **Speed**: Adjust typing speed (5-60 WPM)

## How It Works

### Architecture

```
┌─────────────────┐
│  Background.js  │ ← Polls /api/code_payloads every 2s
│  (Service       │ ← Caches all available code snippets
│   Worker)       │ ← Routes code to content script
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Content.js    │ ← Detects trigger patterns (1#, 2#, ##stop)
│  (Content       │ ← Manages state machine (IDLE/ARMED/TYPING)
│   Script)       │ ← Coordinates typing via Typewriter class
└────────┬────────┘
         │
         ├──────────────┬─────────────┐
         ▼              ▼             ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Page_bridge  │ │ Typewriter  │ │ Direct DOM   │
│ (Injected)   │ │ (Engine)    │ │ (Fallback)   │
└──────────────┘ └─────────────┘ └──────────────┘
```

### State Machine

1. **IDLE**: Waiting for trigger
2. **ARMED**: Trigger detected, requesting code from backend
3. **TYPING**: Actively typing code into editor

### Typing Algorithm

- **WPM Calculation**: 1 word = 5 characters
- **Character Delay**: `60000ms / (WPM × 5)` with ±25% jitter
- **Line Delay**: 1.5-2.5× character delay
- **Initial Pause**: 1200-1800ms thinking time
- **User Pause**: 2000ms pause when user presses a key

## File Structure

```
chrome_extension_programiz/
├── manifest.json          # Extension configuration
├── background.js          # Service worker (polling & routing)
├── content.js             # Main content script (state machine)
├── page_bridge.js         # Page context injected script
├── typewriter.js          # Typing engine
├── popup.html             # Extension popup UI
├── popup.js               # Popup logic
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md              # This file
```

## Configuration

### Typing Speed

Adjust in the extension popup or programmatically:

- **5 WPM**: Very slow (12 seconds per char)
- **10 WPM**: Slow (1.2 seconds per char) - Default
- **20 WPM**: Medium (600ms per char)
- **40 WPM**: Fast (300ms per char)
- **60 WPM**: Very fast (200ms per char)

### Backend API

The extension expects these endpoints:

- **GET /api/code_payloads**: Returns all available code snippets

Response format:
```json
{
  "codes": [
    {
      "index": 1,
      "code_id": "unique-id",
      "language": "python",
      "lines": ["def is_even(num):", "    return num % 2 == 0"],
      "question": "Write a function to find even number",
      "timestamp": "2026-02-03T15:04:45"
    }
  ]
}
```

## Troubleshooting

### Extension Not Working

1. **Check Backend Connection**
   - Ensure backend is running on `http://localhost:8000`
   - Click extension icon to verify "Backend: Connected"

2. **Check Page Match**
   - Extension only works on `https://www.programiz.com/python-programming/online-compiler/*`
   - Refresh the page after loading the extension

3. **Check Console**
   - Open DevTools (F12)
   - Look for `[CodeTyper]` or `[Bridge]` messages
   - Check for any errors

### Typing Not Starting

1. **Verify Code Available**
   - Click extension icon
   - Check "Codes" shows a number > 0

2. **Try Different Trigger**
   - Type `1#` and wait 2-3 seconds
   - Check console for "Requesting code #1" message

3. **Check State**
   - Extension popup should show state changing: IDLE → ARMED → TYPING

### Editor Not Detected

1. **Check Bridge Status**
   - Console should show "Bridge ready, editor: cm6" (or cm5/ace/monaco/textarea)
   - If "Direct DOM access works", fallback mode is active

2. **Manual Test**
   - Try typing manually in the editor first
   - Refresh the page and wait 3 seconds before triggering

## Development

### Building from Source

All files are already properly formatted with correct indentation.

### Testing

1. Load extension in Chrome
2. Navigate to Programiz
3. Open DevTools console
4. Type `1#` in editor
5. Watch console logs for state transitions

### Debugging

Enable verbose logging:
```javascript
// In content.js, all console.log statements with LOG prefix
// In background.js, all console.log statements with '[CodeTyper BG]' prefix
```

## Security & Privacy

- **No Data Collection**: Extension does not collect or transmit any personal data
- **Local Communication**: Only communicates with localhost:8000
- **Minimal Permissions**: Only requests `activeTab` and `storage` permissions
- **CSP Compliant**: Handles Content Security Policy with fallback mechanisms

## License

Part of the Interview Voice Assistant project.

## Support

For issues or questions, check the main project documentation at:
`/home/venkat/InterviewVoiceAssistant/README.md`
