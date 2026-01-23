#!/usr/bin/env python3
"""
Diagnostic test for multiple interview scenarios:
1. Greeting ("Hello")
2. Soft skill ("Tell me about yourself")
3. Technical + Phonetical ("Concept of in it in Python")
4. Technical ("Difference between list and tuple")
"""

import os
import sys

# Ensure models are loaded or mocked for the test
# For this test, we'll call the functions directly to see their output

from question_validator import clean_and_validate
from llm_client import get_interview_answer

scenarios = [
    {
        "name": "Social Greeting",
        "input": "Hi how are you today",
        "should_pass": True
    },
    {
        "name": "Social Personal",
        "input": "Where are you from",
        "should_pass": True
    },
    {
        "name": "Soft Skill",
        "input": "Can you tell me a little bit about yourself",
        "should_pass": True
    },
    {
        "name": "Phonetic Technical",
        "input": "Explain the in it method in Python",
        "should_pass": True
    },
    {
        "name": "Technical Fragment",
        "input": "Generators in Python",
        "should_pass": True
    },
    {
        "name": "Gap Picking Fix",
        "input": "What is gap picking in Python",
        "should_pass": True
    },
    {
        "name": "Resume Specific",
        "input": "Tell me about your experience at MediaMint",
        "should_pass": True
    },
    {
        "name": "Technical Mishearing",
        "input": "What is the translation in Python",
        "should_pass": True
    },
    {
        "name": "Noise (Should Reject)",
        "input": "And then we go to the next slide",
        "should_pass": False
    }
]

print("=" * 80)
print(f"{'SCENARIO TEST SUITE':^80}")
print("=" * 80)

if not os.environ.get("ANTHROPIC_API_KEY"):
    print("\n[SKIP] API Tests (Key missing)")
else:
    for s in scenarios:
        print(f"\n[TEST] {s['name']} -> \"{s['input']}\"")
        is_valid, cleaned, reason = clean_and_validate(s['input'])
        
        if is_valid:
            print(f"  ✓ Validated: \"{cleaned}\"")
            if s['should_pass']:
                print(f"  ... Getting LLM response ...")
                answer = get_interview_answer(cleaned)
                print(f"  [RESULT]:\n{'-'*40}\n{answer}\n{'-'*40}")
            else:
                print(f"  ❌ FAILED: Should have been rejected but passed.")
        else:
            print(f"  ❌ Rejected: {reason}")
            if not s['should_pass']:
                print(f"  ✓ Correctly rejected.")
            else:
                print(f"  ❌ FAILED: Should have been accepted.")

print("\n" + "=" * 80)
