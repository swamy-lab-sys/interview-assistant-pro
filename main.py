#!/usr/bin/env python3
"""
Interview Voice Assistant - Production Pipeline

INTERVIEW-ONLY MODE for real interviews (YouTube/Zoom/Meet/Teams).

DESIGN PRINCIPLES:
1. NEVER block or modify system microphone
2. Accept any system playback audio
3. Hard question boundaries (no overlap)
4. Fast responses (< 4s target)
5. Graceful degradation on all errors
6. Silence > wrong answer

PIPELINE ORDER:
Audio -> VAD -> ASR -> Validate -> LOCK -> Answer -> UI -> UNLOCK -> Cooldown
"""

import os
import sys
import time
import signal
import subprocess
import warnings

# Suppress all warnings for pure output
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

import state
from state import PipelineState
import config
import answer_cache
from llm_client import (
    get_interview_answer,
    get_coding_answer,
    get_streaming_interview_answer,
    clear_session,
    humanize_response,
)
from resume_loader import load_resume, load_job_description
import audio_listener
from audio_listener import (
    record_until_silence,
    select_audio_device_interactive,
)
from stt import transcribe, load_model as load_stt_model
import output_manager
import answer_storage
import fragment_context
from question_validator import clean_and_validate, is_code_request, split_merged_questions, _is_whisper_hallucination
import performance_logger
import threading
import queue

# Debug logging
import debug_logger as dlog

# Thread-safe queue for audio segments
audio_queue = queue.Queue()


# =============================================================================
# CONFIGURATION (Synced with config.py)
# =============================================================================

MAX_QUESTION_DURATION = config.MAX_RECORDING_DURATION
MIN_AUDIO_DURATION = config.MIN_AUDIO_LENGTH
VAD_AGGRESSIVENESS = config.VAD_AGGRESSIVENESS


# =============================================================================
# GLOBAL STATE
# =============================================================================

resume = ""
job_description = ""
should_exit = False


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global should_exit
    # print("\n\nShutting down...")
    should_exit = True
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# =============================================================================
# RESUME LOADING
# =============================================================================

_last_resume_check = 0
_UPLOADED_RESUME_PATH = os.path.expanduser("~/.interview_assistant/uploaded_resume.txt")

def load_resume_context():
    """Load resume ONLY if uploaded via UI. Never load built-in resume.txt."""
    global resume, _last_resume_check
    now = time.time()
    if resume and now - _last_resume_check < _CONTEXT_CHECK_INTERVAL:
        return True
    _last_resume_check = now
    try:
        if os.path.exists(_UPLOADED_RESUME_PATH):
            resume = load_resume(_UPLOADED_RESUME_PATH)
            return bool(resume.strip())
        resume = ""
        return False
    except Exception:
        resume = ""
        return False


_jd_mtime = 0
_last_context_check = 0
_CONTEXT_CHECK_INTERVAL = 30.0  # Only check file changes every 30s

def load_jd_context():
    """Load job description from file (cached, checks mtime at most every 30s)."""
    global job_description, _jd_mtime, _last_context_check
    now = time.time()
    if now - _last_context_check < _CONTEXT_CHECK_INTERVAL:
        return bool(job_description)
    _last_context_check = now
    try:
        jd_path = config.JD_PATH
        if os.path.exists(jd_path):
            mtime = os.path.getmtime(jd_path)
            if mtime != _jd_mtime:
                with open(jd_path, 'r') as f:
                    job_description = f.read()
                _jd_mtime = mtime
            return True
    except Exception:
        pass
    return False


# =============================================================================
# QUESTION HANDLER (SINGLE-SHOT MODE)
# =============================================================================

