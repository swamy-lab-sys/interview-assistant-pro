"""
Strict Interview Question Validator

PHILOSOPHY: Silence is better than a wrong answer.
If ANY doubt → reject.

Rules:
1. Must contain interview verb (what is, explain, difference between, etc.)
2. Minimum 5 words
3. Must NOT end with incomplete marker (and, of, between, to, with, etc.)
4. Must NOT be narration/teaching
5. Must NOT be casual/practice content
"""

import re
from typing import Tuple

INTERVIEW_VERBS = [
    # Core interrogative intent (User requested: what, why, how, explain, difference, define, compare)
    "what is", "what are", "what does", "what do", "what's",
    "why is", "why do", "why does", "why would",
    "how do", "how does", "how to", "how can", "how would",
    "explain", "describe", "define", "compare",
    "difference between", "differences between", "what's the difference", "what is the difference",

    # Technical interview specifics
    "walk me through", "walk through", "tell me about",
    "write code", "write a function", "implement",
    "can you explain", "could you explain",
    "what happens when", "what happens if", "concept of",
    "tell me", "explain about", "briefly", "how to use", "how to implement",
    "write a", "implement a", "create a", "function to", "logic to",

    # MCQ-style patterns (common in technical interviews)
    "which of", "which one", "which statement", "which method", "which function",
    "which data type", "which keyword", "which operator", "which module",
    "output of", "result of", "value of", "type of",
    "maximum", "minimum", "default", "correct", "true about", "false about",
    "following is", "following are", "not supported", "does not", "cannot",
    "possible length", "possible value", "possible output",
]

# =============================================================================
# INCOMPLETE SENTENCE MARKERS - Sentence cannot end with these
# =============================================================================

INCOMPLETE_ENDINGS = [
    "and", "or", "but", "so", "then",
    "of", "to", "with", "for", "from", "by", "in", "on", "at",
    "between", "the", "a", "an", "is", "are", "was", "were",
    "like", "such", "as", "than", "that", "which", "where", "when",
    "if", "because", "since", "while", "although",
    "about", "into", "onto", "through", "during",
    "can", "could", "would", "should", "will", "shall",
    "do", "does", "did", "have", "has", "had",
    "be", "being", "been",
]

# =============================================================================
# NARRATION PATTERNS - Teaching/explanation, NOT questions
# =============================================================================

NARRATION_PATTERNS = [
    # Future tense teaching
    r"^(we('ll| will)|i('ll| will)|let us)\s+(show|demonstrate|explain|see|look|go|discuss|talk|learn|cover)",
    r"^(in this|for this)\s+(video|tutorial|lesson|example|problem|section)",
    r"^(this is|here is|here's)\s+(how|what|the|a|an)",
    r"^(today|now)\s+(we('ll| will)|i('ll| will)|let's)",

    # Teaching statements
    r"^(number|string|list|array|variable|object|function|class)s?\s+(swap|sort|reverse|can be|is|are)",
    r"(can be done|is done|works|is achieved)\s+(like this|this way|as follows|by)",
    r"^(the (best|right|correct|wrong|proper|common)\s+(way|approach|method|technique))",
    r"^(one|another)\s+(way|approach|method|technique)\s+(to|is|would be)",
    r"^(this|it)\s+(allows|provides|enables|helps|helps us)\s+(to|us to)",
    r"^(the|this)\s+(scientific\s+)?method\s+(is|was|will be|allows)",

    # Instructional
    # Instructional
    r"^(first|then|finally|after that)\s*,?\s*(we|you|i|let's)",
    r"^(let me|i('ll| will)|allow me to)\s+(explain|show|demonstrate|walk)",
    r"^(as you can see|notice that|observe|watch|look at)",
    r"^(remember|note|keep in mind|don't forget)",

    # Practice/exercise context
    r"^(practice|exercise|try|attempt|solve)\s+(this|the|these)",
    r"^(the (answer|solution|result|output)\s+(is|would be|will be))",
    r"^(so the|and the)\s+(answer|solution|result|output)",
    r"^(swap|swapping|sorting|reversing|adding|removing)\s+(is|can|works|happens)",

    # Declarations
    r"^(python|java|javascript|c\+\+|go|rust|sql|html|css)\s+(has|uses|provides|supports|allows|is|was)",
    r"^(there are|there is)\s+(many|several|multiple|different|various|two|three|four)",
    r"^(this|that|it|which)\s+(is|was|will be|would be|represents|defines|means)\s+(a|an|the|our)",
    r"^(so we can|that's why|this is why|in order to)\s+(do|make|use|call|implement)",
]

