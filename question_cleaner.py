"""
Question Cleaner & Validator for Interview Voice Assistant

CRITICAL: Only pass through REAL interview questions.
Filter out casual conversation, greetings, thinking aloud.

If in doubt → return empty string → NO ANSWER
"""

import re

# ============================================================
# NOISE PATTERNS - These are NOT questions, IGNORE completely
# ============================================================

IGNORE_PATTERNS = [
    # Greetings & confirmations
    r"^(hi|hello|hey|good morning|good afternoon|good evening)[\s,.!?]*$",
    r"^(okay|ok|alright|sure|yes|no|yeah|yep|nope|right|correct)[\s,.!?]*$",
    r"^(hmm+|umm+|uh+|ah+|oh+)[\s,.!?]*$",

    # Audio/connection checks
    r"can you hear me",
    r"are you (able to |there|ready)",
    r"is (this|it) working",
    r"let me (know|check)",
    r"one (moment|second|sec)",

    # Thinking aloud
    r"^(so+|well|let me (think|see))[\s,.]*$",
    r"^(let's see|let me see)[\s,.]*$",
    r"^(give me a|just a) (moment|second|sec)",

    # Confirmations about candidate
    r"you (have |'ve )?(worked|used|know|familiar)",
    r"(have you|do you) (worked|used|know)",
    r"^(that's|sounds) (good|great|fine|correct)",

    # Partial/incomplete
    r"^(and|but|so|or|also|then)[\s,.]*$",
    r"^[\s,.!?]*$",
]

# ============================================================
# NARRATION PATTERNS - Teaching/explaining, NOT asking
# ============================================================

NARRATION_PATTERNS = [
    # Future tense narration ("we will show you...")
    r"^(we('ll| will)|i('ll| will)|let's|let us) (show|demonstrate|explain|see|look|discuss|talk)",
    r"^(in this|for this) (video|question|problem|example)",
    r"^(this is|here is|here's) (how|what|the)",

    # Teaching statements
    r"^(number|string|list|array|variable)s? (swap|sort|reverse|can be)",
    r"(can be done|is done|works) (like this|this way|as follows)",
    r"^(don't|do not|never|always) (do|use|try)",
    r"^(the (best|right|correct|wrong) way)",

    # Declarative explanations (not questions)
    r"^(swap|swapping|sorting|reversing) (is|can|works)",
    r"^(python|java|javascript) (has|uses|provides)",
    r"^(there are|there is) (many|several|multiple|different)",

    # Instructional
    r"^(first|then|next|finally|now) (we|you|i)",
    r"^(let me|i('ll| will)) (explain|show|demonstrate)",
    r"^(as you can see|notice that|observe)",
]

COMPILED_NARRATION = [re.compile(p, re.IGNORECASE) for p in NARRATION_PATTERNS]

COMPILED_IGNORE = [re.compile(p, re.IGNORECASE) for p in IGNORE_PATTERNS]

# ============================================================
# QUESTION INDICATORS - Must have at least one
# ============================================================

QUESTION_STARTERS = [
    "what", "how", "why", "when", "where", "which",
    "explain", "describe", "define", "tell me about",
    "compare", "difference", "write", "implement",
    "can you explain", "could you explain",
    "give me", "show me", "walk me through",
]

QUESTION_KEYWORDS = [
    "what is", "what are", "what does", "what do",
    "how to", "how do", "how does", "how can",
    "why is", "why do", "why does",
    "explain", "describe", "define",
    "difference between", "compare",
    "implement", "write a", "write code",
    "example of", "give example",
]

# ============================================================
# FILLER REMOVAL
# ============================================================

FILLER_PATTERNS = [
    r"^(okay|ok|alright|so|well|now|right)\s*,?\s*",
    r"^(um+|uh+|hmm+|ah+)\s*,?\s*",
    r"^(let me ask you|i('ll| will) ask you|my question is)\s*,?\s*",
    r"^(the |this )?(first|next|second|last|final) question (is|would be)\s*:?\s*",
    r"^(can you |could you )?(please |kindly )?(tell me|answer)\s*,?\s*",
    r"^(hi |hello |hey )?(everyone|there)\s*,?\s*",
    r"^(in this |for this )?(question|one|video)\s*,?\s*(we('ll| will) )?(show|ask|discuss)?\s*",
    r"^(so+|well)\s+",
    r"^(yeah|yes)\s*,?\s*",
]

COMPILED_FILLERS = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]


def is_narration(text: str) -> bool:
    """
    Check if text is narration/teaching (not a question).

    Narration examples:
    - "We'll show you how to swap numbers"
    - "Number swap can be done like this"
    - "Let me explain this first"
    """
    if not text:
        return False

    text = text.strip()

    # Check against narration patterns
    for pattern in COMPILED_NARRATION:
        if pattern.search(text):
            return True

    return False


def should_ignore(text: str) -> bool:
    """
    Check if text should be completely ignored (not a question).

    Returns True if text is:
    - Greeting
    - Confirmation
    - Thinking aloud
    - Audio check
    - Narration/teaching
    - Too short
    """
    if not text:
        return True

    text = text.strip()

    # Too short to be a real question
    if len(text) < 15:
        return True

    # Check against ignore patterns
    for pattern in COMPILED_IGNORE:
        if pattern.search(text):
            return True

    # Check if it's narration (teaching, not asking)
    if is_narration(text):
        return True

    return False


