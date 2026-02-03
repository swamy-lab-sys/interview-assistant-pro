"""
Answer Storage for Interview Voice Assistant

ACCUMULATING ANSWER MODE WITH PERFORMANCE METRICS

Features:
- ALL Q&A answers kept and displayed (no overwriting)
- New answers added to the list (interview history preserved)
- Performance metrics (latency) stored with each answer
- Thread-safe operations
"""

import json
import os
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configuration
ANSWERS_DIR = Path.home() / ".interview_assistant"
CURRENT_ANSWER_FILE = ANSWERS_DIR / "current_answer.json"
HISTORY_FILE = ANSWERS_DIR / "answer_history.jsonl"
MASTER_LOG_FILE = ANSWERS_DIR / "interview_master_log.jsonl"  # Permanent storage

# Thread-safe write lock
_write_lock = threading.Lock()

# All answers for this session (accumulates, never overwrites)
_all_answers: List[Dict[str, Any]] = []

# Duplicate lookup index: lowercase question -> index in _all_answers
_answer_index: Dict[str, int] = {}

# Current answer buffer (the one being streamed right now)
_current_answer: Dict[str, Any] = {
    'question': '',
    'answer': '',
    'timestamp': '',
    'is_complete': False,
    'metrics': None,  # Performance metrics
}

# Directory creation cache - avoid repeated mkdir syscalls
_dir_ensured = False

# Throttled write state for streaming chunks
_last_write_time: float = 0.0
_WRITE_THROTTLE_INTERVAL = 0.15  # Write to disk at most every 150ms during streaming


def ensure_answers_dir():
    """Create answers directory if not exists (cached after first call)."""
    global _dir_ensured
    if not _dir_ensured:
        ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
        _dir_ensured = True


def _write_current(force: bool = False):
    """Write all answers (including current in-progress) to file for web UI.

    Args:
        force: If True, always write immediately (used for complete answers).
               If False, throttle writes to reduce disk I/O during streaming.
    """
    global _last_write_time

    now = time.monotonic()
    if not force and (now - _last_write_time) < _WRITE_THROTTLE_INTERVAL:
        return

    try:
        ensure_answers_dir()
        # Build full list: completed answers + current in-progress answer
        display_list = list(_all_answers)
        # If current answer is being streamed (not yet in _all_answers), add it
        if _current_answer.get('question') and not _current_answer.get('is_complete'):
            display_list.append(_current_answer)
        with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
            json.dump(display_list, f, ensure_ascii=False)
            f.flush()
            if force:
                os.fsync(f.fileno())
        _last_write_time = now
    except Exception:
        pass


def _save_to_history():
    """Append completed answer to history file."""
    try:
        ensure_answers_dir()
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            json.dump(_current_answer, f, ensure_ascii=False)
            f.write('\n')
            f.flush()
    except Exception:
        pass


def _log_permanent(data: Dict[str, Any]):
    """Save to master log (called inline, no thread spawn)."""
    try:
        ensure_answers_dir()
        # Append to master log - NEVER CLEARED
        with open(MASTER_LOG_FILE, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception:
        pass


def clear_all():
    """Clear all stored answers (fresh start)."""
    global _current_answer, _all_answers, _answer_index, _dir_ensured

    _dir_ensured = False
    ensure_answers_dir()

    with _write_lock:
        _current_answer = {
            'question': '',
            'answer': '',
            'timestamp': '',
            'is_complete': False,
            'metrics': None,
        }
        _all_answers = []
        _answer_index = {}

        try:
            with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)

            # Clear history file (Session only)
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()

            # NOTE: We DO NOT clear MASTER_LOG_FILE

        except Exception:
            pass


def set_processing_question(question_text: str):
    """
    Set current question in 'thinking' mode.
    New question starts streaming -- added to the list, not replacing.
    """
    global _current_answer
    with _write_lock:
        _current_answer = {
            'question': question_text.strip(),
            'answer': '',  # Start empty for streaming
            'timestamp': datetime.now().isoformat(),
            'is_complete': False,
            'metrics': None,
        }
        _write_current(force=True)


