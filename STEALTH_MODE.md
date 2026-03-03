# 🕵️ Stealth Keyboard Control Mode

## Overview

The Interview Assistant now supports **completely stealth operation** using keyboard shortcuts instead of text triggers. No visible UI elements appear on coding platforms during interviews.

## 🎮 Control Methods

### **1. Keyboard Shortcuts (Primary)**

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl + Alt + A` | **START/RESUME** | Begin code generation or resume from pause |
| `Ctrl + Alt + P` | **PAUSE** | Temporarily stop generation (preserves state) |
| `Ctrl + Alt + S` | **STOP** | Hard kill switch (clears all state) |
| `Ctrl + Alt + M` | **TOGGLE MODE** | Switch between AUTO-TYPE ↔ VIEW-ONLY |

### **2. Localhost UI Controls (Fallback)**

Open `http://localhost:8000` and click the `</>` button (bottom-right) to access:

- ▶ **Start/Resume** button
- ⏸ **Pause** button
- ⛔ **Stop** button
- **AUTO/VIEW** mode toggle button
- Real-time **status** indicator (STOPPED / RUNNING / PAUSED)

## 🔁 Operating Modes

### AUTO-TYPE Mode
- Generated code is **typed into the platform editor**
- Identical code appears on **localhost:8000**
- Use when: You want automated typing assistance

### VIEW-ONLY Mode (Stealth)
- Code is **NEVER typed** into the platform
- Solution appears **ONLY on localhost:8000**
- You manually type by viewing the code on:
  - Your phone
  - Second monitor
  - Laptop beside you
- Use when: Maximum stealth required

## 📋 Usage Workflow

### Quick Start
1. **Open coding platform** (LeetCode, HackerRank, Codewars, etc.)
2. **Read the problem**
3. **Press `Ctrl + Alt + A`** (or click ▶ on localhost)
4. **Watch code appear**:
   - AUTO mode: Types into editor
   - VIEW mode: Shows on localhost only

### Toggle Mode Mid-Session
```
Ctrl + Alt + M → Switch to VIEW-ONLY
Ctrl + Alt + M → Switch back to AUTO-TYPE
```

### Pause/Resume
```
Ctrl + Alt + P → Pause (preserves state)
Ctrl + Alt + A → Resume from where you left off
```

### Emergency Stop
```
Ctrl + Alt + S → Hard stop (kill everything)
```

## 🎯 What Changed

### ❌ REMOVED
- Text triggers (`##start`, `##stop`, `##start`)
- Visible popup dependency
- Text polling system

### ✅ ADDED
- Keyboard shortcuts (Ctrl+Alt+A/P/S/M)
- Localhost control panel
- Mode toggle (Auto-Type / View-Only)
- Real-time status sync

## 🔒 Stealth Features

- **No visible UI** on coding platforms
- **No text commands** in editor
- **No DOM injection** into interview pages
- **Silent operation** (only console logs for debugging)
- **Localhost-only controls** (safe during screen share)

## 🖥️ Localhost Dashboard

### Access
```
http://localhost:8000
```

### Features
- **Code View Panel** (slide-out from right)
- **Control Buttons** (Start/Pause/Stop/Mode)
- **Status Indicator** (STOPPED / RUNNING / PAUSED)
- **Mode Display** (AUTO / VIEW)
- **Live Code Preview** (syntax highlighted)
- **Auto-refresh** every 2 seconds

## 🚨 Auto-Stop Triggers

The system automatically stops if:
- Interviewer voice detected
- Tab/page change
- Proctoring warning
- Camera/mic/screen share request

**Safety first: Silence is always preferred over wrong behavior**

## 🧪 Testing

1. **Start server**:
   ```bash
   python3 main.py voice
   ```

2. **Load extension**:
   - Chrome → Extensions → Reload "Extension Name"

3. **Open http://localhost:8000**:
   - Click `</>` button (bottom-right)
   - See control panel

4. **Go to any coding platform**:
   - Press `F12` → Console
   - Press `Ctrl + Alt + A`
   - Check console for `⚡ Ctrl+Alt+A: START/RESUME`

5. **Watch code appear**:
   - AUTO mode: In editor + localhost
   - VIEW mode: Localhost only

## 📝 Notes

- Keyboard shortcuts work **globally** on coding platforms
- Localhost controls are **safe** during screen sharing
- Mode persists across page reloads
- Code always mirrors to localhost (regardless of mode)

## 🎓 Best Practices

### Before Interview
1. Test keyboard shortcuts on a practice problem
2. Verify localhost:8000 is accessible
3. Choose your default mode (AUTO or VIEW)

### During Interview
1. Keep localhost:8000 open on second device
2. Use keyboard shortcuts (invisible to interviewer)
3. If nervous, switch to VIEW-ONLY mode (`Ctrl+Alt+M`)

### Emergency
```
Ctrl + Alt + S → STOP EVERYTHING
```

## 🔧 Troubleshooting

**Shortcuts not working?**
- Check console (F12) for "keydown" events
- Ensure focus is on the coding platform page

**Localhost not updating?**
- Verify server is running
- Check if polling interval is active (every 2s)

**Mode toggle not reflecting?**
- Server might be offline
- Extension toggles locally as fallback

---

**You're now fully stealth. Happy coding! 🚀**
