# Manual Testing Guide

## Production Safety Verification

This guide provides step-by-step manual testing to verify the InterviewVoiceAssistant captures ONLY system audio and NEVER captures microphone input.

---

## Prerequisites

1. Run automated safety checks:
   ```bash
   ./verify_safety.sh
   ```
   All tests should PASS.

2. Ensure persistence is configured:
   ```bash
   ./setup_persistent_audio.sh
   ```

---

## Test 1: YouTube Audio Triggers Answer

**Purpose:** Verify app responds to system audio playback.

**Steps:**
1. Start the app:
   ```bash
   python3 main.py voice
   ```

2. Select device (usually option `8` for `pulse`).

3. Wait for "🟢 READY FOR INTERVIEW".

4. Open YouTube in browser and play an interview question video:
   - Search: "mock interview questions"
   - Play any question (e.g., "Tell me about yourself")

5. **Expected result:**
   ```
   🎤 Listening...
   Recording... (speak now)
   Recording finished
   📝 Transcribing interviewer question...
   ============================================================
   INTERVIEWER: [transcribed question text]
   ============================================================

   ANSWER:
   [Claude generates answer based on resume]
   ```

6. **PASS criteria:**
   - ✅ YouTube audio is transcribed
   - ✅ App generates an answer
   - ✅ Answer appears in terminal

---

## Test 2: Microphone Does NOT Trigger Answer

**Purpose:** Verify app IGNORES microphone input.

**Steps:**
1. With app still running from Test 1.

2. Speak directly into laptop microphone:
   - Say clearly: "Tell me about your experience"
   - Speak at normal volume

3. **Expected result:**
   ```
   🎤 Listening...
   [No response, continues listening]
   ```

4. **PASS criteria:**
   - ✅ App does NOT transcribe your voice
   - ✅ App does NOT generate an answer
   - ✅ App continues showing "🎤 Listening..."
   - ✅ No transcription appears

---

## Test 3: Zoom/Meet Audio Triggers Answer

**Purpose:** Verify app works during real video call.

**Steps:**
1. Join a Zoom/Google Meet call (can be a test call with friend).

2. Have someone on the call ask you a question.

3. **Expected result:**
   - App captures the remote speaker's voice
   - App transcribes and generates answer
   - YOUR voice (into laptop mic) is NOT captured by app

4. **PASS criteria:**
   - ✅ Remote speaker's question is transcribed
   - ✅ Answer is generated
   - ✅ Your spoken responses are NOT transcribed
   - ✅ Call audio works normally (they can hear you)

---

## Test 4: Silence Guard Works

**Purpose:** Verify retrigger protection.

**Steps:**
1. Play continuous YouTube audio (e.g., interview compilation).

2. After app generates ONE answer, observe behavior.

3. **Expected result:**
   ```
   [Answer completes]
   ⏸️  Waiting for 2.5s silence before next question...

   [If YouTube keeps playing]
   ⏸️  Silence period active (1.8s remaining), ignoring audio...
   ⏸️  Silence period active (0.5s remaining), ignoring audio...
   ✓ Silence period complete, ready for next question
   ```

4. **PASS criteria:**
   - ✅ Only ONE answer per question
   - ✅ Continuous audio doesn't retrigger immediately
   - ✅ Requires 2.5s silence before accepting next question

---

## Test 5: Microphone Still Works for Interview

**Purpose:** Verify microphone is NOT disabled.

**Steps:**
1. Keep app running.

2. Open a Zoom/Meet test call or use `pavucontrol`:
   ```bash
   pavucontrol
   ```
   Go to "Recording" tab.

3. Speak into microphone and observe meters.

4. **Expected result:**
   - Microphone input level shows activity
   - Zoom/Meet receives your audio
   - App does NOT show transcription

5. **PASS criteria:**
   - ✅ Microphone is functional
   - ✅ Zoom/Meet can hear you
   - ✅ App does NOT capture your voice

---

## Test 6: Configuration Persists After Reboot

**Purpose:** Verify routing survives system restart.

**Steps:**
1. Note current configuration:
   ```bash
   pactl get-default-source
   ```
   Should show: `system_audio_capture`

2. Reboot the system:
   ```bash
   sudo reboot
   ```

3. After reboot, check again:
   ```bash
   pactl get-default-source
   ```

4. **Expected result:**
   ```
   system_audio_capture
   ```

5. **PASS criteria:**
   - ✅ Default source is still `system_audio_capture`
   - ✅ Configuration persisted across reboot
   - ✅ App still works correctly after reboot

---

## Troubleshooting

### App captures microphone after reboot

**Problem:** Configuration didn't persist.

**Fix:**
```bash
./setup_persistent_audio.sh
```

### No system audio devices found

**Problem:** PulseAudio monitor not exposed.

**Fix:**
```bash
pactl load-module module-remap-source source_name=system_audio_capture master=@DEFAULT_MONITOR@
pactl set-default-source system_audio_capture
```

### YouTube audio not being captured

**Problem:** Audio might be routed to different output device.

**Check:**
```bash
pactl list sinks short
pactl get-default-sink
```

Make sure YouTube is using the default sink.

---

## Production Readiness Checklist

Before actual interview:

- [ ] All automated tests pass (`./verify_safety.sh`)
- [ ] Test 1 PASSED (YouTube triggers answer)
- [ ] Test 2 PASSED (Microphone ignored)
- [ ] Test 3 PASSED (Zoom/Meet works)
- [ ] Test 4 PASSED (Silence guard works)
- [ ] Test 5 PASSED (Mic functional for interview)
- [ ] Test 6 PASSED (Persists after reboot)
- [ ] Resume.txt is populated with your experience
- [ ] ANTHROPIC_API_KEY is set correctly
- [ ] SSH from mobile works (for viewing answers)
- [ ] Tested complete interview flow end-to-end

---

## Production Usage

**Start interview mode:**
```bash
export ANTHROPIC_API_KEY='your-key-here'
python3 main.py voice
```

**SSH from mobile to view answers:**
```bash
ssh user@laptop-ip
cd InterviewVoiceAssistant
# Terminal shows answers in real-time
```

**During interview:**
- Interviewer speaks → App listens → Generates answer → You read from phone
- You speak → App ignores → Interview continues
- One answer per question (2.5s silence required between questions)

---

## Safety Guarantees

1. **Device-level isolation:** App only accepts 'pulse'/'default' devices, which are verified to route to system audio, not microphone.

2. **Runtime verification:** App checks PulseAudio routing at startup and refuses to run if unsafe.

3. **Name-based filtering:** All hardware microphone devices are blocked by name patterns.

4. **Fail-safe defaults:** If routing cannot be verified, app refuses to run.

5. **Persistent configuration:** Settings survive reboots via PulseAudio config file.

**Bottom line:** The app CANNOT capture microphone input, even if misconfigured. It will simply refuse to run rather than capture mic.
