"""
Fragment Context - Cross-source question merging.

Handles: Interviewer types "find even numbers" in chat, then speaks
"using slicing method" → merged into "find even numbers using slicing method"

Uses shared file for cross-process communication (main.py + web/server.py).
"""

import json
import time
from pathlib import Path

CONTEXT_FILE = Path.home() / ".interview_assistant" / "fragment_context.json"
MERGE_WINDOW = 45  # seconds - fragments within this window can be merged

# In-memory cache to avoid disk reads in same process
_context_cache = None
_dir_ensured = False

FILLER_WORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'in', 'of', 'to', 'and', 'or',
    'for', 'with', 'by', 'on', 'at', 'it', 'this', 'that', 'do',
    'does', 'can', 'you', 'me', 'i', 'we', 'my', 'your', 'how',
    'what', 'which', 'from', 'be', 'have', 'has', 'was', 'were',
    'will', 'would', 'could', 'should', 'not', 'no', 'so', 'given',
})

# Words that start a continuation fragment (not a new question)
CONTINUATION_STARTERS = (
    "using ", "with ", "by ", "in python", "in java", "in ",
    "for ", "then ", "also ", "and then ", "and ",
    "without ", "instead of ", "rather than ", "not using ",
    "optimize ", "improve ", "refactor ", "but ",
    "like ", "such as ", "via ",
)

# Method/technique keywords that indicate a continuation when in short fragments
METHOD_KEYWORDS = {
    "slicing", "slice", "list comprehension", "comprehension",
    "lambda", "recursion", "recursive", "iteration", "iterative",
    "sorting", "filtering", "mapping", "reduce",
    "generator", "decorator", "class based", "function based",
    "brute force", "dynamic programming", "binary search",
    "two pointer", "sliding window", "stack", "queue",
    "hashmap", "hash map", "linked list", "dictionary",
    "set", "tuple", "regex", "built in", "builtin",
    "one liner", "one line", "loop", "for loop", "while loop",
    "try except", "exception handling",
}


def save_context(question: str, source: str):
    """Save processed question as context for future merging."""
    global _context_cache, _dir_ensured
    data = {
        'question': question.strip(),
        'source': source,
        'timestamp': time.time(),
    }
    _context_cache = data
    try:
        if not _dir_ensured:
            CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
            _dir_ensured = True
        with open(CONTEXT_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def get_recent_context():
    """Get recent question context if within merge window."""
    global _context_cache
    # Fast path: use in-memory cache (same process)
    if _context_cache and time.time() - _context_cache.get('timestamp', 0) <= MERGE_WINDOW:
        return _context_cache
    # Slow path: read from disk (cross-process)
    try:
        if not CONTEXT_FILE.exists():
            return None
        with open(CONTEXT_FILE, 'r') as f:
            data = json.load(f)
        if time.time() - data.get('timestamp', 0) <= MERGE_WINDOW:
            _context_cache = data
            return data
        return None
    except Exception:
        return None


def is_continuation(text: str) -> bool:
    """Check if text is a continuation fragment, not a standalone question."""
    if not text:
        return False

    lower = text.lower().strip()
    words = lower.split()

    if len(words) > 10 or len(words) < 2:
        return False

    # Starts with continuation word
    for starter in CONTINUATION_STARTERS:
        if lower.startswith(starter):
            return True

    # Short fragment with method keyword but no question starter
    if len(words) <= 6:
        from question_validator import QUESTION_STARTERS
        has_q_starter = any(lower.startswith(s) for s in QUESTION_STARTERS)
        if not has_q_starter and not lower.endswith('?'):
            for kw in METHOD_KEYWORDS:
                if kw in lower:
                    return True

    return False


def merge_with_context(new_text: str) -> tuple:
    """
    Try to merge new text with recent context.

    Returns (merged_text, was_merged)
    """
    if not new_text:
        return new_text, False

    context = get_recent_context()
    if not context:
        return new_text, False

    prev_q = context.get('question', '').strip()
    if not prev_q:
        return new_text, False

    new_lower = new_text.lower().strip()
    prev_lower = prev_q.lower().strip()

    prev_words = set(prev_lower.split()) - FILLER_WORDS
    new_words = set(new_lower.split()) - FILLER_WORDS

    # Case 1: Explicit Continuation Starter
    # e.g. "using slicing" -> "Find even numbers using slicing"
    for starter in CONTINUATION_STARTERS:
        if new_lower.startswith(starter):
            return f"{prev_q} {new_text}", True

    # Case 2: Method/Technique Keyword present in short fragment
    # e.g. "recursion" -> "Fibonacci using recursion"
    if len(new_text.split()) < 6:
        for kw in METHOD_KEYWORDS:
            if kw in new_lower:
                return f"{prev_q} using {new_text}" if "using" not in new_lower else f"{prev_q} {new_text}", True

    # Case 3: Significant Overlap (Rephrasing or Expansion)
    # e.g. "Find longest substring" ... "Longest substring without repeats"
    # Logic: If new text contains significant part of old text, use new text (it's likely a correction/refinement)
    if prev_words and new_words:
        shared = prev_words & new_words
        overlap_ratio = len(shared) / len(prev_words)
        
        # If >50% of the previous question words are repeated in the new one, assume new one is simply a better version
        if overlap_ratio > 0.5:
             # But if new text adds significant length, it might be an elaboration
             return new_text, True

    # Case 4: Data + Instruction Merge
    # e.g. Chat: "[1, 2, 3]" -> Voice: "Filter out odd numbers"
    # Logic: If one fragment looks like a code list/structure and the other is an instruction, merge them.
    is_prev_data = any(c in prev_q for c in "[]{}()") or "list" in prev_lower or "numbers" in prev_lower
    
    # Specific fix for "filter out" queries which rely heavily on context
    is_filter_task = "filter" in new_lower or "remove" in new_lower or "keep" in new_lower or "odd" in new_lower or "even" in new_lower
    
    if is_prev_data and (is_filter_task or "find" in new_lower or "calculate" in new_lower or "count" in new_lower):
         # If new text is just a short instruction, append it. If it's a full sentence rephrase, maybe not.
         # But usually "filter odd numbers" assumes the list exists.
         return f"{prev_q} and then {new_text}", True

    return new_text, False


def clear_context():
    """Clear fragment context (fresh start)."""
    global _context_cache
    _context_cache = None
    try:
        if CONTEXT_FILE.exists():
            CONTEXT_FILE.unlink()
    except Exception:
        pass