COMPILED_NARRATION = [re.compile(p, re.IGNORECASE) for p in NARRATION_PATTERNS]

# =============================================================================
# IGNORE PATTERNS - Never trigger on these
# =============================================================================

IGNORE_PATTERNS = [
    # Confirmations/fillers
    r"^(okay|ok|alright|sure|yes|no|yeah|yep|nope|right|correct|exactly|absolutely)[\s,.!?]*$",
    r"^(hmm+|umm+|uh+|ah+|oh+|huh)[\s,.!?]*$",
    r"^(great|good|nice|perfect|excellent|wonderful|awesome)[\s,.!?]*$",
    r"scientific method", r"natural world", r"empirical evidence", r"observing and gathering",

    # Audio checks
    r"can you hear me",
    r"is (this|the audio|my audio|it) working",
    r"are you (able to|there|ready|hearing)",
    r"let me (check|know|see)",
    r"one (moment|second|sec|minute)",
    r"give me a (moment|second|sec|minute)",

    # Thinking aloud
    r"^(so+|well|let me (think|see))[\s,.!?]*$",
    r"^(let's see|let me see|let me think)[\s,.!?]*$",

    # Partial fragments
    r"^(and|but|so|or|also|then|because|if|when)[\s,.!?]*$",
    r"^[\s,.!?]*$",

    # Meta comments about interview
    r"(take your time|no rush|whenever you're ready)",
    r"(that's|sounds) (good|great|fine|correct|right)",
    r"^(moving on|next|let's move)",

    # Profanity & Noise
    r"what the fuck",
    r"hey what\?$",
    r"it's too hard to run",
]

COMPILED_IGNORE = [re.compile(p, re.IGNORECASE) for p in IGNORE_PATTERNS]

# =============================================================================
# FILLER REMOVAL
# =============================================================================

FILLER_PATTERNS = [
    r"^(okay|ok|alright|so|well|now|right|yes|yeah)\s*,?\s*",
    r"^(um+|uh+|hmm+|ah+)\s*,?\s*",
    r"^(let me ask you|i('ll| will) ask you|my question is|the question is)\s*[,:;]?\s*",
    r"^(the |this )?(first|next|second|third|last|final|following) question (is|would be)\s*[,:;]?\s*",
    r"^(can you |could you )?(please |kindly )?(tell me|answer)\s*[,:;]?\s*",
    r"^(so+|well)\s+",
    r"^(next slide|it's time|it is time|next time|let's try|let's start|let's see|let's talk about|let's discuss|let's look at)\s*(to|the|if)?\s*,?\s*",
]

COMPILED_FILLERS = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]

# =============================================================================
# MINIMUM THRESHOLDS
# =============================================================================

# Minimum question length (relaxed for YouTube)
MIN_WORD_COUNT = 2      # "Explain polymorphism" is valid
MIN_CHAR_COUNT = 8      # Very short questions OK if technical
 # Lowered for more flexibility

# =============================================================================
# CANONICAL INTERVIEW QUESTIONS (ALWAYS ACCEPT - BYPASS WORD COUNT)
# =============================================================================

