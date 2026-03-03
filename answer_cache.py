"""
Answer Cache for Interview Voice Assistant

REQUIRED: Cache answers by normalized question to avoid repeated LLM calls.

RULES:
1. Normalize question before lookup (lowercase, strip punctuation, whitespace)
2. Cache hit = instant return (<1s)
3. Cache miss = LLM call (2-4s)
4. No expiration (session-scoped)
5. No persistence (memory only)
"""

import re
import time
import atexit
import threading
from collections import OrderedDict
from typing import Optional, Dict

import config

import json
from pathlib import Path

# Thread-safe LRU cache using OrderedDict
_cache: OrderedDict = OrderedDict()
_cache_lock = threading.Lock()
_max_size: int = getattr(config, 'CACHE_MAX_SIZE', 1000)

# Persistent Cache File
# Fix: config.ANSWERS_DIR is a string, so we must wrap it in Path() and expand user (~)
CACHE_FILE = Path(config.ANSWERS_DIR).expanduser() / "answer_cache.json"

# Cache stats
_hits = 0
_misses = 0

# Batched write control
_dirty = False
_last_save_time = 0.0
_SAVE_INTERVAL = 30.0  # Save to disk at most every 30 seconds


def load_cache_from_disk():
    """Load cache from disk on startup."""
    global _cache
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with _cache_lock:
                    _cache.clear()
                    # Convert dict back to OrderedDict (insertion order not guaranteed in JSON, but useful enough)
                    for k, v in data.items():
                        _cache[k] = v
            print(f"[CACHE] Loaded {len(_cache)} answers from disk.")
    except Exception as e:
        print(f"[CACHE] Failed to load cache: {e}")

# NOTE: Do not auto-load at import. main.py calls clear_cache() immediately after import.
# Call load_cache_from_disk() explicitly if you need persistence across restarts.


def _flush_on_exit():
    """Save dirty cache to disk on shutdown."""
    if _dirty:
        save_cache_to_disk()

atexit.register(_flush_on_exit)

def save_cache_to_disk():
    """Save cache to disk."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _cache_lock:
            # OrderedDict to dict
            data = dict(_cache)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[CACHE] Failed to save cache: {e}")


def normalize_question(question: str) -> str:
    """
    Normalize question for cache lookup.
    """
    if not question:
        return ""

    # Lowercase and strip
    normalized = question.lower().strip()

    # Remove trailing punctuation
    normalized = re.sub(r'[?.!,;:]+$', '', normalized)

    # Remove leading filler words
    filler_pattern = r'^(okay|ok|alright|so|well|um+|uh+|hmm+|ah+)\s*,?\s*'
    normalized = re.sub(filler_pattern, '', normalized, flags=re.IGNORECASE)

    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized)

    # Final strip
    normalized = normalized.strip()

    return normalized


def get_cached_answer(question: str) -> Optional[str]:
    """Get cached answer for question."""
    global _hits, _misses

    key = normalize_question(question)
    if not key:
        return None

    with _cache_lock:
        if key in _cache:
            _hits += 1
            _cache.move_to_end(key)  # Mark as recently used
            return _cache[key]
        _misses += 1
        return None


def cache_answer(question: str, answer: str) -> None:
    """Cache answer for question. Disk writes are batched for performance."""
    global _dirty, _last_save_time
    key = normalize_question(question)
    if not key or not answer:
        return

    with _cache_lock:
        _cache[key] = answer
        _cache.move_to_end(key)
        while len(_cache) > _max_size:
            _cache.popitem(last=False)
        _dirty = True

    # Batched disk write: only save every _SAVE_INTERVAL seconds
    now = time.time()
    if now - _last_save_time >= _SAVE_INTERVAL:
        save_cache_to_disk()
        _last_save_time = now
        _dirty = False


def is_duplicate_question(question: str) -> bool:
    """Check if question is already cached (duplicate)."""
    key = normalize_question(question)
    if not key:
        return False

    with _cache_lock:
        return key in _cache


def clear_cache() -> None:
    """Clear all cached answers (fresh start)."""
    global _hits, _misses

    with _cache_lock:
        _cache.clear()
        _hits = 0
        _misses = 0
    
    save_cache_to_disk()


def get_cache_stats() -> Dict[str, int]:
    """
    Get cache statistics.

    Returns:
        dict with 'hits', 'misses', 'size'
    """
    with _cache_lock:
        return {
            'hits': _hits,
            'misses': _misses,
            'size': len(_cache)
        }


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ANSWER CACHE - TEST")
    print("=" * 60)

    # Test normalization
    test_cases = [
        ("What is Python?", "what is python"),
        ("What is Python", "what is python"),
        ("WHAT IS PYTHON?", "what is python"),
        ("Okay, what is Python?", "what is python"),
        ("  What  is   Python?  ", "what is python"),
        ("Um, what is Python", "what is python"),
        ("So, what is Python?", "what is python"),
    ]

    print("\nNormalization tests:")
    for input_q, expected in test_cases:
        result = normalize_question(input_q)
        status = "PASS" if result == expected else "FAIL"
        print(f"  [{status}] '{input_q}' -> '{result}'")
        if result != expected:
            print(f"         Expected: '{expected}'")

    # Test caching
    print("\nCaching tests:")
    clear_cache()

    # Cache miss
    result = get_cached_answer("What is Python?")
    print(f"  Cache miss: {result is None}")

    # Cache answer
    cache_answer("What is Python?", "Python is a programming language.")

    # Cache hit
    result = get_cached_answer("What is Python?")
    print(f"  Cache hit: {result is not None}")
    print(f"  Answer: {result}")

    # Normalized cache hit (different formatting)
    result = get_cached_answer("Okay, what is python")
    print(f"  Normalized hit: {result is not None}")

    # Stats
    stats = get_cache_stats()
    print(f"\n  Stats: {stats}")

    print("\n" + "=" * 60)
