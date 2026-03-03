#!/usr/bin/env python3
"""
Python Interview Simulation
---------------------------
Simulates a real technical interview flow to test the "Human-Like" capabilities.
Scenarios covered:
1. Conceptual (Deep Dive)
2. Internal/Low-Level (Memory, GIL)
3. Architecture/Scenario (Trade-offs)
4. Coding (Algorithm & Scripting)
5. Behavioral (Experience)

Usage:
    export ANTHROPIC_API_KEY=your_key
    python3 simulate_python_interview.py
"""

import os
import sys
import time
from question_validator import is_code_request, validate_question
from llm_client import get_interview_answer, get_coding_answer

# ANSI Colors for readability
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Mock Resume Context
RESUME_CONTEXT = """
Senior Backend Engineer with 5 years of experience.
Expertise: Python, Django, PostgreSQL, Docker, AWS.
Project: Built a high-traffic e-commerce API serving 1M users.
"""

def type_effect(text, delay=0.01):
    """simulate typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def header(text):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN} INTERVIEWER: {text}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def simulate_interaction(category, question):
    header(f"[{category}] {question}")
    
    # 1. Validation & Analysis
    print(f"{YELLOW}[Internal Thinking] Analyzing intent...{RESET}")
    is_valid, cleaned, reason = validate_question(question)
    
    if not is_valid:
        print(f"{RED}❌ Question Rejected: {reason}{RESET}")
        return

    wants_code = is_code_request(question)
    intent = "CODING" if wants_code else "CONCEPTUAL/SCENARIO"
    print(f"{YELLOW}[Internal Thinking] Intent detected: {intent}{RESET}")
    
    # 2. Generation
    start_time = time.time()
    print(f"{YELLOW}[Internal Thinking] formulations Answer...{RESET} ", end="", flush=True)
    
    try:
        if wants_code:
            answer = get_coding_answer(question)
        else:
            answer = get_interview_answer(question, resume_text=RESUME_CONTEXT)
        
        duration = time.time() - start_time
        print(f"({duration:.1f}s)")
        
        # 3. Output
        print(f"\n{GREEN}{BOLD}CANDIDATE (You):{RESET}")
        if wants_code:
            print(f"{RESET}{answer}{RESET}")
        else:
            type_effect(answer, delay=0.005)
            
    except Exception as e:
        print(f"\n{RED}Error generating answer: {e}{RESET}")

def main():
    print(f"{BOLD}Starting Python Interview Simulation...{RESET}")
    # Load .env explicitly if needed
    if not os.environ.get("ANTHROPIC_API_KEY"):
         # Try loading from .env manually just in case
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{RED}Error: ANTHROPIC_API_KEY not found.{RESET}")
        return

    scenarios = [
        ("Core Concept", "What is the difference between list and tuple in Python?"),
        ("Internals", "How does Python handle memory management? Explain garbage collection."),
        ("Scenario/Design", "I have a slow API endpoint in Django. How would you debug and optimize it?"),
        ("Coding (Algo)", "Write a Python function to check if a string is a palindrome."),
        ("Behavioral", "Tell me about a time you made a technical mistake causing production issues.")
    ]
    
    for category, question in scenarios:
        simulate_interaction(category, question)
        time.sleep(1)  # Pause between questions for realism

if __name__ == "__main__":
    main()
