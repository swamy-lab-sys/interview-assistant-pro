# Voice Mode Improvements - ChatGPT-Style Interface

## Current Issues

From the terminal output, we can identify several problems:

1. **Transcription Errors**:
   - "Double next, and double next" → "Tuple next, and tuple next"
   - "What is the degradation?" (probably mishearing)
   - Random captures: "I don't know if I can", "Also sinu Python"

2. **Always-On Listening**:
   - Captures everything in system audio
   - No control over when to speak
   - Picks up background noise and irrelevant speech

3. **No Visual Feedback**:
   - User doesn't know when system is listening
   - No indication of transcription progress
   - Unclear when processing starts/ends

4. **Poor UX**:
   - Can't cancel mid-capture
   - No way to retry if transcription fails
   - Mixed with random API calls from browser

## Proposed Solution: Push-to-Talk Voice Mode

### Key Features

1. **Push-to-Talk Interface**:
   - Hold SPACEBAR (or click button) to speak
   - Visual feedback when recording
   - Release to process
   - Clear "Listening..." indicator

2. **Better Audio Flow**:
   - Only capture when user activates
   - No background audio bleeding
   - Clear start/end markers
   - Real-time volume indicator

3. **Improved Transcription**:
   - Use better Whisper model (small or medium)
   - Show transcription before processing
   - Allow editing before submitting
   - Confidence score visible

4. **ChatGPT-Style UI**:
   - Conversation view
   - Clear Q&A pairs
   - Voice waveform animation
   - Processing indicators

### Implementation Plan

#### 1. New Voice UI Component (`web/templates/voice.html`)
- Large circular button (like ChatGPT)
- Hold to speak, release to send
- Waveform animation while recording
- Transcription preview
- Edit capability

#### 2. Push-to-Talk Backend (`voice_server.py`)
- WebSocket for real-time audio streaming
- Browser MediaRecorder API
- Send audio chunks to server
- Real-time transcription feedback

#### 3. Improved Audio Pipeline
- Remove always-on capture
- On-demand recording only
- Better noise cancellation
- Confidence thresholds

#### 4. Better STT Configuration
- Upgrade from `base.en` to `small.en` or `medium.en`
- Add language detection
- Post-processing for technical terms
- Context-aware corrections

### User Flow

```
1. User opens http://localhost:8000/voice
2. Sees big microphone button
3. Holds SPACEBAR (or clicks button)
4. Visual feedback: "Listening..." + waveform
5. Speaks question clearly
6. Releases SPACEBAR
7. System transcribes → shows text
8. User can edit or confirm
9. Click "Send" → generates answer
10. Answer appears in chat-style UI
```

### Benefits

✅ **Accuracy**: No background noise, clear start/end
✅ **Control**: User decides when to speak
✅ **Visibility**: Clear feedback at every step
✅ **Reliability**: No random captures, no validation issues
✅ **UX**: Familiar ChatGPT-style interface

## Next Steps

1. Create new voice UI page
2. Add WebSocket support for real-time audio
3. Implement push-to-talk controls
4. Upgrade Whisper model
5. Add transcription editing
6. Test with real interview scenarios
