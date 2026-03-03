#!/usr/bin/env python3
"""
Test for Multi-Modal Scenario: Chat + Voice Merging
---------------------------------------------------
Scenario:
1. Interviewer types in Chat: "Find longest substring"
2. Interviewer says in Voice: "without repeating characters"
3. System must merge them into: "Find longest substring without repeating characters"
"""

import time
import fragment_context
from llm_client import get_coding_answer
from question_validator import validate_question

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def test_chat_voice_merge():
    print(f"\n{CYAN}{'='*60}")
    print(f"SCENARIO: Chat Context + Voice Instruction")
    print(f"{'='*60}{RESET}")

    # Step 1: Chat Input (Simulated from Chrome Extension)
    chat_input = "Find longest substring"
    print(f"\n[Time 0s] {YELLOW}Interviewer types in CHAT:{RESET} '{chat_input}'")
    
    # Save to context
    fragment_context.save_context(chat_input, "chat")
    print(f"{GREEN}✓ Context Saved: [CHAT] {chat_input}{RESET}")

    time.sleep(1)

    # Step 2: Voice Input (Simulated from Mic)
    voice_input = "without repeating characters"
    print(f"\n[Time +2s] {YELLOW}Interviewer says in VOICE:{RESET} '{voice_input}'")
    
    # Attempt Merge
    print(f"System merging process...")
    merged_text, was_merged = fragment_context.merge_with_context(voice_input)
    
    if was_merged:
        print(f"{GREEN}✓ MERGE SUCCESSFUL!{RESET}")
        print(f"Final Question: {CYAN}'{merged_text}'{RESET}")
    else:
        print(f"{RED}❌ Merge Failed.{RESET}")
        return

    # Step 3: Solve the merged question
    print(f"\n{YELLOW}[Internal Thinking] Solving merged question...{RESET}")
    solution = get_coding_answer(merged_text)
    
    print(f"\n{CYAN}--- GENERATED SOLUTION ---{RESET}")
    print(solution)
    print(f"{CYAN}--------------------------{RESET}")

if __name__ == "__main__":
    # Clear any old context first
    fragment_context.clear_context()
    test_chat_voice_merge()
