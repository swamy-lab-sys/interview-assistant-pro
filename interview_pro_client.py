#!/usr/bin/env python3
"""
Interview Assistant Pro - Local Client
Captures audio, transcribes with Whisper, gets answers from SaaS API
"""

import os
import sys
import threading
import queue
import time
import httpx
import numpy as np

# Configuration
API_URL = os.environ.get("IVA_API_URL", "https://interview-assistant-api-pro.onrender.com")
API_KEY = os.environ.get("IVA_API_KEY", "")

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.5  # seconds

# State
audio_queue = queue.Queue()
is_running = True
current_answer = ""


def get_api_key():
    """Get API key from environment or prompt user"""
    global API_KEY
    if API_KEY:
        return API_KEY

    # Check config file
    config_path = os.path.expanduser("~/.interview_assistant_pro/api_key")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            API_KEY = f.read().strip()
            return API_KEY

    # Prompt user
    print("\n" + "="*60)
    print("  INTERVIEW ASSISTANT PRO - SETUP")
    print("="*60)
    print("\nYou need an API key to use this client.")
    print("Get one at: https://interview-assistant-api-pro.onrender.com/register")
    print()
    API_KEY = input("Enter your API key (iva_...): ").strip()

    # Save for future use
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        f.write(API_KEY)

    return API_KEY


def ask_question(question: str, is_coding: bool = False) -> str:
    """Send question to SaaS API and get answer"""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{API_URL}/api/ask",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "question": question,
                    "is_coding": is_coding
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data["answer"]
            elif response.status_code == 429:
                return "[LIMIT REACHED] Monthly question limit reached. Upgrade to Pro!"
            else:
                return f"[ERROR] {response.text}"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def display_answer(answer: str):
    """Display answer in a clear format"""
    print("\n" + "="*60)
    print("  SUGGESTED ANSWER")
    print("="*60)
    print()
    print(answer)
    print()
    print("="*60)
    print()


def text_mode():
    """Interactive text mode - type questions manually"""
    print("\n" + "="*60)
    print("  INTERVIEW ASSISTANT PRO - TEXT MODE")
    print("="*60)
    print("\nType interview questions and get AI-powered answers.")
    print("Commands: 'quit' to exit, 'code' prefix for coding questions")
    print()

    while True:
        try:
            question = input("\n❓ Question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! Good luck with your interview!")
                break

            if not question:
                continue

            # Check if coding question
            is_coding = question.lower().startswith('code:')
            if is_coding:
                question = question[5:].strip()

            print("\n⏳ Thinking...")
            answer = ask_question(question, is_coding)
            display_answer(answer)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


def voice_mode():
    """Voice mode - listens to microphone and transcribes"""
    try:
        import sounddevice as sd
        from faster_whisper import WhisperModel
    except ImportError:
        print("\n[ERROR] Voice mode requires additional packages.")
        print("Install them with:")
        print("  pip install sounddevice faster-whisper")
        return

    print("\n" + "="*60)
    print("  INTERVIEW ASSISTANT PRO - VOICE MODE")
    print("="*60)
    print("\nListening to your microphone...")
    print("Speak the interviewer's question, then wait for the answer.")
    print("Press Ctrl+C to exit.")
    print()

    # Load Whisper model
    print("Loading speech recognition model...")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("Ready! Listening...\n")

    audio_buffer = []
    silence_threshold = 0.01
    silence_duration = 0
    max_silence = 1.5  # seconds of silence before processing
    is_speaking = False

    def audio_callback(indata, frames, time_info, status):
        nonlocal audio_buffer, silence_duration, is_speaking

        audio_data = indata[:, 0].copy()
        volume = np.abs(audio_data).mean()

        if volume > silence_threshold:
            is_speaking = True
            silence_duration = 0
            audio_buffer.extend(audio_data)
        elif is_speaking:
            silence_duration += frames / SAMPLE_RATE
            audio_buffer.extend(audio_data)

            if silence_duration >= max_silence and len(audio_buffer) > SAMPLE_RATE:
                # Process the audio
                audio_array = np.array(audio_buffer, dtype=np.float32)
                audio_queue.put(audio_array)
                audio_buffer = []
                is_speaking = False
                silence_duration = 0

    def process_audio():
        while is_running:
            try:
                audio_data = audio_queue.get(timeout=1)

                # Transcribe
                print("🎤 Transcribing...")
                segments, _ = model.transcribe(audio_data, language="en")
                text = " ".join([seg.text for seg in segments]).strip()

                if text and len(text) > 10:
                    print(f"\n📝 Heard: {text}")

                    # Get answer
                    print("⏳ Getting answer...")
                    is_coding = any(word in text.lower() for word in
                                   ['code', 'function', 'algorithm', 'implement', 'write'])
                    answer = ask_question(text, is_coding)
                    display_answer(answer)
                    print("🎤 Listening...\n")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR] {e}")

    # Start processing thread
    process_thread = threading.Thread(target=process_audio, daemon=True)
    process_thread.start()

    # Start audio stream
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=audio_callback,
            blocksize=int(SAMPLE_RATE * CHUNK_DURATION)
        ):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        global is_running
        is_running = False
        print("\n\nStopped listening. Goodbye!")


def main():
    # Get API key
    api_key = get_api_key()
    if not api_key:
        print("No API key provided. Exiting.")
        return

    # Verify API key
    print("\nVerifying API key...")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if response.status_code == 200:
                user = response.json()
                print(f"✓ Logged in as: {user['email']}")
                print(f"  Plan: {user['subscription_tier'].upper()}")
                print(f"  Questions remaining: {user['questions_limit'] - user['questions_this_month']}")
            else:
                print(f"✗ Invalid API key. Please check and try again.")
                return
    except Exception as e:
        print(f"✗ Could not connect to server: {e}")
        return

    # Show menu
    print("\n" + "="*60)
    print("  SELECT MODE")
    print("="*60)
    print("\n  1. Text Mode  - Type questions manually (for testing)")
    print("  2. Voice Mode - Listen to microphone (for interviews)")
    print()

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        voice_mode()
    else:
        text_mode()


if __name__ == "__main__":
    main()
