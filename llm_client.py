"""
LLM Client for Interview Voice Assistant

Supports both streaming and single-shot modes.

Rules:
- 10 second hard timeout
- 2-3 sentence answers
- Code only when explicitly asked
"""

import os
import time
from anthropic import Anthropic

# Import debug logger
try:
    import debug_logger as dlog
    LOGGING_ENABLED = True
except ImportError:
    LOGGING_ENABLED = False
    class DlogStub:
        def log(self, *args, **kwargs): pass
        def log_error(self, *args, **kwargs): pass
    dlog = DlogStub()

# Client with 10s timeout
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    max_retries=2,
    timeout=10.0
)

# Haiku for speed
MODEL = "claude-3-haiku-20240307"

# Token limits - enough to complete answers
MAX_TOKENS_INTERVIEW = 200  # Complete answers without cut-off
MAX_TOKENS_CODING = 250     # Clean code with example

# Temperature - lower = more consistent
TEMP_INTERVIEW = 0.2
TEMP_CODING = 0.1


def get_interview_answer(question: str, resume_text: str = "", include_code: bool = False) -> str:
    """
    Get interview answer in SINGLE-SHOT mode (fallback).
    """
    # CLEAN PROFESSIONAL - NO FILLERS
    system_prompt = """You are Venkata, Senior Python Developer (5+ years).

RULES:
1. NO FILLERS ("Ah", "Sure"). Start DIRECTLY with the answer.
2. STRUCTURE:
   - **Key Concept**: 1 sentence definition.
   - **Explanation**: 2-3 bullet points max.
   - **Code**: < 5 lines, ONLY if essential.
3. LENGTH: Keep it under 100 words.

INTRO: "I'm Venkata Chalapathi from Tirupati, 5+ years Python Django. MediaMint. Building HRMS (70+ apps). CI/CD, DB optimization. Looking for backend roles."

PHONETIC: translation=Abstraction, double=Tuple
"""

    start_time = time.time()
    dlog.log(f"[LLM] Single-shot request: {question[:50]}...", "DEBUG")

    try:
        api_start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_INTERVIEW,
            temperature=TEMP_INTERVIEW,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        )
        api_time = time.time() - api_start

        elapsed = time.time() - start_time
        answer = response.content[0].text.strip()

        dlog.log(f"[LLM] Single-shot complete: {len(answer)} chars in {api_time*1000:.0f}ms", "DEBUG")
        return answer

    except Exception as e:
        elapsed = time.time() - start_time
        dlog.log_error(f"[LLM] Single-shot failed after {elapsed*1000:.0f}ms", e)
        print(f"[LLM ERROR] {elapsed:.2f}s | {e}")
        return ""  # Return empty on error - silence is better


def get_streaming_interview_answer(question: str, resume_text: str = ""):
    """
    Get interview answer in STREAMING mode.
    Yields chunks of text.
    """
    # CLEAN PROFESSIONAL ANSWERS - 5 YEARS EXPERIENCE
    system_prompt = """You are Venkata Chalapathi, Senior Python Developer (5+ years).

=== STRICT RULES ===
1. **NO FILLERS**: No "Ah,", "Okay,", "Let me explain".
2. **FORMAT**:
   - **Main Point**: 1 sentence direct answer.
   - **Details**: 2-3 short bullet points.
   - **Code**: Max 5 lines (if needed).
3. **TONE**: Professional, confident, concise.

=== EXAMPLE ===
**Main Point**: Lists are mutable, Tuples are immutable.
**Details**:
- Lists: `[]`, can change elements (dynamic data).
- Tuples: `()`, fixed elements (config, constants).
**Code**:
```python
x = [1, 2] # List
y = (1, 2) # Tuple
```

=== INTRO ===
"I'm Venkata Chalapathi from Tirupati, 5+ years Python Django. MediaMint. Building HRMS (70+ apps). CI/CD, DB optimization. Looking for backend roles."

=== PHONETICS ===
- "translation" -> "Abstraction"
- "double" -> "Tuple"
"""

    dlog.log(f"[LLM] Streaming request: {question[:50]}...", "DEBUG")
    stream_start = time.time()
    chunk_count = 0
    total_chars = 0
    first_chunk_time = None

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS_INTERVIEW,
            temperature=TEMP_INTERVIEW,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        ) as stream:
            for text in stream.text_stream:
                chunk_count += 1
                total_chars += len(text)
                if first_chunk_time is None:
                    first_chunk_time = time.time() - stream_start
                    dlog.log(f"[LLM] First chunk in {first_chunk_time*1000:.0f}ms", "DEBUG")
                yield text

        total_time = time.time() - stream_start
        dlog.log(f"[LLM] Stream complete: {total_chars} chars, {chunk_count} chunks in {total_time*1000:.0f}ms", "DEBUG")

    except Exception as e:
        elapsed = time.time() - stream_start
        dlog.log_error(f"[LLM] Stream failed after {elapsed*1000:.0f}ms", e)
        print(f"[LLM STREAM ERROR] {e}")
        yield ""


def get_coding_answer(question: str) -> str:
    """
    Get coding answer in SINGLE-SHOT mode.
    Clean, professional code with example
    """
    system_prompt = """Write clean Python code as a senior developer would.

RULES:
- Brief explanation (1 sentence) of approach
- Clean, readable code (10-15 lines max)
- Include example usage with print()
- Use meaningful variable names

FORMAT:
Brief approach, then code:
```python
def function_name(param):
    # logic
    return result

# Example
print(function_name(5))
```

Sound like experienced developer, not textbook."""

    start_time = time.time()
    dlog.log(f"[LLM] Coding request: {question[:50]}...", "DEBUG")

    try:
        api_start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_CODING,
            temperature=TEMP_CODING,
            system=system_prompt,
            messages=[{"role": "user", "content": question}]
        )
        api_time = time.time() - api_start

        elapsed = time.time() - start_time
        answer = response.content[0].text.strip()

        dlog.log(f"[LLM] Coding complete: {len(answer)} chars in {api_time*1000:.0f}ms", "DEBUG")
        return answer

    except Exception as e:
        elapsed = time.time() - start_time
        dlog.log_error(f"[LLM] Coding failed after {elapsed*1000:.0f}ms", e)
        print(f"[LLM-CODE ERROR] {elapsed:.2f}s | {e}")
        return ""  # Return empty on error - silence is better
