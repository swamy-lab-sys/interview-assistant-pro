#!/usr/bin/env python3
"""
Edge Case Testing for Conflict Detection
----------------------------------------
Tests specific scenarios where the merging logic might fail or be too aggressive.

Scenarios:
1. [Conflict] Chat has Code, Voice asks UNRELATED question. (Should NOT merge)
2. [Chain] Three fragments: "Create list" -> "filter odd" -> "sum them". (Should merge all)
3. [Correction] "Find index of 5" -> "Find index of 10". (Should REPLACE, not append)
4. [Ambiguity] "See eye see dee" (Phonetic check)
"""

import time
import fragment_context
from question_validator import validate_question

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_result(name, result, expected_contain, should_not_contain=None):
    print(f"\n{CYAN}TEST: {name}{RESET}")
    print(f"Result: '{result}'")
    
    success = True
    if expected_contain and expected_contain not in result:
        print(f"{RED}❌ FAILED: Missing '{expected_contain}'{RESET}")
        success = False
    
    if should_not_contain and should_not_contain in result:
        print(f"{RED}❌ FAILED: Should NOT contain '{should_not_contain}'{RESET}")
        success = False
        
    if success:
        print(f"{GREEN}✓ PASSED{RESET}")

def test_unrelated_merge():
    # Scenario 1: Chat has code, Voice is unrelated
    chat_context = "def foo(): return 1"
    fragment_context.save_context(chat_context, "chat")
    time.sleep(0.1)
    
    voice_input = "Tell me about yourself"
    merged, _ = fragment_context.merge_with_context(voice_input)
    
    # Expectation: Should NOT merge "def foo" with "Tell me about yourself"
    print_result("Unrelated Voice Input", merged, "Tell me about yourself", "def foo")


def test_chain_merge():
    # Scenario 2: Chaining 3 fragments
    # 1. "Create a list of numbers"
    fragment_context.save_context("Create a list of numbers", "voice")
    time.sleep(0.1)
    
    # 2. "then filter out odd ones" (Should merge with 1)
    merged_1, _ = fragment_context.merge_with_context("then filter out odd ones")
    fragment_context.save_context(merged_1, "voice") # System saves the result
    time.sleep(0.1)
    
    # 3. "and finally sum them" (Should merge with 1+2)
    merged_2, _ = fragment_context.merge_with_context("and finally sum them")
    
    print_result("Chain Merging", merged_2, "Create a list", "sum them")
    print_result("Chain Merging (Middle)", merged_2, "filter out odd")


def test_correction_overlap():
    # Scenario 3: Correction
    fragment_context.save_context("Find the index of number 5", "voice")
    time.sleep(0.1)
    
    # User corrects themselves
    voice_input = "Find the index of number 10"
    
    merged, _ = fragment_context.merge_with_context(voice_input)
    
    # Expectation: Should be JUST "Find the index of number 10", NOT "Find the index of number 5 Find the index of number 10"
    if "number 5" not in merged and "number 10" in merged:
        print(f"\n{CYAN}TEST: Correction Overlap{RESET}\n{GREEN}✓ PASSED: Replaced correctly '{merged}'{RESET}")
    else:
        print(f"\n{CYAN}TEST: Correction Overlap{RESET}\n{RED}❌ FAILED: '{merged}'{RESET}")

def test_phonetic_ambiguity():
    # Scenario 4: "See eye see dee"
    input_text = "how to implement see eye see dee pipeline"
    _, cleaned, _ = validate_question(input_text)
    
    print_result("Phonetic 'See Eye See Dee'", cleaned, "CI/CD", "see eye")

if __name__ == "__main__":
    test_unrelated_merge()
    test_chain_merge()
    test_correction_overlap()
    test_phonetic_ambiguity()
