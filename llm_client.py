"""
LLM Client for Interview Voice Assistant

Optimized for:
- Minimal token usage (short system prompt)
- No conversation history (fresh session per question)
- Fast responses via streaming
- 10 second hard timeout
"""

import os
import time
from anthropic import Anthropic

try:
    import debug_logger as dlog
except ImportError:
    class DlogStub:
        def log(self, *args, **kwargs): pass
        def log_error(self, *args, **kwargs): pass
    dlog = DlogStub()

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    max_retries=0,   # 0 = fail fast (was 1 = 2x10s=20s total wait on timeout)
    timeout=12.0     # single attempt, 12s max
)

import config as _cfg
MODEL = os.environ.get("LLM_MODEL_OVERRIDE", _cfg.LLM_MODEL)

MAX_TOKENS_INTERVIEW = 130
MAX_TOKENS_CODING = 450
MAX_TOKENS_PLATFORM = 1200

TEMP_INTERVIEW = 0.4
TEMP_CODING = 0.1

INTERVIEW_PROMPT = """You are a senior engineer in a job interview. You ARE the person in the RESUME.

FORMAT: 3-4 bullet points ONLY. Each bullet is ONE simple sentence under 15 words.

EXAMPLE:
Q: What is Kubernetes architecture?
- Kubernetes has a master node and multiple worker nodes
- Master runs the API server, scheduler, and etcd for cluster state
- Worker nodes run your application pods managed by kubelet
- I've used it to deploy and scale microservices in production

Q: Difference between list and tuple?
- Lists are mutable so you can change them after creation
- Tuples are immutable and slightly faster for read-only data
- I use tuples for fixed configs and lists for dynamic collections

Q: How to deploy application in AWS?
- I typically use EC2 instances behind an Application Load Balancer
- The app is containerized with Docker and deployed via ECS or EKS
- We set up a CI/CD pipeline using CodePipeline or GitHub Actions
- CloudWatch handles monitoring and auto-scaling manages traffic spikes

RULES:
- ONLY 3-4 bullets. NEVER more than 4. NO sub-bullets or nested items.
- NO colons inside bullets. NO "such as:", "including:", "for example:". Just state it directly.
- NO paragraphs, NO preamble, NO "let's explain", NO analogies.
- NO bold, NO code blocks, NO scripts, NO YAML, NO commands, NO brackets, NO technical syntax.
- ABSOLUTELY NEVER include ```code```, script snippets, YAML, or command-line syntax. Describe steps in plain English only.
- If asked "how to deploy/set up/configure", describe the approach verbally, never write actual scripts or code.
- If question sounds garbled, guess the closest tech term and answer it.
- NEVER say "I don't have experience" or "There is no concept called".
- NEVER reveal you are AI."""


CODING_PROMPT = """You are a human software engineer writing code naturally during an interview.

CRITICAL: Write code like a REAL HUMAN, not AI. Interviewers can detect AI-generated code.

VARIABLE NAMING (HUMAN STYLE):
- Use SIMPLE, CASUAL names like real humans do:
  ✓ Good: arr, temp, res, result, ans, count, i, j, k, curr, prev
  ✓ Good: nums, words, s, n, m, total, val, key
  ✗ BAD (too AI-perfect): sorted_word, anagram_dict, word_list, input_string
  ✗ BAD (too descriptive): reversed_string, anagram_dictionary, character_count

FUNCTION NAMING (HUMAN STYLE):
- Keep it SHORT and simple:
  ✓ Good: find, check, get, solve, count, reverse
  ✗ BAD (too descriptive): find_anagrams, check_palindrome, get_even_numbers

EXAMPLES OF HUMAN CODE:

Problem: "Find anagram groups"
HUMAN CODE (what you should write):
def find(words):
    res = {}
    for w in words:
        key = ''.join(sorted(w))
        if key in res:
            res[key].append(w)
        else:
            res[key] = [w]
    return list(res.values())

AI CODE (NEVER write like this):
def find_anagrams(word_list):
    anagram_dict = {}
    for word in word_list:
        sorted_word = ''.join(sorted(word))
        if sorted_word in anagram_dict:
            anagram_dict[sorted_word].append(word)
        else:
            anagram_dict[sorted_word] = [word]
    return list(anagram_dict.values())

Problem: "Reverse a string"
HUMAN CODE:
def reverse(s):
    return s[::-1]

AI CODE (NEVER):
def reverse_string(input_string):
    reversed_string = input_string[::-1]
    return reversed_string

Problem: "Find even numbers"
HUMAN CODE:
def find(arr):
    return [x for x in arr if x % 2 == 0]

AI CODE (NEVER):
def find_even_numbers(number_list):
    even_numbers = [num for num in number_list if num % 2 == 0]
    return even_numbers

RULES:
- ZERO text/explanation before or after. Just code.
- NO comments. NO markdown fencing.
- SIMPLE variable names (arr, temp, res, i, j, k, n, m, s, w, key, val)
- SHORT function names (find, check, get, solve, count, reverse)
- 3-15 lines max (enough for robust logic).
- For Python: no `if __name__` block.
- Mix of styles (not perfectly consistent - humans aren't perfect!)
- For YAML/Ansible/Terraform/Groovy/Dockerfile: output the script directly.
- For SQL: output the query directly.

REMEMBER: Code should look like it was written by a human in 2-3 minutes, not AI-generated perfection!
"""