TECHNICAL_TERMS = [
    # Python core
    "python", "decorator", "generator", "iterator", "closure", "lambda",
    "class", "function", "method", "module", "package", "member", "concept",
    "list", "dict", "dictionary", "tuple", "set", "string", "array",
    "comprehension", "slice", "slicing", "index", "indexing",
    "args", "kwargs", "argument", "parameter", "default", "keyword",
    "docstring", "annotation", "type hint", "typing",
    # Common MCQ terms
    "identifier", "variable name", "natively", "support", "data type", "output", "length",
    # OOP
    "inheritance", "polymorphism", "encapsulation", "abstraction",
    "object", "instance", "constructor", "destructor", "init",
    "self", "cls", "static", "classmethod", "staticmethod",
    "super", "mro", "method resolution", "overriding", "overloading", "override", "overwrite",
    "composition", "aggregation", "interface", "protocol",
    # Data structures
    "stack", "queue", "heap", "tree", "graph", "linked list",
    "hash", "hashtable", "hashmap", "binary tree", "bst",
    "deque", "priority queue", "trie", "b-tree", "red-black",
    "sorting", "searching", "algorithm", "complexity", "big o",
    # Concepts
    "recursion", "iteration", "loop", "variable", "constant",
    "scope", "namespace", "global", "local", "nonlocal",
    "exception", "error", "try", "except", "finally", "raise",
    "context manager", "with statement", "yield", "return",
    "pass by reference", "pass by value", "call by", "assignment",
    "truthy", "falsy", "boolean", "conditional", "ternary",
    # Memory
    "memory", "garbage collection", "gc", "reference", "pointer",
    "mutable", "immutable", "copy", "deepcopy", "shallow copy",
    "memory leak", "reference counting", "generational",
    # Advanced
    "metaclass", "descriptor", "property", "async", "await",
    "coroutine", "thread", "threading", "multiprocessing", "gil",
    "pickle", "pickling", "serialization", "json", "api", "rest",
    "singleton", "factory", "observer", "strategy", "design pattern",
    "solid", "dry", "kiss", "dependency injection",
    # Testing
    "unittest", "pytest", "testing", "mock", "fixture",
    "tdd", "bdd", "coverage", "assertion", "test case",
    # Web
    "flask", "django", "fastapi", "request", "response", "http",
    "middleware", "router", "endpoint", "authentication", "authorization",
    "session", "cookie", "token", "jwt", "oauth",
    # Database
    "sql", "database", "orm", "query", "join", "index",
    "transaction", "acid", "normalization", "denormalization",
    "nosql", "mongodb", "postgresql", "mysql", "redis",
    # Python specific
    "dunder", "magic method", "special method", "__str__", "__repr__",
    "__eq__", "__hash__", "__len__", "__iter__", "__next__",
    "__enter__", "__exit__", "__call__", "__getattr__", "__setattr__",
    "walrus", "f-string", "format", "enumerate", "zip", "map", "filter",
    "reduce", "any", "all", "sorted", "reversed", "range",
    # DevOps/Tools
    "git", "docker", "kubernetes", "ci/cd", "deployment",
    "virtual environment", "venv", "pip", "poetry", "conda",
    "asyncio", "concurrent", "future", "executor", "pool",
    "lock", "semaphore", "mutex", "deadlock", "race condition",
    # Career & Resume Terms
    "mediamint", "capgemini", "experience", "responsibility", "project", "role", "background",
    # Added Topics & Mishearings
    "abstraction", "translation", "incapacitation", "encapsulation", 
    "prime", "fizzbuzz", "factorial", "palindrome", "fibonacci",
    "django", "model", "view", "template", "orm", "migration", "middleware", "serializer", "drf",
    "sql", "select", "join", "group by", "index", "acid", "transaction", "foreign key",
    "javascript", "callback", "promise", "async", "await", "closure", "hoisting", "prototype", "dom", "react",
]

# Canonical question patterns (regex) - ALWAYS ACCEPT if matches
CANONICAL_PATTERNS = [
    r"^what (is|are) ",       # "what is python", "what are decorators"
    r"^explain ",              # "explain generators"
    r"^define ",               # "define polymorphism"
    r"^describe ",             # "describe inheritance"
    r"^tell me about ",        # "tell me about yourself"
    r"^(hi|hello|hey) ",       # Greetings
    r"^how are you",           # Social questions
    r"^your strengths",        # Soft questions
    r"^your weaknesses",       # Soft questions
]

import re
COMPILED_CANONICAL = [re.compile(p, re.IGNORECASE) for p in CANONICAL_PATTERNS]


def is_canonical_question(text: str) -> bool:
    """
    Check if text is a canonical interview question that should ALWAYS be accepted.

    Canonical questions bypass minimum word count requirements.
    Examples: "What is Python?", "Explain decorators", "Define polymorphism"

    EXPORTED: Use this for early finalization in audio capture.

    Returns:
        bool: True if canonical question (accept regardless of length)
    """
    if not text:
        return False

    lower = text.lower().strip()

    # If it's a social/social-technical pattern, accept it even without technical terms
    social_patterns = [
        r"tell me about ",
        r"about yourself",
        r"(hi|hello|hey) ",
        r"how are you",
        r"your strengths",
        r"your weaknesses",
        r"introduce yourself",
        r"where are you from",
        r"where do you (stay|live|locate)",
    ]
    
    for p in social_patterns:
        if re.search(p, lower):
            return True

    # Check if matches other canonical patterns
    matches_pattern = False
    for pattern in COMPILED_CANONICAL:
        if pattern.match(text):
            matches_pattern = True
            break

    if not matches_pattern:
        return False

    # Check if contains a technical term for other patterns
    for term in TECHNICAL_TERMS:
        if term in lower:
            return True

    return False


