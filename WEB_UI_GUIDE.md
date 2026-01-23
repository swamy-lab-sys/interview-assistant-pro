# Mobile Web UI - Quick Guide

## Overview
The Interview Voice Assistant now includes a **local, read-only, mobile-friendly web UI** that displays interview answers cleanly on your phone browser.

## Features
- ✅ Runs automatically when you start the app
- ✅ Mobile-optimized clean view
- ✅ Auto-refreshes every 1.5 seconds
- ✅ No authentication needed (local network only)
- ✅ Works completely offline
- ✅ Fails gracefully if port is busy

## How to Use

### 1. Start the Interview Assistant
```bash
python3 main.py voice
# or
python3 main.py text
```

The web UI starts automatically in the background.

### 2. Find Your Laptop's IP Address
```bash
# On Linux
hostname -I | awk '{print $1}'

# Or
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### 3. Open on Your Phone
1. Make sure your phone is on the **same WiFi network** as your laptop
2. Open your phone's browser (Safari, Chrome, etc.)
3. Navigate to: `http://<laptop-ip>:8080`
   - Example: `http://192.168.1.100:8080`

### 4. View Answers
- Questions and answers appear automatically
- Page refreshes every 1.5 seconds
- Most recent answer is highlighted in yellow
- Clean, readable typography

## Architecture

### Files Changed
1. **`web_ui.py`** (NEW)
   - Flask web server
   - HTML template with inline CSS
   - Log file parser
   - Background thread management

2. **`main.py`** (MODIFIED)
   - Added `import web_ui`
   - Added `web_ui.start_web_ui()` call in `voice_mode()` and `text_mode()`

### How It Works
1. Web server runs in a background daemon thread
2. Reads from `~/.interview_assistant/answers.log`
3. Parses Q&A pairs from the log file
4. Serves mobile-friendly HTML page
5. Auto-refresh via meta tag (no JavaScript needed)

### Safety Features
- **Non-blocking**: Runs in background thread, doesn't affect CLI
- **Graceful failure**: If port 8080 is busy, logs warning and continues
- **No crash risk**: Exceptions are caught and logged
- **Clean terminal**: No verbose output unless `VERBOSE=1` is set

## Troubleshooting

### Port 8080 Already in Use
If you see: `⚠️  Web UI: Port 8080 is busy, continuing without web UI`

**Solution**: Stop the process using port 8080 or change the port in `web_ui.py`:
```python
WEB_PORT = 8081  # Change to any available port
```

### Can't Access from Phone
**Check**:
1. Phone and laptop are on the same WiFi network
2. Laptop firewall allows incoming connections on port 8080
3. Using correct IP address (not 127.0.0.1 or localhost)

**Allow firewall (if needed)**:
```bash
sudo ufw allow 8080/tcp
```

### Page Not Updating
- The page auto-refreshes every 1.5 seconds
- If stuck, manually refresh the page
- Check that answers are being written to `~/.interview_assistant/answers.log`

## Technical Details

### Port
- Default: `8080`
- Configurable in `web_ui.py`

### Log File
- Location: `~/.interview_assistant/answers.log`
- Format: Append-only text file
- Managed by `output_manager.py`

### Dependencies
- Flask (already in `requirements.txt`)
- No additional packages needed

### Performance
- Minimal overhead (background thread)
- No database queries
- Simple file parsing
- Lightweight HTML/CSS

## Security Notes

⚠️ **IMPORTANT**: This web UI is designed for **local network use only**

- No authentication
- No HTTPS
- No input validation (read-only)
- Should NOT be exposed to the internet
- Safe for local WiFi during interviews

## Example Use Case

**Scenario**: Phone interview via Zoom on laptop

1. Start the app on laptop: `python3 main.py voice`
2. Open web UI on phone: `http://192.168.1.100:8080`
3. Place phone on desk in view
4. Interviewer asks questions via Zoom
5. Answers appear on phone screen automatically
6. Read answers naturally while maintaining eye contact with camera

## Disabling Web UI

If you don't want the web UI, simply comment out the startup call in `main.py`:

```python
# web_ui.start_web_ui()  # Disabled
```

The CLI will work exactly as before.