def has_question_intent(text: str) -> bool:
    """
    Check if text has clear question intent.

    Returns True if text contains question indicators.
    """
    if not text:
        return False

    lower = text.lower()

    # Check for question keywords
    for keyword in QUESTION_KEYWORDS:
        if keyword in lower:
            return True

    # Check for question starters
    for starter in QUESTION_STARTERS:
        if lower.startswith(starter):
            return True

    # Check for question mark
    if text.strip().endswith("?"):
        return True

    return False


def remove_fillers(text: str) -> str:
    """Remove filler phrases from beginning of text."""
    if not text:
        return ""

    text = text.strip()

    # Apply filler removal repeatedly
    changed = True
    iterations = 0
    while changed and iterations < 10:
        changed = False
        iterations += 1
        for pattern in COMPILED_FILLERS:
            new_text = pattern.sub('', text).strip()
            if new_text != text and len(new_text) > 0:
                text = new_text
                changed = True

    return text


def extract_question(text: str) -> str:
    """
    Extract the actual question from multi-sentence text.

    If multiple sentences, find the one with question intent.
    """
    if not text:
        return ""

    # Split into sentences
    sentences = re.split(r'[.!]\s+', text)

    # If only one sentence, return it
    if len(sentences) == 1:
        return text.strip()

    # Find sentence with question intent (prefer later ones)
    for sentence in reversed(sentences):
        sentence = sentence.strip()
        if sentence and has_question_intent(sentence):
            return sentence

    # If no clear question found, return the last substantial sentence
    for sentence in reversed(sentences):
        sentence = sentence.strip()
        if len(sentence) > 15:
            return sentence

    return text.strip()


def clean_question(text: str) -> str:
    """
    Main function: Clean and validate interview question.

    Returns:
    - Cleaned question if valid
    - Empty string if should be ignored

    CRITICAL: If in doubt, return empty string.
    """
    if not text:
        return ""

    text = text.strip()

    # Step 1: Check if entire text should be ignored
    if should_ignore(text):
        return ""

    # Step 2: Remove fillers
    text = remove_fillers(text)

    # Step 3: Check again after filler removal
    if should_ignore(text):
        return ""

    # Step 4: Extract the actual question
    text = extract_question(text)

    # Step 5: Final validation - must have question intent
    if not has_question_intent(text):
        # Check if it's a clear imperative (explain X, describe Y)
        lower = text.lower()
        imperatives = ["explain", "describe", "define", "compare", "implement", "write"]
        if not any(lower.startswith(imp) for imp in imperatives):
            return ""  # No clear question intent

    # Step 6: Capitalize and clean up
    if text:
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

        # Remove trailing period if followed by nothing
        text = text.rstrip('.')

        # Add question mark if it's a question
        if not text.endswith('?'):
            lower = text.lower()
            if any(lower.startswith(q) for q in ["what", "how", "why", "when", "where", "which", "can", "could", "is", "are", "do", "does"]):
                text += "?"

    return text


def is_code_request(text: str) -> bool:
    """
    Check if the question explicitly requests code.

    Returns True only if interviewer says:
    - "write code"
    - "implement"
    - "program"
    - "show example"
    - "write a function"
    """
    if not text:
        return False

    lower = text.lower()

    code_keywords = [
        "write code", "write a code",
        "write a function", "write function",
        "write a program", "write program",
        "implement", "implementation",
        "show me the code", "show code",
        "code example", "show example",
        "program to", "function to",
        "write a script", "script to",
    ]

    for keyword in code_keywords:
        if keyword in lower:
            return True

    return False


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    tests = [
        # Should IGNORE - Greetings/confirmations
        ("Okay", ""),
        ("Can you hear me?", ""),
        ("Alright", ""),
        ("Let me think", ""),
        ("Hmm", ""),
        ("Are you ready?", ""),

        # Should IGNORE - Narration/teaching (CRITICAL)
        ("We'll show you how to swap numbers in Python", ""),
        ("Number swap can be done like this", ""),
        ("Let me explain this first", ""),
        ("In this problem we will see how to reverse", ""),
        ("Don't do this method", ""),
        ("Swapping is done using tuple unpacking", ""),
        ("Python has a simple way to swap", ""),
        ("The best way to do this is", ""),

        # Should ANSWER - Direct questions
        ("How do you swap two numbers in Python?", "How do you swap two numbers in Python?"),
        ("Explain how to swap two numbers", "Explain how to swap two numbers"),
        ("Write code to swap two numbers", "Write code to swap two numbers"),
        ("What is Python?", "What is Python?"),
        ("What is pickling?", "What is pickling?"),

        # Should ANSWER - With filler removed
        ("Okay, what is Python?", "What is Python?"),
        ("Alright, explain list vs tuple", "Explain list vs tuple"),
        ("The first question is: explain decorators", "Explain decorators"),
    ]

    print("Question Cleaner Tests (with Narration Detection):")
    print("=" * 70)

    passed = 0
    failed = 0

    for input_text, expected in tests:
        result = clean_question(input_text)
        status = "✓" if result == expected else "✗"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"{status} IN:  '{input_text}'")
        print(f"  OUT: '{result}'")
        if result != expected:
            print(f"  EXP: '{expected}'")
        print()

    print(f"Results: {passed} passed, {failed} failed")
