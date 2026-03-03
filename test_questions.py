#!/usr/bin/env python3
"""
Test script to submit interview questions and verify responses
"""

import os
import sys

# Ensure API key is set
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("❌ ANTHROPIC_API_KEY not set")
    sys.exit(1)

import answer_storage
import config
from llm_client import stream_coding_answer, stream_with_resume
from resume_loader import load_resume as load_resume_file
from intent_detector import is_coding_question

def load_resume():
    """Load resume from file"""
    try:
        return load_resume_file(config.RESUME_PATH)
    except:
        return "4+ years Python developer experience"

def test_question(question):
    """Submit a question and get response"""
    print(f"\n{'='*60}")
    print(f"QUESTION: {question}")
    print('='*60)

    # Start new answer
    answer_storage.start_new_answer(question)

    full_response = ""

    # Determine question type and stream response
    if is_coding_question(question):
        print("[Type: CODING]")
        for chunk in stream_coding_answer(question):
            print(chunk, end='', flush=True)
            full_response += chunk
            answer_storage.append_answer_chunk(chunk)
    else:
        print("[Type: GENERAL]")
        resume = load_resume()
        for chunk in stream_with_resume(question, resume):
            print(chunk, end='', flush=True)
            full_response += chunk
            answer_storage.append_answer_chunk(chunk)

    # Finalize answer
    answer_storage.finalize_answer()

    print(f"\n{'='*60}")
    return full_response

def main():
    # Clear previous answers
    print("Clearing previous answers...")
    answer_storage.clear_answers()

    # Test questions
    questions = [
        "How do you swap two numbers in Python?",
        "What is Pickling in Python?"
    ]

    for q in questions:
        test_question(q)
        print("\n")

    # Show final state
    print("\n" + "="*60)
    print("FINAL STORED ANSWERS:")
    print("="*60)
    answers = answer_storage.get_all_answers()
    for i, qa in enumerate(answers):
        print(f"\n[{i+1}] Q: {qa['question']}")
        print(f"    A: {qa['answer'][:100]}...")

    print(f"\n✅ Test complete. Check http://localhost:8000/ to see the UI")

if __name__ == "__main__":
    main()
