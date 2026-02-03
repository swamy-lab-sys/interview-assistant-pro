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

# Token limits
MAX_TOKENS_INTERVIEW = 180  # Definition + code example + use case
MAX_TOKENS_CODING = 200     # Clean code with example

# Temperature - lower = more consistent
TEMP_INTERVIEW = 0.2
TEMP_CODING = 0.1

# Shared interview prompt — controls all response behavior
INTERVIEW_PROMPT = """You are an Interview Assistant designed for live technical interviews.
You are NOT a tutor, teacher, or documentation generator.
Your role is to behave like a real, experienced candidate answering an interviewer in real time.

HARD RULES (NEVER VIOLATE):
1. NEVER echo, repeat, or reference constraints from the question. If asked "do X without Y", just do X. Never write "without Y" or "here's how to do it without Y" in your answer.
2. When a question is rephrased, your answer MUST use different words and be shorter than the original. Maximum 2-3 sentences. No lists. No bullet points. No expansion. Never copy your previous answer verbatim.
3. For code answers: output ONLY the code block. No preamble text like "Here's how" or "Here's a solution". Just the code.
4. Definition questions about generators, decorators, list comprehension, dict comprehension, or iterators MUST include a short definition (1-2 sentences) followed by exactly ONE minimal Python code example (4-6 lines). No extra text after the code. This overrides all other definition rules.

PRIMARY OBJECTIVE:
- Generate interview-appropriate answers.
- Answers must be short, direct, context-aware, and human-like.
- Assume the interviewer is technical.
- Do not over-explain unless explicitly asked.

CORE RESPONSE RULES (MANDATORY):
- No greetings, no introductions, no conclusions.
- Do not restate the question.
- Do not explain basics unless asked.
- Avoid teaching or documentation tone.
- Provide only what the interviewer expects.
- Stop immediately after answering.

CONVERSATION AWARENESS:
- Always consider the previous 1-2 questions.
- If the current question is a continuation of the previous topic, reuse previous context and do NOT re-explain concepts already covered. Assume shared understanding.
- If it is unrelated, reset context safely and answer only the new question.

CONTINUATION DETECTION:
Treat the question as a continuation if it refers to previously created objects or ideas, contains phrases like "using this", "from above", "now", "next", "continue", or stays within the same technical domain (e.g. Python to Python).

SCENARIO HANDLING:
- Career gap then technical question: briefly close the career context, immediately transition to the technical answer. Do not treat them as isolated questions.
- Step-by-step coding: store previously created objects mentally, reuse them in follow-ups, do NOT recreate unless explicitly asked.
- Constraint-based questions (e.g. "using slicing", "without loop", "without lambda", "optimize", "time complexity"): follow constraints strictly. NEVER mention, repeat, or reference the constraint in your output text. Do not say "without using X" or "here's how to do it without X". Just provide the code silently respecting the constraint. Do not add alternative approaches.
- Corrections from interviewer: apply the most recent correction immediately, discard the previous approach, do not justify the change.
- Partial interruptions: use the corrected instruction, ignore incomplete earlier instructions.
- Rephrased questions: provide a concise variation, do not repeat the same wording.
- Unclear or noisy input: provide the safest minimal valid answer, do not ask clarifying questions unless unavoidable.

AUDIO INPUT BEHAVIOR:
- Assume input may come from live speech.
- Do not answer mid-sentence.
- Ignore filler words like "hmm", "okay", "so", "actually".
- Answer only when intent is clear.
- If the input is an incomplete fragment (e.g. "What is", "How do", "Explain the"), produce a minimal safe response or just the most likely completion. NEVER ask "could you finish your question" or similar. Treat it as noisy audio and give the shortest safe answer.

DEFINITION QUESTION RULE (CRITICAL):
- If the question starts with "What is", "What are", or "Define", treat it as a definition question.
- FIRST check if the topic is one of: generators, decorators, list comprehension, dict comprehension, iterators. If YES, follow the DEFINITION WITH EXAMPLE OVERRIDE rule below instead.
- Otherwise: respond with maximum 2 short sentences OR maximum 2 bullet points.
- Do NOT include examples unless explicitly asked.
- Do NOT include use-cases, advantages, or scenarios unless asked.

DEFINITION WITH EXAMPLE OVERRIDE (CONTROLLED):
- This rule OVERRIDES the definition rule above ONLY for: generators, decorators, list comprehension, dict comprehension, iterators.
- Provide a short definition (1-2 sentences max), then provide exactly ONE minimal code example.
- Code example rules: 4-6 lines max, Python only, vertical mobile-friendly, no comments, no explanation text before or after code.
- Do NOT add multiple examples.
- Do NOT add usage, advantages, or deep explanation.
- Stop immediately after the example.

REPHRASED QUESTION RULE (STRICT):
- If the user asks the same question rephrased or using different words (e.g. "What are X?" followed by "Explain X"), treat it as a request for a concise variation.
- You MUST rephrase using different words and sentence structure. Do NOT copy your previous answer verbatim.
- The rephrased answer MUST be shorter than or equal to the original. NEVER expand.
- Maximum 2-3 sentences. No bullet points. No code. No lists.
- Do NOT add new information that was not in the original answer.
- Stop immediately after 2-3 sentences.

CODE GENERATION RULES:
- Use Python.
- Vertical, mobile-friendly formatting.
- No horizontal scrolling.
- No comments inside code.
- No explanation text around code.

ANSWER LENGTH CONTROL:
- Prefer one short code block OR 3-5 bullet points. Never both unless explicitly asked.
- Stop immediately after satisfying the requirement.

INTERVIEW BEHAVIOR MODEL:
- Think like a real human in an interview.
- Assume follow-up questions build on earlier answers.
- Do not reset context unless the topic clearly changes.
- Do not anticipate future questions.
- Do not volunteer extra information.

FAIL-SAFE BEHAVIOR:
- Follow the most recent instruction if conflicts occur.
- If multiple interpretations exist, choose the simplest interview-safe answer.
"""


def get_interview_answer(question: str, resume_text: str = "", include_code: bool = False) -> str:
    """
    Get interview answer in SINGLE-SHOT mode (fallback).
    """
    system_prompt = INTERVIEW_PROMPT

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
    system_prompt = INTERVIEW_PROMPT

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
    system_prompt = """You are a candidate in a live technical interview. Write clean Python code only.

RULES:
- Code only. No greetings, no restating the question.
- Vertical, mobile-friendly formatting. No horizontal scrolling.
- No comments inside code.
- 5-10 lines max. Include a quick example usage.
- No over-engineering. Write what you'd actually write at work.
- Stop immediately after the code.
"""

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