def handle_question(question_text: str) -> bool:
    """
    Process a validated interview question.

    PIPELINE:
    1. FIRST GATE: Check if blocked
    2. Check cache
    3. Acquire lock (LOGGING ONLY AFTER LOCK)
    4. Generate answer (single-shot, 10s timeout)
    5. Cache + UI update
    6. Release lock + adaptive cooldown

    Returns:
        bool: True if answered
    """
    dlog.start_request()
    dlog.log(f"Processing question: {question_text}", "INFO")

    # Dynamic context reload
    load_jd_context()
    load_resume_context()

    # Step 1: FIRST GATE - check before any work
    if state.should_block_input():
        dlog.log("Blocked by state gate", "WARN")
        return False

    answer = ""
    wants_code = False

    # Step 2: Check cache
    cache_start = time.time()
    cached_answer = answer_cache.get_cached_answer(question_text)
    cache_time = time.time() - cache_start

    if cached_answer is not None:
        dlog.log_cache_hit(question_text)
        dlog.log_timing("cache_lookup", cache_time, "HIT")

        if state.should_block_input():
            return False

        state.start_generation()
        try:
            state.mark_llm_start()
            state.mark_llm_end()

            ui_start = time.time()
            state.mark_ui_start()
            output_manager.write_header(question_text)
            output_manager.write_answer_chunk(cached_answer)
            output_manager.write_footer()
            state.mark_ui_end()
            dlog.log_ui_update(time.time() - ui_start, "cached_answer")

            metrics = state.finalize_metrics()
            answer_storage.set_complete_answer(question_text, cached_answer, metrics)

            answer = cached_answer
            dlog.end_request(question_text, len(answer))
            return True
        finally:
            # ALWAYS release lock
            state.stop_generation()
            state.start_cooldown(answer_length=len(answer), is_code='```' in answer)
            state.set_last_question(question_text)

    # Step 3: Acquire lock FIRST
    dlog.log_cache_miss(question_text)
    dlog.log_timing("cache_lookup", cache_time, "MISS")

    if state.should_block_input():
        dlog.log("Blocked by state gate (after cache)", "WARN")
        return False

    state.start_generation()
    dlog.log_state_change("IDLE", "GENERATING")

    try:
        output_manager.write_header(question_text)

        wants_code = is_code_request(question_text)
        dlog.log(f"Code request: {wants_code}", "DEBUG")

        # Notify UI we are processing (Thinking state)
        answer_storage.set_processing_question(question_text)

        # Step 4: Generate answer (SINGLE-SHOT, 10s timeout handled by llm_client)
        state.mark_llm_start()
        llm_start = time.time()
        dlog.log_llm_start(question_text)

        if wants_code:
            # Coding questions: single-shot for clean code blocks
            dlog.log("Using single-shot mode for code", "DEBUG")
            answer = get_coding_answer(question_text)
            llm_time = (time.time() - llm_start) * 1000
            print(f"[PERF] LLM Generation (Code): {llm_time:.0f}ms")

            answer_storage.set_complete_answer(question_text, answer, None)
            output_manager.write_answer_chunk(answer)
            dlog.log_llm_complete(time.time() - llm_start, len(answer), False)
        else:
            # Interview answers: single-shot so humanize runs BEFORE UI display
            dlog.log("Using single-shot mode for interview", "DEBUG")
            state.mark_ui_start()
            answer = get_interview_answer(question_text, resume, job_description, include_code=False)
            llm_time = (time.time() - llm_start) * 1000
            print(f"[PERF] LLM Generation: {llm_time:.0f}ms")
            output_manager.write_answer_chunk(answer)
            dlog.log_llm_complete(time.time() - llm_start, len(answer), False)

        state.mark_llm_end()

        # Step 5: Cache answer
        answer_cache.cache_answer(question_text, answer)
        dlog.log("Answer cached", "DEBUG")

        # Step 6: Finalize UI
        ui_start = time.time()
        output_manager.write_footer()
        state.mark_ui_end()

        metrics = state.finalize_metrics()
        answer_storage.set_complete_answer(question_text, answer, metrics)
        dlog.log_ui_update(time.time() - ui_start, "finalize")

        # Log performance
        if metrics:
            perf_summary = performance_logger.get_console_summary(metrics)
            dlog.log(f"Performance: {perf_summary}", "INFO")
            print(f"{perf_summary}")

        dlog.end_request(question_text, len(answer))
        return True

    except KeyboardInterrupt:
        raise
    except Exception as e:
        dlog.log_error(f"Answer generation failed", e)
        import traceback
        traceback.print_exc()
        return False
    finally:
        # ALWAYS release lock and start cooldown
        state.stop_generation()
        dlog.log_state_change("GENERATING", "COOLDOWN")
        state.start_cooldown(answer_length=len(answer), is_code=wants_code or '```' in answer)
        state.set_last_question(question_text)


# =============================================================================
# AUDIO CAPTURE + TRANSCRIPTION
# =============================================================================

def capture_worker():
    """
    Producer thread: Continuously captures audio and puts it in the queue.
    This ensures we NEVER miss a question while processing the previous one.
    """
    from professional_audio import capture_question
    print("\n--- Audio Capture Thread Started ---")
    dlog.log("Audio capture worker started", "INFO")

    while not should_exit:
        try:
            # Capture using professional engine
            capture_start = time.time()
            audio = capture_question(
                max_duration=config.MAX_RECORDING_DURATION,
                silence_duration=config.SILENCE_DEFAULT,  # Used config for better pause handling
                verbose=False
            )
            capture_time = time.time() - capture_start

            if audio is not None and len(audio) >= int(16000 * MIN_AUDIO_DURATION):
                audio_length = len(audio) / 16000  # seconds
                dlog.log_audio_capture(capture_time, audio_length, len(audio))
                audio_queue.put(audio)
                dlog.log_queue_status(audio_queue.qsize(), "audio_added")

            # Small breath to avoid CPU spin if capture fails immediately
            time.sleep(0.1)

        except Exception as e:
            dlog.log_error("Capture worker error", e)
            time.sleep(1)