def append_answer_chunk(chunk: str):
    """Append a chunk of text to the current answer (Streaming).

    Writes are throttled to reduce disk I/O during rapid streaming.
    """
    global _current_answer
    with _write_lock:
        _current_answer['answer'] += chunk
        _write_current(force=False)


def flush_current_to_disk():
    """Force-flush the current in-progress answer to disk.

    Call this after streaming ends to ensure the final state is persisted.
    """
    with _write_lock:
        _write_current(force=True)


def set_complete_answer(
    question_text: str,
    answer_text: str,
    metrics: Optional[Dict[str, int]] = None
):
    """
    Set complete answer with optional metrics.

    ATOMIC OPERATION:
    - Finalizes the current answer
    - Adds it to the accumulated session list
    - Stores performance metrics
    - Single UI update
    - Logs to permanent storage
    """
    global _current_answer, _all_answers

    ensure_answers_dir()

    with _write_lock:
        _current_answer = {
            'question': question_text.strip(),
            'answer': answer_text.strip(),
            'timestamp': datetime.now().isoformat(),
            'is_complete': True,
            'metrics': metrics,
        }
        # O(1) duplicate lookup via index dict
        q_lower = question_text.strip().lower()
        duplicate_idx = _answer_index.get(q_lower)

        if duplicate_idx is not None and duplicate_idx < len(_all_answers):
            # Update existing entry instead of adding duplicate
            _all_answers[duplicate_idx] = _current_answer.copy()
        else:
            # New question -- add to the list and index
            _answer_index[q_lower] = len(_all_answers)
            _all_answers.append(_current_answer.copy())

        _write_current(force=True)
        _save_to_history()

        # Permanent logging inline (cheap append, no thread needed)
        _log_permanent(_current_answer.copy())



def get_current_answer() -> Optional[Dict[str, Any]]:
    """
    Get the current (latest) answer.

    Returns:
        dict with question, answer, timestamp, is_complete, metrics
        or None if no answer
    """
    if _current_answer.get('question'):
        return _current_answer.copy()
    return None


def get_all_answers() -> list:
    """
    Get ALL session answers (newest first).
    No deduplication, no limit -- every Q&A is preserved for interview reference.

    Reads from memory if available (main process), otherwise reads from
    the JSON file on disk (web server subprocess).
    """
    with _write_lock:
        display_list = list(_all_answers)
        # Include current in-progress answer at the top
        if _current_answer.get('question') and not _current_answer.get('is_complete'):
            display_list.append(_current_answer.copy())

    # If in-memory list is empty, read from disk (web server runs in separate process)
    if not display_list and CURRENT_ANSWER_FILE.exists():
        try:
            with open(CURRENT_ANSWER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    display_list = [a for a in data if a.get('question')]
                elif isinstance(data, dict) and data.get('question'):
                    # Backward compat: old single-answer format
                    display_list = [data]
        except Exception:
            pass

    # Newest first for display
    display_list.reverse()
    return display_list


def get_latest_answer() -> Optional[Dict[str, Any]]:
    """Get the most recent answer."""
    return get_current_answer()


def get_answers_file_path() -> str:
    """Get path to current answer file."""
    return str(CURRENT_ANSWER_FILE)


def get_history_file_path() -> str:
    """Get path to history file."""
    return str(HISTORY_FILE)


def get_answer_count() -> int:
    """Get count of historical answers."""
    if not HISTORY_FILE.exists():
        return 0
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


# Backward compatibility aliases
def clear_and_start_new(question_text: str):
    """Deprecated: Use set_complete_answer instead."""
    pass


def start_new_answer(question_text: str):
    """Deprecated: Use set_complete_answer instead."""
    pass


def finalize_answer():
    """Deprecated: Use set_complete_answer instead."""
    pass


def clear_answers():
    """Alias for clear_all."""
    clear_all()