PLATFORM_PROMPT = """You are an expert competitive programmer. Output WORKING Python code that passes ALL test cases.

INTERNAL THINKING (DO NOT OUTPUT):
- Identify the problem type (DP, DFS, Greedy, etc.).
- Analyze constraints (N < 10^5 implies O(N) or O(N log N)).
- Consider edge cases (empty list, min/max values).
- Select the OPTIMAL solution.

CRITICAL FORMAT RULES (FOLLOW EXACTLY):
1. Output ONLY raw Python 3 code - absolutely NO explanations, NO "Here's the code", NO markdown
2. The VERY FIRST LINE must be 'def' or 'class' - NO text before code
3. Use EXACT function name from EDITOR_CONTENT
4. MUST use 4-SPACE INDENTATION for all nested code (this is critical!)
5. For Codewars/LeetCode: just the function definition, no main block
6. For HackerRank/Codility: include if __name__ == '__main__'
7. NO comments, NO print statements for debugging

WORD-TO-NUMBER CONVERSION (parse_int, words_to_int, etc.):
Use this EXACT pattern with PROPER INDENTATION:

def parse_int(string):
    nums = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
            'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
            'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
    words = string.replace('-', ' ').replace(' and ', ' ').split()
    total, current = 0, 0
    for word in words:
        if word in nums:
            current += nums[word]
        elif word == 'hundred':
            current *= 100
        elif word == 'thousand':
            current *= 1000
            total += current
            current = 0
        elif word == 'million':
            current *= 1000000
            total += current
            current = 0
        elif word == 'billion':
            current *= 1000000000
            total += current
            current = 0
    return total + current

KEY ALGORITHM INSIGHTS:
- "hundred": MULTIPLY current (current *= 100), do NOT add to total
- "thousand"/"million": SCALE then ADD to total, then RESET current
- This handles: "seven hundred eighty-three thousand" = (7*100+83)*1000 = 783000

OTHER PATTERNS:
- Array/List problems: Handle empty arrays, single element, negative numbers
- String problems: Handle empty string, single char, whitespace
- Math problems: Handle zero, negative, large numbers

REMEMBER: Every line inside a function MUST start with 4 spaces of indentation!
Output clean Python code only."""


import re

