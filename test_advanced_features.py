#!/usr/bin/env python3
"""
Advanced Multimodal & Phonetic Correction Test
----------------------------------------------
Tests:
1. Data + Instruction Merge: Chat "[1..8]" + Voice "find even numbers"
2. Phonetic Correction: "What is CA CD" -> "What is CI/CD"
3. Slow Speech Simulation: Fragmentation test
"""

import time
import fragment_context
from question_validator import validate_question
from llm_client import get_coding_answer

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def test_data_merge():
    print(f"\n{CYAN}{'='*60}")
    print(f"SCENARIO 1: Data (Chat) + Instruction (Voice)")
    print(f"{'='*60}{RESET}")

    # 1. Chat Context (The Data)
    chat_data = "Here is the list: [1, 2, 3, 4, 5, 6, 7, 8]"
    print(f"User types in Chat: '{chat_data}'")
    fragment_context.save_context(chat_data, "chat")

    time.sleep(1)

    # 2. Voice Instruction
    voice_inst = "Identify the even numbers"
    print(f"User says in Voice: '{voice_inst}'")
    
    # Merge
    merged, success = fragment_context.merge_with_context(voice_inst)
    if success:
        print(f"{GREEN}✓ Merged Result: '{merged}'{RESET}")
    else:
        print(f"{RED}❌ Merge Failed{RESET}")

def test_phonetic_fix():
    print(f"\n{CYAN}{'='*60}")
    print(f"SCENARIO 2: Phonetic Correction (Misheard Tech Terms)")
    print(f"{'='*60}{RESET}")
    
    bad_input = "What is CA CD pipeline?"
    print(f"Raw Input: '{bad_input}'")
    
    is_valid, cleaned, reason = validate_question(bad_input)
    print(f"Validator Output: '{cleaned}'")
    
    if "CI CD" in cleaned or "CI/CD" in cleaned:
        print(f"{GREEN}✓ Correction Successful: CA CD -> CI/CD{RESET}")
    else:
        print(f"{RED}❌ Correction Failed{RESET}")

def test_slow_speech_fragment():
    print(f"\n{CYAN}{'='*60}")
    print(f"SCENARIO 3: Slow Speech Fragmentation")
    print(f"{'='*60}{RESET}")
    
    # Simulate first fragment arriving
    frag1 = "Create a list from 1 to 10"
    print(f"Fragment 1: '{frag1}'")
    fragment_context.save_context(frag1, "voice")
    
    time.sleep(1)
    
    # Simulate second fragment arriving after pause
    frag2 = "then find the even numbers"
    print(f"Fragment 2 (after pause): '{frag2}'")
    
    merged, success = fragment_context.merge_with_context(frag2)
    print(f"Merged Result: '{merged}'")

if __name__ == "__main__":
    test_data_merge()
    test_phonetic_fix()
    test_slow_speech_fragment()