def processing_worker():
    """
    Consumer thread: Processes captured audio segments sequentially.
    """
    print("\n--- Processing Worker Started ---")
    dlog.log("Processing worker started", "INFO")

    # Smart Buffer State
    partial_transcription = ""
    last_partial_time = 0

    while not should_exit:
        try:
            # Get next audio segment
            try:
                audio = audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            dlog.log_queue_status(audio_queue.qsize(), "processing_audio")

            # 1. Transcribe
            stt_start = time.time()
            state.mark_transcription_start()
            transcription, score = transcribe(audio)
            transcription = transcription.strip()
            state.mark_transcription_end()
            stt_time = time.time() - stt_start

            if not transcription or len(transcription) < 5:
                # Log even short transcriptions for debugging
                if config.VERBOSE:
                     print(f"[PERF] Transcribe: {stt_time*1000:.0f}ms | Confidence: {score:.2f} | Text: '{transcription}'")
                dlog.log(f"Transcription too short: '{transcription}'", "DEBUG")
                audio_queue.task_done()
                continue

            # Log significant performance metrics
            print(f"\n[PERF] Transcribe: {stt_time*1000:.0f}ms | Confidence: {score:.2f}")
            if config.VERBOSE:
                 print(f"[TEXT] '{transcription}'")

            # 2. Confidence Filter
            if score < 0.25:
                dlog.log(f"Low confidence ({score:.2f}), skipping", "DEBUG")
                audio_queue.task_done()
                continue

            # 2b. EARLY HALLUCINATION CHECK - Reject Whisper hallucinations immediately
            if _is_whisper_hallucination(transcription):
                if config.VERBOSE:
                    print(f"[HALLUCINATION] Rejected: '{transcription[:50]}...'")
                dlog.log(f"Hallucination rejected: '{transcription[:50]}'", "DEBUG")
                audio_queue.task_done()
                continue

            # 3. Smart Validation & Aggregation
            state.mark_validation_start()

            # Logic: Always buffer deeply until a distinct "gap" of silence is detected
            # or the combined buffer forms a very strong complete question.

            # 1. Add current chunk to buffer
            if config.VERBOSE:
                print(f"[SMART] Received chunk: '{transcription}'")

            # Simple list-based buffer to ensure clean joining
            if not hasattr(processing_worker, "text_buffer"):
                processing_worker.text_buffer = []

            processing_worker.text_buffer.append(transcription)
            last_partial_time = time.time()
            dlog.log(f"Buffer now has {len(processing_worker.text_buffer)} chunks", "DEBUG")

            # 2. FAST PATH: If transcription ends with ? or . it's likely complete
            current_text = " ".join(processing_worker.text_buffer).strip()
            is_complete_sentence = current_text.endswith('?') or (
                current_text.endswith('.') and len(current_text.split()) >= 4
            )

            # 2b. WAIT: Check if more audio is coming (but shorter wait for complete sentences)
            wait_start = time.time()
            AGGREGATION_WINDOW = 0.05 if is_complete_sentence else 0.15  # EXTREME SPEED

            more_chunks_arrived = False
            while (time.time() - wait_start) < AGGREGATION_WINDOW:
                if not audio_queue.empty():
                    more_chunks_arrived = True
                    break
                time.sleep(0.05)  # Reduced from 0.1s

            if more_chunks_arrived:
                dlog.log("More chunks arriving, continuing to buffer", "DEBUG")
                # Loop back to grab the next chunk and combine it
                state.mark_validation_end()
                audio_queue.task_done()
                continue

            # 3. Time's up! Process what we have.
            full_text = current_text
            buffer_wait_time = time.time() - wait_start

            if config.VERBOSE:
                print(f"[SMART] Finalizing buffer: '{full_text}'")

            dlog.log(f"Buffer finalized after {buffer_wait_time*1000:.0f}ms wait: '{full_text}'", "DEBUG")

            # Reset buffer
            processing_worker.text_buffer = []

            # SPLIT MERGED QUESTIONS: Extract the best question if multiple are merged
            original_text = full_text
            full_text = split_merged_questions(full_text)
            if full_text != original_text:
                if config.VERBOSE:
                    print(f"[SMART] Extracted question: '{full_text}'")
                dlog.log(f"Split merged: '{original_text}' -> '{full_text}'", "DEBUG")

            # FRAGMENT MERGING: Merge with recent chat/voice context
            merged_text, was_merged = fragment_context.merge_with_context(full_text)
            if was_merged:
                dlog.log(f"Fragment merged: '{full_text}' -> '{merged_text}'", "INFO")
                if config.VERBOSE:
                    print(f"[MERGE] '{full_text}' + context -> '{merged_text}'")
                full_text = merged_text

            # Validate the COMBINED text
            validate_start = time.time()
            is_valid, cleaned, reason = clean_and_validate(full_text)
            validate_time = time.time() - validate_start
            state.mark_validation_end()

            dlog.log_validation(validate_time, is_valid, reason, cleaned)

            if not is_valid:
                if config.VERBOSE:
                    print(f"[DEBUG] Validation rejected: '{cleaned}' ({reason})")
                audio_queue.task_done()
                continue

            validated = cleaned

            # 4. Action Gate (Concurrency Protection)
            # While we captured the audio concurrently, we process the LLM answer
            # one at a time to keep the UI clean.
            gate_start = time.time()
            while state.should_block_input() and not should_exit:
                time.sleep(0.05)  # Reduced from 0.5s for faster unlocking
            gate_wait = time.time() - gate_start

            if gate_wait > 0.1:
                dlog.log(f"Waited {gate_wait*1000:.0f}ms at action gate", "DEBUG")

            if should_exit:
                audio_queue.task_done()
                break

            # 5. Process
            dlog.log(f"Passing to handle_question: '{validated}'", "INFO")
            answer_storage.set_processing_question(validated)
            handle_question(validated)

            # 6. Save context for cross-source fragment merging
            fragment_context.save_context(validated, "voice")

            audio_queue.task_done()

        except Exception as e:
            dlog.log_error("Processing worker error", e)
            time.sleep(1)