# Pre-compiled AI opener patterns
_OPENER_PATTERNS = [
    re.compile(r"^Sure,?\s*", re.IGNORECASE),
    re.compile(r"^(Great|Good|Excellent|Nice) question[.!,]?\s*", re.IGNORECASE),
    re.compile(r"^That's a (great|good|excellent) question[.!,]?\s*", re.IGNORECASE),
    re.compile(r"^Let me explain[.!,:]?\s*", re.IGNORECASE),
    re.compile(r"^(Certainly|Absolutely|Of course)[.!,]?\s*", re.IGNORECASE),
    re.compile(r"^Here'?s?\s*(the|my|a)?\s*(answer|explanation|breakdown|overview)?[.!,:]?\s*", re.IGNORECASE),
    re.compile(r"^(So|Well|Okay|Ok),?\s+", re.IGNORECASE),
    re.compile(r"^(I'd be happy to|Let me share|Allow me to|I'd like to)[.!,:]?\s*", re.IGNORECASE),
    re.compile(r"^Okay,?\s*(got it|understood|sure)[.!,]?\s*", re.IGNORECASE),
    re.compile(r"^(Ah,?\s*)?(I apologize|I'm sorry|My apologies)[^.]*\.\s*", re.IGNORECASE),
    re.compile(r"^Here are (some of )?(the )?(main |key )?(features|characteristics|benefits|advantages)[^:]*:\s*", re.IGNORECASE),
    re.compile(r"^(Let me|I'll) (provide|give) (you )?(a |an )?(general )?(overview|explanation|breakdown)[^.]*[.:]\s*", re.IGNORECASE),
    re.compile(r"^(Let'?s|Let me) explain[^:]*[:.]?\s*", re.IGNORECASE),
    re.compile(r"^(A |Here'?s a )?(concise|brief|short|quick) (explanation|overview|summary)[^:]*[:.]?\s*", re.IGNORECASE),
    re.compile(r"^Imagine[^.]*[.:]\s*", re.IGNORECASE),
    re.compile(r"^Think of[^.]*[.:]\s*", re.IGNORECASE),
    re.compile(r"^In (simple|plain) terms[,:]?\s*", re.IGNORECASE),
]

# Pre-compiled formatting patterns
_BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
_HEADER_RE = re.compile(r'^#{1,4}\s+', re.MULTILINE)
_BULLET_RE = re.compile(r'^\s*[-*•]\s+', re.MULTILINE)
_NUMBERED_RE = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)
_BOLD_HEADER_RE = re.compile(r'^\s*\*\*[^*]+\*\*\s*:?\s*$', re.MULTILINE)

_CODE_BLOCK_RE = re.compile(r'```[\s\S]*?(?:```|$)')
_INLINE_CODE_RE = re.compile(r'`([^`]+)`')
_HERES_EXAMPLE_RE = re.compile(r"Here'?s?\s*(an?\s*)?(simple\s*)?(example|code)[^:]*:\s*", re.IGNORECASE)
_FOR_EXAMPLE_RE = re.compile(r"For example[,:]?\s*", re.IGNORECASE)
_KEY_POINTS_RE = re.compile(r"Here are (the |some )?(key |main )?(points|things|features|characteristics)[^:]*:\s*", re.IGNORECASE)

# Pre-compiled AI identity leak patterns (compiled once at module load)
_AI_LEAK_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
    r"As an AI[^.]*\.\s*",
    r"I am an AI[^.]*\.\s*",
    r"I'?m an (AI|artificial)[^.]*\.\s*",
    r"I don'?t have a physical[^.]*\.\s*",
    r"I do not have a physical[^.]*\.\s*",
    r"created by Anthropic[^.]*\.\s*",
    r"I am an artificial intelligence[^.]*\.\s*",
    r"without a physical form[^.]*\.\s*",
    r"I cannot (participate|appear|be recorded)[^.]*\.\s*",
    r"I can only (respond|communicate|provide)[^.]*text[^.]*\.\s*",
    r"I (apologize|'m sorry|am sorry),?\s*(but\s*)?(I\s*)?(do not|don'?t|am not|cannot)[^.]*\.\s*",
    r"I'?m afraid[^.]*\.\s*",
    r"there seems to be (a |some )?misunderstanding[^.]*\.\s*",
    r"without (any )?more (specific )?details[^.]*\.\s*",
    r"I do not (actually )?have (any |direct )?(experience|information|knowledge|expertise)[^.]*\.\s*",
    r"I don'?t have (any |direct )?(experience|information|knowledge|expertise)[^.]*\.\s*",
    r"I (apologize|'m sorry),?\s*I misunderstood[^.]*\.\s*",
    r"However,?\s*I can provide[^.]*\.\s*",
    r"Could you please provide more context[^.]*\.\s*",
    r"I'?m not sure which[^.]*\.\s*",
    r"I haven'?t had the (opportunity|need|chance)[^.]*\.\s*",
    r"As a developer with \d+ years? of experience,?\s*",
    r"In my experience (working with|as a)[^,]*,\s*",
]]