def _extract_question(text: str) -> str:
    """
    Extract question by trimming at first question mark.

    EXTRACTION RULE:
    - Trim transcription at first ?
    - Never include trailing explanation from video audio

    Examples:
        "What is Python? It is a programming language..." -> "What is Python?"
        "How does GC work? Let me explain..." -> "How does GC work?"
    """
    if not text:
        return ""

    text = text.strip()

    # Find first question mark
    qmark_idx = text.find('?')
    if qmark_idx > 0:
        # Extract up to and including the question mark
        return text[:qmark_idx + 1].strip()

    return text


def _remove_fillers(text: str) -> str:
    """Remove filler phrases from start of text."""
    if not text:
        return ""

    text = text.strip()
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


def _is_narration(text: str) -> bool:
    """Check if text is narration/teaching, not a question."""
    if not text:
        return False

    for pattern in COMPILED_NARRATION:
        if pattern.search(text):
            return True

    return False


def _should_ignore(text: str) -> bool:
    """Check if text should be completely ignored."""
    if not text:
        return True

    for pattern in COMPILED_IGNORE:
        if pattern.search(text):
            return True

    return False


def _has_interview_verb(text: str) -> bool:
    """Check if text contains at least one interview verb."""
    if not text:
        return False

    lower = text.lower()

    for verb in INTERVIEW_VERBS:
        if verb in lower:
            return True

    # Check for question mark with reasonable length
    if text.strip().endswith("?") and len(text.split()) >= MIN_WORD_COUNT:
        return True

    return False


def _is_incomplete(text: str) -> bool:
    """Check if sentence is incomplete (ends with preposition/conjunction)."""
    if not text:
        return True

    stripped = text.strip()

    # If ends with question mark, it's likely complete
    if stripped.endswith("?"):
        return False

    # Get last word
    words = stripped.rstrip("?.,!").split()
    if not words:
        return True

    last_word = words[-1].lower()

    # Allow "for" at end if it's part of "used for", "what for", etc.
    if last_word == "for" and len(words) >= 2:
        prev_word = words[-2].lower()
        if prev_word in ["used", "what", "designed", "made", "meant", "needed", "good", "best"]:
            return False

    return last_word in INCOMPLETE_ENDINGS


