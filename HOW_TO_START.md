# How to Start Your Interview Voice Assistant

## Quick Fix for "bad marshal data" Error

If you're seeing the error:
```
ValueError: bad marshal data (invalid reference)
```

**Run this command:**
```bash
./fix_python_cache.sh
```

This will:
1. Clean corrupted Python bytecode cache (system-wide)
2. Clean project cache
3. Remove and recreate virtual environment
4. Reinstall all dependencies
5. Verify the installation

---

## Normal Startup (After Fix)

### Option 1: Using run.sh (Recommended)
```bash
./run.sh
```

This automatically:
- Activates virtual environment
- Loads environment variables from `.env`
- Checks for API key
- Starts the interview assistant

### Option 2: Manual Start
```bash
# Activate virtual environment
source venv/bin/activate

# Set API key (if not in .env)
export ANTHROPIC_API_KEY="your-api-key-here"

# Start the application
python main.py
```

---

## First Time Setup

If this is your first time running the project:

```bash
# 1. Run the fix script to ensure clean environment
./fix_python_cache.sh

# 2. Create .env file with your API key
echo 'ANTHROPIC_API_KEY="your-key-here"' > .env

# 3. Update your resume
nano resume.txt

# 4. Start the application
./run.sh
```

---

## What Gets Started

When you run `./run.sh`, the system will:

1. ✅ Load your virtual environment
2. ✅ Check for API key
3. ✅ Start web UI at `http://localhost:8000`
4. ✅ Load AI models
5. ✅ Begin listening for interview questions

You should see:
```
==========================================================
INTERVIEW VOICE ASSISTANT
==========================================================
✓ Web UI: http://localhost:8000
Loading models...
✓ System Ready
✓ Logs: /path/to/debug.log

Listening for system audio...
```

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
# Add to .env file
echo 'ANTHROPIC_API_KEY="your-key"' >> .env

# Or export temporarily
export ANTHROPIC_API_KEY="your-key"
```

### Error: "venv not found"
```bash
# Run the fix script
./fix_python_cache.sh
```

### Error: Import errors or module not found
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Still having issues?
```bash
# Nuclear option - complete reset
./fix_python_cache.sh
```

---

## Stopping the Application

Press `Ctrl+C` to stop gracefully.

---

## Alternative Startup Scripts

Your project has several startup options:

| Script | Purpose |
|--------|---------|
| `./run.sh` | **Main production mode** |
| `./start_voice_mode.sh` | Voice mode with optimizations |
| `./start_fast.sh` | Fast startup (minimal checks) |
| `./clean_ui_start.sh` | Start with clean UI state |
| `./setup.sh` | First-time setup (creates venv, installs deps) |

---

## Next Steps After Starting

1. **Test the system**: The web UI at `http://localhost:8000` shows real-time answers
2. **Speak a question**: The system listens for interviewer questions
3. **View answers**: Answers appear on screen and in the web UI
4. **Check logs**: Debug logs are saved to the logs directory

---

**You're all set! 🚀**