def humanize_response(text: str) -> str:
    """Strip AI-style formatting to produce spoken-style plain text."""
    if not text:
        return text
    # Remove entire code blocks first (```...```)
    text = _CODE_BLOCK_RE.sub('', text)
    # Remove inline backticks but keep the text inside
    text = _INLINE_CODE_RE.sub(r'\1', text)
    # Strip AI openers
    for pattern in _OPENER_PATTERNS:
        text = pattern.sub('', text)
    # Strip "Here's an example:" and similar
    text = _HERES_EXAMPLE_RE.sub('', text)
    text = _FOR_EXAMPLE_RE.sub('', text)
    text = _KEY_POINTS_RE.sub('', text)
    # Remove bold-only header lines (e.g., "**Infrastructure Automation**")
    text = _BOLD_HEADER_RE.sub('', text)
    # Remove markdown headers (## Header)
    text = _HEADER_RE.sub('', text)
    # Remove bold markers but keep inner text
    text = _BOLD_RE.sub(r'\1', text)
    # KEEP bullet point markers (- ) since we want bullet format output
    # But remove numbered list markers (1. 2. 3.)
    text = _NUMBERED_RE.sub('- ', text)
    # Remove "Topic: explanation" patterns (e.g., "Memory Efficiency: Generators...")
    text = re.sub(r'(?m)^\s*[A-Z][A-Za-z\s/]+:\s+', '', text)
    # Remove label-colon in bullet lines (e.g., "- API Server: Exposes..." → "- API Server exposes...")
    text = re.sub(r'(?m)^(\s*-\s+[A-Za-z\s/]+):\s+', r'\1 ', text)
    # Remove trailing "such as:", "including:", "for example:" at end of bullets
    text = re.sub(r',?\s*(such as|including|for example|e\.g\.)\s*:?\s*$', '.', text, flags=re.MULTILINE | re.IGNORECASE)
    # Remove sub-bullets (indented bullets like "  - item")
    text = re.sub(r'(?m)^\s{2,}-\s+.*$', '', text)
    # Remove label-colon patterns mid-sentence (e.g., "Iterability: Generators are...")
    text = re.sub(r'(?<=[.!?])\s+[A-Z][A-Za-z\s/]{2,30}:\s+', ' ', text)
    # Remove e.g. patterns
    text = re.sub(r'\s*\(e\.g\.?\s*[^)]*\)', '', text)
    # Remove "etc." trailing (require comma before to avoid destroying words like "etcd")
    text = re.sub(r',\s+etc\.?\s*', '. ', text)
    # Remove standalone syntax symbols like [], (), {}, __method__() patterns
    text = re.sub(r'\s*\[\]\s*', ' ', text)
    text = re.sub(r'\s*\(\)\s*', ' ', text)
    text = re.sub(r'\s*\{\}\s*', ' ', text)
    text = re.sub(r'__\w+__\(\)', '', text)  # __enter__(), __exit__(), __init__()
    text = re.sub(r'__\w+__', '', text)  # __init__, __str__, etc.
    # Remove "Note that..." filler sentences
    text = re.sub(r'\(Note that[^)]*\)', '', text)
    text = re.sub(r'Note that[^.]*\.\s*', '', text)
    # Remove "It is important to note..." filler
    text = re.sub(r'It is important to (note|understand|remember)[^.]*\.\s*', '', text, flags=re.IGNORECASE)
    # Collapse multiple newlines but preserve single newlines for bullet format
    text = re.sub(r'\n{3,}', '\n', text)
    text = re.sub(r'\n\n', '\n', text)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    # Remove AI identity leaks and "I don't have experience" patterns (pre-compiled)
    for pattern in _AI_LEAK_PATTERNS:
        text = pattern.sub("", text)
    # Collapse spaces and periods after removals
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'^\s*[,.]\s*', '', text)
    text = text.strip()

    # Limit to max 4 bullet points (drop excess bullets)
    lines = text.split('\n')
    bullet_count = 0
    truncated_lines = []
    for line in lines:
        if line.strip().startswith('-'):
            bullet_count += 1
            if bullet_count > 4:
                break
        truncated_lines.append(line)
    text = '\n'.join(truncated_lines).strip()

    return text


