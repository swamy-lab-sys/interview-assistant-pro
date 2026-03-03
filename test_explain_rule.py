"""
Test CONCEPT EXPLANATION RULE - "Explain" questions must be concise.
Max 3 sentences or 3 bullet points. No paragraphs. No code unless asked.
"""

import os
import sys
import time

# Ensure API key is available
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set")
    sys.exit(1)

from llm_client import get_interview_answer

SCENARIOS = [
    {
        "id": 1,
        "name": "Explain metaclass",
        "question": "Explain the concept of a meta class",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 2,
        "name": "Explain method overriding",
        "question": "Explain the concept of method overriding",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 3,
        "name": "Explain abstract class",
        "question": "Explain the concept of an abstract class",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 4,
        "name": "Explain how closures work",
        "question": "Explain how closures work in Python",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 5,
        "name": "Explain polymorphism",
        "question": "Explain polymorphism",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 6,
        "name": "Explain MRO",
        "question": "Explain the method resolution order in Python",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 7,
        "name": "Explain GIL",
        "question": "Explain the GIL in Python",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
    {
        "id": 8,
        "name": "Explain context managers",
        "question": "Explain how context managers work",
        "checks": {
            "max_sentences": 3,
            "no_code": True,
            "no_paragraphs": True,
        }
    },
]


def count_sentences(text):
    """Count sentences (split on . ! ? but ignore code)."""
    clean = text.strip()
    if not clean:
        return 0
    # Remove code blocks
    import re
    clean = re.sub(r'```[\s\S]*?```', '', clean)
    clean = re.sub(r'`[^`]+`', '', clean)
    # Split on sentence endings
    sentences = re.split(r'[.!?]+', clean)
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def has_code_block(text):
    return '```' in text or '    ' in text or 'def ' in text or 'class ' in text


def has_paragraphs(text):
    """Check if response has multiple paragraphs (double newline separated blocks)."""
    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
    return len(blocks) > 2


def count_bullets(text):
    import re
    return len(re.findall(r'^[\s]*[-•*]\s', text, re.MULTILINE))


def run_tests():
    passed = 0
    failed = 0
    results = []

    for scenario in SCENARIOS:
        sid = scenario["id"]
        name = scenario["name"]
        question = scenario["question"]
        checks = scenario["checks"]

        print(f"\n{'='*60}")
        print(f"Scenario {sid}: {name}")
        print(f"Q: {question}")
        print(f"{'='*60}")

        answer = get_interview_answer(question)
        print(f"\nA: {answer}")

        # Run checks
        issues = []

        num_sentences = count_sentences(answer)
        max_s = checks.get("max_sentences", 3)
        num_bullets = count_bullets(answer)

        # Allow 3 sentences OR 3 bullets
        if num_sentences > max_s and num_bullets == 0:
            issues.append(f"Too many sentences: {num_sentences} (max {max_s})")
        if num_bullets > 3:
            issues.append(f"Too many bullets: {num_bullets} (max 3)")

        if checks.get("no_code") and has_code_block(answer):
            issues.append("Contains code block (not asked for)")

        if checks.get("no_paragraphs") and has_paragraphs(answer):
            issues.append("Contains multiple paragraphs")

        # Length check - concise answers should be under 400 chars
        if len(answer) > 500:
            issues.append(f"Too long: {len(answer)} chars (expected <500)")

        if issues:
            failed += 1
            status = "FAIL"
            print(f"\n  Result: FAIL")
            for issue in issues:
                print(f"    - {issue}")
        else:
            passed += 1
            status = "PASS"
            print(f"\n  Result: PASS ({num_sentences} sentences, {len(answer)} chars)")

        results.append((sid, name, status, issues))
        time.sleep(0.5)  # Rate limit

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{passed+failed} passed")
    print(f"{'='*60}")
    for sid, name, status, issues in results:
        mark = "PASS" if status == "PASS" else "FAIL"
        print(f"  [{mark}] Scenario {sid}: {name}")
        if issues:
            for issue in issues:
                print(f"         - {issue}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
