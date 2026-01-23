# Quick Start Guide

## 5-Minute Setup

### 1. Run Setup
```bash
./setup.sh
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```
Get your key: https://console.anthropic.com/

### 3. Update Resume
```bash
nano resume.txt
```
Add your actual experience, projects, and skills.

### 4. Calibrate Speaker Detection
```bash
python main.py calibrate
```
Follow prompts to record your voice and interviewer voice.

### 5. Test It
```bash
# Test with keyboard first
python main.py text

# Try a question
INTERVIEWER: Tell me about your Python experience
```

### 6. Go Live
```bash
# Start interview mode
python main.py voice
```

## That's It!

The system will:
1. Listen for interviewer questions
2. Ignore your voice
3. Transcribe questions
4. Generate answers
5. Display on screen

## Tips

✅ **Position laptop** to capture both voices
✅ **Read naturally** - don't be robotic
✅ **Paraphrase** answers in your own words
✅ **Maintain eye contact** with camera
✅ **Practice first** in text mode

## iPhone Setup (Optional)

If you want answers on iPhone:

1. Enable SSH on laptop
2. Install Termius on iPhone
3. Connect via SSH: `ssh user@laptop-ip`
4. Run: `python main.py voice`
5. Place iPhone out of camera view

See README.md for detailed iPhone setup.

## Troubleshooting

**Not detecting interviewer?**
```bash
python main.py calibrate
```

**Transcription wrong?**
Edit `config.py` and set `STT_MODEL_SIZE = "small"`

**Slow responses?**
Install GPU-enabled PyTorch for 4x speed boost

**API key error?**
```bash
export ANTHROPIC_API_KEY="your-key"
```

## Ready for Interview?

Checklist:
- [ ] Calibration done
- [ ] Tested in text mode
- [ ] Tested in voice mode
- [ ] Resume updated
- [ ] Laptop positioned
- [ ] API key works
- [ ] Charged devices

**You're ready! Good luck! 🚀**

---

Full documentation: [README.md](README.md)