def clear_session():
    """Clear any session state. Called between questions for isolation."""
    HISTORY.clear()



# Global conversation history (deque for O(1) popleft)
from collections import deque
HISTORY = deque(maxlen=3)

def get_interview_answer(question: str, resume_text: str = "", job_description: str = "", include_code: bool = False) -> str:
    """Single-shot interview answer with history context."""
    system_prompt = INTERVIEW_PROMPT

    if resume_text:
        system_prompt += f"\n\nYOUR RESUME (answer as this person):\n{resume_text}"

    if job_description:
        system_prompt += f"\n\nJOB DESCRIPTION (tailor answers to this):\n{job_description}"

    dlog.log(f"[LLM] Single-shot: {question[:60]}", "DEBUG")

    # Build messages with history
    messages = []
    for q, a in HISTORY:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": question})
    # Prefill to force bullet format (prevents preamble)
    messages.append({"role": "assistant", "content": "-"})

    try:
        api_start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_INTERVIEW,
            temperature=TEMP_INTERVIEW,
            system=system_prompt,
            messages=messages
        )
        api_time = time.time() - api_start
        answer = humanize_response("-" + response.content[0].text.strip())

        # Update history (deque auto-evicts oldest when full)
        HISTORY.append((question, answer))
            
        dlog.log(f"[LLM] Done: {len(answer)} chars in {api_time*1000:.0f}ms", "DEBUG")
        return answer

    except Exception as e:
        dlog.log_error("[LLM] Single-shot failed", e)
        return ""


def get_streaming_interview_answer(question: str, resume_text: str = "", job_description: str = ""):
    """Streaming interview answer with history context."""
    system_prompt = INTERVIEW_PROMPT

    if resume_text:
        system_prompt += f"\n\nYOUR RESUME (answer as this person):\n{resume_text}"

    if job_description:
        system_prompt += f"\n\nJOB DESCRIPTION (tailor answers to this):\n{job_description}"

    dlog.log(f"[LLM] Streaming: {question[:60]}", "DEBUG")
    stream_start = time.time()

    # Build messages with history
    messages = []
    for q, a in HISTORY:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": question})
    # Prefill to force bullet format
    messages.append({"role": "assistant", "content": "-"})

    full_answer = "-"
    try:
        yield "-"
        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS_INTERVIEW,
            temperature=TEMP_INTERVIEW,
            system=system_prompt,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                full_answer += text
                yield text

        # Update history after stream completes
        HISTORY.append((question, full_answer))
        if len(HISTORY) > MAX_HISTORY:
            HISTORY.pop(0)

        dlog.log(f"[LLM] Stream done in {(time.time() - stream_start)*1000:.0f}ms", "DEBUG")

    except Exception as e:
        dlog.log_error("[LLM] Stream failed", e)
        yield ""