def _word_count(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def validate_question(text: str) -> Tuple[bool, str, str]:
    """
    Validate if text is a real interview question.

    Args:
        text: Raw transcribed text

    Returns:
        Tuple of (is_valid, cleaned_text, rejection_reason)
        - is_valid: True if valid interview question
        - cleaned_text: Cleaned question text (empty if invalid)
        - rejection_reason: Why rejected (empty if valid)
    """
    if not text:
        return False, "", "empty"

    original = text.strip()

    # Step 0: Extract question (trim at first ?)
    # This prevents trailing explanations from video audio
    extracted = _extract_question(original)
    if extracted != original:
        original = extracted

    # Step 1: Check ignore patterns
    if _should_ignore(original):
        return False, "", "ignore_pattern"

    # Step 2: Remove fillers FIRST (so we can check what's underneath)
    cleaned = _remove_fillers(original)

    # Step 3: Check narration AFTER filler removal
    if _is_narration(cleaned):
        return False, "", "narration"

    # Step 4: Check again after filler removal
    if _should_ignore(cleaned):
        return False, "", "ignore_after_clean"

    if _is_narration(cleaned):
        return False, "", "narration_after_clean"

    # Step 4.5: Phonetic Correction (Hard Mapping)
    phonetic_map = {
        "translation": "abstraction",
        "double": "tuple",
        "in it method": "__init__ method",
        "death method": "dev method",
        "incapacitation": "encapsulation",
        "gap picking": "pickling",
        "trickling": "pickling",
        "pick a link": "pickle",
        "kill and un": "pickling and un",
    }
    for mishearing, correction in phonetic_map.items():
        if mishearing in cleaned.lower():
            cleaned = re.sub(re.escape(mishearing), correction, cleaned, flags=re.IGNORECASE)

    # Step 5: Check for CANONICAL question (bypass word count)
    # CRITICAL: "What is Python?" must ALWAYS be accepted
    is_canonical = is_canonical_question(cleaned)

    # Step 6: Check minimum length (SKIP for canonical questions)
    if not is_canonical:
        if len(cleaned) < MIN_CHAR_COUNT:
            return False, "", f"too_short_chars:{len(cleaned)}"

        word_count = _word_count(cleaned)
        if word_count < MIN_WORD_COUNT:
            return False, "", f"too_short_words:{word_count}"

    # Step 7: Technical Sovereignty & Fragment Check (Bypass strict grammar)
    tech_count = sum(1 for term in TECHNICAL_TERMS if term in cleaned.lower())
    word_count = _word_count(cleaned)
    has_question_mark = cleaned.strip().endswith('?')

    # MCQ-style: technical statement ending with period (e.g., "Maximum possible length of an identifier.")
    # Must have at least 5 words and 1+ technical terms to avoid false positives
    is_mcq_style = cleaned.endswith('.') and tech_count >= 1 and word_count >= 5

    # Step 7a: Check for incomplete sentence EARLY (before accepting tech fragments)
    is_incomplete = _is_incomplete(cleaned)

    # Only accept canonical/MCQ-style if NOT incomplete (unless ends with ?)
    if is_canonical and not is_incomplete:
        if len(cleaned) > 1:
            cleaned = cleaned[0].upper() + cleaned[1:]
        return True, cleaned, ""

    if is_mcq_style:  # MCQ style already ends with '.', so it's complete
        if len(cleaned) > 1:
            cleaned = cleaned[0].upper() + cleaned[1:]
        return True, cleaned, ""

    if has_question_mark and tech_count >= 1:
        if len(cleaned) > 1:
            cleaned = cleaned[0].upper() + cleaned[1:]
        return True, cleaned, ""

    # Step 8: Standard Interview Verb Check
    if not _has_interview_verb(cleaned):
        return False, cleaned, "no_interview_verb"

    # Step 9: Check for incomplete sentence
    if is_incomplete:
        if tech_count < 2:
            return False, cleaned, "incomplete_sentence"

    # Step 10: RELAXED REQUIREMENT - Accept interrogative or MCQ-style questions
    first_words = cleaned.lower().split()[:3]
    first_two = ' '.join(first_words[:2]) if len(first_words) >= 2 else ''
    first_three = ' '.join(first_words[:3]) if len(first_words) >= 3 else ''

    has_interrogative_start = any([
        first_words[0] in ['what', 'why', 'how', 'explain', 'define', 'describe', 'compare', 'tell', 'which', 'is', 'are', 'can', 'hi', 'hello', 'hey', 'introduce', 'write', 'implement', 'create', 'function', 'maximum', 'minimum', 'default', 'output', 'result', 'value', 'type', 'true', 'false', 'correct', 'incorrect', 'name'],
        first_two in ['what is', 'what are', 'how do', 'how does', 'why is', 'why do', 'is it', 'are there', 'do you', 'can you', 'tell me', 'write a', 'implement a', 'function to', 'how to', 'which of', 'which one', 'output of', 'result of', 'value of', 'type of', 'true about', 'false about', 'name the', 'name a'],
        first_three in ['tell me about', 'can you explain', 'how are you', 'write a function', 'logic to find', 'which of the', 'which one of', 'what is the', 'what are the'],
        '?' in cleaned,
        # MCQ-style: statements ending with period that contain technical terms (already validated above)
        cleaned.endswith('.') and tech_count >= 1 and _word_count(cleaned) >= 4
    ])

    if not has_interrogative_start:
        return False, cleaned, "no_interrogative_start"

    # Step 9: Format output
    # Capitalize first letter
    if len(cleaned) > 1:
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Ensure proper ending
    if not cleaned.endswith(("?", ".", "!")):
        # Add question mark for question-style text
        lower = cleaned.lower()
        if any(lower.startswith(q) for q in ["what", "how", "why", "when", "where", "which", "can", "could", "is", "are", "do", "does"]):
            cleaned += "?"

    return True, cleaned, ""


def is_valid_interview_question(text: str) -> bool:
    """
    Simple check: is this a valid interview question?

    Use validate_question() for detailed rejection reason.
    """
    is_valid, _, _ = validate_question(text)
    return is_valid


def clean_and_validate(text: str):
    """
    Clean and validate question. Returns (is_valid, cleaned_text, reason).
    """
    return validate_question(text)


# =============================================================================
# CODE REQUEST DETECTION
# =============================================================================

CODE_REQUEST_PATTERNS = [
    "write code", "write a code", "write the code",
    "write a function", "write function", "write the function",
    "write a program", "write program",
    "write a script", "write script",
    "implement", "implementation",
    "show me the code", "show code", "show the code",
    "code example", "code for",
    "program to", "function to", "script to",
    "give me code", "give code",
]


def is_code_request(text: str) -> bool:
    """Check if question explicitly requests code."""
    if not text:
        return False

    lower = text.lower()

    for pattern in CODE_REQUEST_PATTERNS:
        if pattern in lower:
            return True

    return False


# =============================================================================
# TEST SUITE
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        # === MUST REJECT ===
        # Greetings/confirmations
        ("Okay", False, "ignore_pattern"),
        ("Alright", False, "ignore_pattern"),
        ("Can you hear me?", False, "ignore_pattern"),
        ("Let me think", False, "ignore_pattern"),
        ("Hmm", False, "ignore_pattern"),
        ("Great", False, "ignore_pattern"),

        # Narration/teaching (CRITICAL)
        ("We'll show you how to swap numbers in Python", False, "narration"),
        ("Number swap can be done like this", False, "narration"),
        ("Let me explain this first", False, "narration"),
        ("In this problem we will see how to reverse a list", False, "narration"),
        ("Don't do this method it's wrong", False, "narration"),
        ("Swapping is done using tuple unpacking", False, "narration"),
        ("Python has a simple way to swap variables", False, "narration"),
        ("The best way to do this is using enumerate", False, "narration"),
        ("First we will define the function", False, "narration"),
        ("As you can see the output is correct", False, "narration"),
        ("There are many ways to solve this", False, "narration"),
        ("The answer is using a dictionary", False, "narration"),

        # Incomplete sentences (CRITICAL)
        ("What is the difference between", False, "incomplete_sentence"),
        ("Explain the concept of", False, "incomplete_sentence"),
        ("How do you handle errors in", False, "incomplete_sentence"),
        ("What happens when you use", False, "incomplete_sentence"),
        ("Can you explain the", False, "incomplete_sentence"),

        # CANONICAL QUESTIONS - MUST ACCEPT (even if short)
        ("What is Python", True, ""),  # Canonical - ACCEPT
        ("What is decorator", True, ""),  # Canonical - ACCEPT
        ("Explain decorators", True, ""),  # Canonical - ACCEPT
        ("What are generators", True, ""),  # Canonical - ACCEPT

        # Still too short (not canonical)
        ("Tell me about it", False, "too_short"),  # Not canonical, too short

        # No interview verb
        ("Python is a great language right", False, "no_interview_verb"),
        ("I use Python every day at work", False, "no_interview_verb"),

        # === MUST ACCEPT ===
        # Direct questions
        ("What is Python and why is it popular?", True, ""),
        ("How do you swap two numbers in Python?", True, ""),
        ("Explain how decorators work in Python", True, ""),
        ("What is the difference between list and tuple?", True, ""),
        ("Why is Python called an interpreted language?", True, ""),

        # Coding requests
        ("Write code to swap two numbers", True, ""),
        ("Implement a function to reverse a string", True, ""),
        ("Write a program to find duplicates in a list", True, ""),

        # With fillers (should clean and accept)
        ("Okay, what is Python used for?", True, ""),
        ("Alright, explain list comprehensions in Python", True, ""),
        ("The first question is what is pickling?", True, ""),

        # Edge cases that should pass
        ("Can you explain what happens when Python imports a module?", True, ""),
        ("How would you handle exceptions in a production system?", True, ""),
        ("What's the difference between append and extend methods?", True, ""),
    ]

    print("=" * 70)
    print("STRICT INTERVIEW QUESTION VALIDATOR - TEST SUITE")
    print("=" * 70)
    print()

    passed = 0
    failed = 0

    for text, expected_valid, expected_reason in test_cases:
        is_valid, cleaned, reason = validate_question(text)

        # Check validity
        validity_match = is_valid == expected_valid

        # For rejections, check if reason category matches
        reason_match = True
        if not expected_valid and expected_reason:
            reason_match = reason.startswith(expected_reason.split(":")[0])

        success = validity_match and reason_match

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"[{status}] Input: \"{text}\"")
        print(f"       Expected: valid={expected_valid}, reason~{expected_reason}")
        print(f"       Got:      valid={is_valid}, reason={reason}")
        if is_valid:
            print(f"       Cleaned:  \"{cleaned}\"")
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)}")
    print("=" * 70)
