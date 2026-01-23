"""
Output Manager for Interview Voice Assistant

Handles console output and log file writing.
"""

import threading
import time
from pathlib import Path

# Configuration
ANSWERS_DIR = Path.home() / ".interview_assistant"
ANSWERS_LOG = ANSWERS_DIR / "answers.log"

_write_lock = threading.Lock()


def ensure_answers_dir():
    """Create answers directory if not exists."""
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)


def write_header(question_text):
    """Write question header to log and console."""
    ensure_answers_dir()

    timestamp = time.strftime("%H:%M:%S")
    header = f"\n{'='*60}\n"
    header += f"TIME: {timestamp}\n"
    header += f"QUESTION: {question_text}\n"
    header += f"{'='*60}\n"

    with _write_lock:
        with open(ANSWERS_LOG, "a", encoding="utf-8") as f:
            f.write(header)
            f.flush()
    
    # Print to console for the user to see what was heard
    print(f"\n[Q] {question_text}")
    print("-" * 30)


def write_answer_chunk(chunk):
    """Write answer text to log and console."""
    with _write_lock:
        with open(ANSWERS_LOG, "a", encoding="utf-8") as f:
            f.write(chunk)
            f.flush()

    # Print only the answer text
    print(chunk, end='', flush=True)


def write_footer():
    """Write answer footer to log only."""
    footer = f"\n{'='*60}\n"

    with _write_lock:
        with open(ANSWERS_LOG, "a", encoding="utf-8") as f:
            f.write(footer)
            f.flush()


def clear_answer_buffer():
    """Clear the answers log file."""
    ensure_answers_dir()
    with _write_lock:
        with open(ANSWERS_LOG, "w", encoding="utf-8") as f:
            f.write(f"# Interview Voice Assistant\n")
            f.write(f"# Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