# =============================================================================
# MAIN INTERVIEW LOOP
# =============================================================================

def start_concurrent_pipeline():
    """Starts the producer and consumer threads."""
    producer = threading.Thread(target=capture_worker, daemon=True)
    consumer = threading.Thread(target=processing_worker, daemon=True)
    
    producer.start()
    consumer.start()
    
    # Keep main thread alive
    while not should_exit:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break


# =============================================================================
# STARTUP
# =============================================================================

def start(boot_start_time: float = None):
    """
    Production startup.

    ALWAYS SUCCEEDS - never crashes due to audio/device issues.
    """
    print("\n" + "=" * 60)
    print("INTERVIEW VOICE ASSISTANT")
    print("=" * 60)
    print(f"  STT Model: {config.STT_MODEL}")
    print(f"  LLM Model: {os.environ.get('LLM_MODEL_OVERRIDE', config.LLM_MODEL)}")

    # Clear runtime state (locks, cooldowns, etc.)
    state.force_clear_all()
    answer_cache.clear_cache()
    fragment_context.clear_context()
    dlog.clear_logs()

    # Clear all previous Q&A data for fresh interview
    # (run.sh already deletes files, this ensures in-memory is also clear)
    answer_storage.clear_all(force_clear=True)
    print("✓ Fresh interview session started")

    # Log startup (to file only)
    dlog.log("=" * 60, "INFO")
    dlog.log("INTERVIEW VOICE ASSISTANT STARTING", "INFO")
    dlog.log(f"Log files: {dlog.get_log_paths()}", "INFO")

    # Start Web UI (Silent)
    try:
        subprocess.run(["fuser", "-k", "8000/tcp"], capture_output=True, timeout=2)
        subprocess.Popen(
            [sys.executable, "web/server.py"],
            start_new_session=True
        )
        print("✓ Web UI: http://localhost:8000")
    except Exception:
        pass

    # Pre-load STT
    print("Loading models...")
    import stt
    import numpy as np
    stt.transcribe(np.zeros(16000, dtype=np.float32))
    print("✓ System Ready")

    output_manager.clear_answer_buffer()

    # Print log file locations
    log_paths = dlog.get_log_paths()
    print(f"✓ Logs: {log_paths['debug']}")

    print("\nListening for system audio...")
    dlog.log("System ready, listening for audio", "INFO")

    # Start Concurrent Pipeline
    start_concurrent_pipeline()


def main():
    """Main entry point - silent startup."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    # Resume only loaded if uploaded via UI (not built-in resume.txt)
    load_resume_context()
    if resume:
        print(f"✓ Resume loaded ({len(resume)} chars)")
    else:
        print("  No resume uploaded (upload via UI if needed)")

    # Load job description
    global job_description
    try:
        job_description = load_job_description(config.JD_PATH)
        if job_description.strip():
            print(f"✓ Job Description loaded ({len(job_description)} chars)")
    except:
        pass
    
    start()


if __name__ == "__main__":
    main()