def _clean_code_answer(text: str) -> str:
    """Strip any text preamble/explanation from code answers, keep only code."""
    if not text:
        return text
    # Remove markdown code fences
    text = re.sub(r'^```\w*\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    text = text.strip()
    # If starts with text preamble (not code), strip everything before first code line
    lines = text.split('\n')
    code_start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith('def ') or stripped.startswith('class ') or
            stripped.startswith('import ') or stripped.startswith('from ') or
            stripped.startswith('if ') or stripped.startswith('for ') or
            stripped.startswith('while ') or stripped.startswith('#') or
            re.match(r'^[a-z_]\w*\s*=', stripped) or
            stripped.startswith('- hosts:') or stripped.startswith('- hosts ') or
            stripped.startswith('- name:') or stripped.startswith('---') or
            # Terraform patterns
            stripped.startswith('provider ') or stripped.startswith('resource ') or
            stripped.startswith('variable ') or stripped.startswith('output ') or
            stripped.startswith('terraform {') or stripped.startswith('data ') or
            stripped.startswith('module ') or stripped.startswith('locals {') or
            # Dockerfile patterns
            stripped.startswith('FROM ') or stripped.startswith('RUN ') or
            stripped.startswith('COPY ') or stripped.startswith('CMD ') or
            stripped.startswith('WORKDIR ') or stripped.startswith('EXPOSE ') or
            # SQL patterns
            stripped.upper().startswith('SELECT ') or stripped.upper().startswith('CREATE ') or
            stripped.upper().startswith('INSERT ') or stripped.upper().startswith('ALTER ') or
            # Groovy/Jenkins
            stripped.startswith('pipeline {') or stripped.startswith('node {') or
            stripped.startswith('stage(')):
            code_start_idx = i
            break
    if code_start_idx > 0:
        text = '\n'.join(lines[code_start_idx:]).strip()
    # Remove trailing explanation text after the code
    final_lines = []
    code_ended = False
    for line in text.split('\n'):
        if code_ended:
            break
        # If we hit an empty line after code, check if next line looks like text
        if not line.strip() and final_lines:
            final_lines.append(line)
            continue
        # Text explanation lines (no indentation, starts with "This", "Here", "The", etc.)
        if (final_lines and not line.startswith(' ') and not line.startswith('\t') and
            re.match(r'^(This|Here|The|It|Note|Output|Example|Usage|How|You)', line)):
            break
        final_lines.append(line)
    # Remove trailing empty lines
    while final_lines and not final_lines[-1].strip():
        final_lines.pop()
    return '\n'.join(final_lines)


def get_coding_answer(question: str) -> str:
    """Single-shot coding answer. Clean executable Python only."""
    dlog.log(f"[LLM] Coding: {question[:60]}", "DEBUG")

    try:
        api_start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_CODING,
            temperature=TEMP_CODING,
            system=CODING_PROMPT,
            messages=[{"role": "user", "content": question}]
        )
        answer = _clean_code_answer(response.content[0].text.strip())
        dlog.log(f"[LLM] Coding done: {len(answer)} chars in {(time.time() - api_start)*1000:.0f}ms", "DEBUG")
        return answer

    except Exception as e:
        dlog.log_error("[LLM] Coding failed", e)
        return ""


def get_platform_solution(problem_text: str, editor_content: str = "", url: str = "") -> str:
    """Generate solution for coding platforms (##start mode)."""
    dlog.log(f"[LLM] Platform solve: {url[:40]}", "DEBUG")

    user_content = f"URL: {url}\n\nEDITOR_CONTENT:\n{editor_content}\n\nPROBLEM_TEXT:\n{problem_text}"

    try:
        api_start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS_PLATFORM,
            temperature=0.0,
            system=PLATFORM_PROMPT,
            messages=[{"role": "user", "content": user_content}]
        )

        answer = response.content[0].text.strip()

        # Strip common LLM explanation phrases
        unwanted_prefixes = [
            "Here's the Python code",
            "Here is the Python code",
            "Here's the code",
            "Here is the code",
            "Here's my solution",
            "Here is my solution",
            "The solution is",
            "Below is the",
            "This code",
        ]
        for prefix in unwanted_prefixes:
            if answer.lower().startswith(prefix.lower()):
                # Find where the actual code starts (after : or newline)
                idx = answer.find(':')
                if idx != -1 and idx < 100:
                    answer = answer[idx+1:].strip()
                else:
                    idx = answer.find('\n')
                    if idx != -1:
                        answer = answer[idx+1:].strip()
                break

        if answer.startswith("```"):
            answer = answer.split("\n", 1)[1] if "\n" in answer else answer
        if answer.endswith("```"):
            answer = answer.rsplit("\n", 1)[0] if "\n" in answer else answer
        # Also handle ```python specifically
        if answer.startswith("```python"):
            answer = answer[9:].strip()

        lines = answer.split('\n')
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('#!'):
                continue
            if '#' in line and "'" not in line and '"' not in line:
                line = line.split('#')[0].rstrip()
            clean_lines.append(line)

        answer = '\n'.join(clean_lines).strip()
        dlog.log(f"[LLM] Platform done: {len(answer)} chars in {(time.time() - api_start)*1000:.0f}ms", "DEBUG")
        return answer

    except Exception as e:
        dlog.log_error("[LLM] Platform failed", e)
        return ""
