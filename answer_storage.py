"""
Answer Storage for Interview Voice Assistant

SINGLE-ANSWER MODE WITH PERFORMANCE METRICS

Features:
- Single Q&A displayed at a time
- New question REPLACES previous (no stacking)
- Performance metrics (latency) stored with each answer
- Thread-safe operations
"""

import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
ANSWERS_DIR = Path.home() / ".interview_assistant"
CURRENT_ANSWER_FILE = ANSWERS_DIR / "current_answer.json"
HISTORY_FILE = ANSWERS_DIR / "answer_history.jsonl"
MASTER_LOG_FILE = ANSWERS_DIR / "interview_master_log.jsonl"  # Permanent storage

# Thread-safe write lock
_write_lock = threading.Lock()

# Current answer buffer
_current_answer: Dict[str, Any] = {
    'question': '',
    'answer': '',
    'timestamp': '',
    'is_complete': False,
    'metrics': None,  # Performance metrics
}


def ensure_answers_dir():
    """Create answers directory if not exists."""
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)


def _write_current():
    """Write current answer to file for web UI - IMMEDIATE FLUSH."""
    import os
    try:
        ensure_answers_dir()
        with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
            json.dump(_current_answer, f, ensure_ascii=False)  # Removed indent for speed
            f.flush()
            os.fsync(f.fileno())  # Force write to disk immediately
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


def _background_log_permanent(data: Dict[str, Any]):
    """Background task to save to master log."""
    try:
        ensure_answers_dir()
        # Append to master log - NEVER CLEARED
        with open(MASTER_LOG_FILE, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')
    except Exception:
        # Silently fail to avoid affecting main thread
        pass


def clear_all():
    """Clear all stored answers (fresh start)."""
    global _current_answer

    ensure_answers_dir()

    with _write_lock:
        _current_answer = {
            'question': '',
            'answer': '',
            'timestamp': '',
            'is_complete': False,
            'metrics': None,
        }

        try:
            with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
                json.dump(_current_answer, f, ensure_ascii=False)
            
            # Clear history file (Session only)
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
                
            # NOTE: We DO NOT clear MASTER_LOG_FILE
                
        except Exception:
            pass


def set_processing_question(question_text: str):
    """
    Set current question in 'thinking' mode.
    """
    global _current_answer
    with _write_lock:
        _current_answer = {
            'question': question_text.strip(),
            'answer': '', # Start empty for streaming
            'timestamp': datetime.now().isoformat(),
            'is_complete': False,
            'metrics': None,
        }
        _write_current()


def append_answer_chunk(chunk: str):
    """Append a chunk of text to the current answer (Streaming)."""
    global _current_answer
    with _write_lock:
        _current_answer['answer'] += chunk
        _write_current()


def set_complete_answer(
    question_text: str,
    answer_text: str,
    metrics: Optional[Dict[str, int]] = None
):
    """
    Set complete answer with optional metrics.

    ATOMIC OPERATION:
    - Sets answer (in case streaming missed something or for final clean version)
    - Stores performance metrics
    - Single UI update
    - Triggers background permanent logging
    """
    global _current_answer

    ensure_answers_dir()

    with _write_lock:
        _current_answer = {
            'question': question_text.strip(),
            'answer': answer_text.strip(),
            'timestamp': datetime.now().isoformat(),
            'is_complete': True,
            'metrics': metrics,
        }
        _write_current()
        _save_to_history()
        
        # Fire and forget background logging for performance
        threading.Thread(
            target=_background_log_permanent, 
            args=(_current_answer.copy(),)
        ).start()



def get_current_answer() -> Optional[Dict[str, Any]]:
    """
    Get the current answer.

    Returns:
        dict with question, answer, timestamp, is_complete, metrics
        or None if no answer
    """
    if CURRENT_ANSWER_FILE.exists():
        try:
            with open(CURRENT_ANSWER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('question'):
                    return data
        except Exception:
            pass

    return None


def get_all_answers() -> list:
    """
    Get unique recent answers (Question-based de-duplication).
    """
    answers_map = {} # Key: Question, Value: Answer data
    
    # 1. Load history
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        ans = json.loads(line.strip())
                        q = ans.get('question', '').lower().strip()
                        if q:
                            # Keep the latest version of this question
                            answers_map[q] = ans
                    except:
                        continue
        except:
            pass
            
    # 2. Add current (always takes priority)
    current = get_current_answer()
    if current:
        q = current.get('question', '').lower().strip()
        if q:
            answers_map[q] = current
            
    # 3. Sort by timestamp (newest first) and limit to 5
    sorted_answers = sorted(answers_map.values(), key=lambda x: x.get('timestamp', ''), reverse=True)
    return sorted_answers[:5]


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


# Note: append_answer_chunk is defined above at line 107 for streaming support


def finalize_answer():
    """Deprecated: Use set_complete_answer instead."""
    pass


def clear_answers():
    """Alias for clear_all."""
    clear_all()
