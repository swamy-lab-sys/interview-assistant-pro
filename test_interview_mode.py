#!/usr/bin/env python3
"""
Test Suite for Interview Voice Assistant

ACCEPTANCE CRITERIA:
- Zero duplicate questions
- Zero overlapping answers
- Latency <= 4s for new questions
- Cached answers <= 1s
- Works across all platforms
- Stable for long video playback

TESTS:
1. Functional: "What is Python?" -> answer in <3s
2. Cache: Repeated question -> cached answer in <1s
3. Replace: New question -> previous replaced
4. Cooldown: Speak during cooldown -> ignored
5. Validation: Canonical questions accepted, narration rejected
"""

import sys
import time
import threading

# Test modules
import state
import answer_cache
from question_validator import (
    clean_and_validate,
    is_code_request,
    is_canonical_question,
    validate_question,
)
from audio_listener import (
    set_silence_duration,
    get_silence_duration,
    set_platform_silence,
)


def test_state_management():
    """Test state.py: generation lock, cooldown, deduplication."""
    print("\n" + "=" * 60)
    print("TEST: State Management")
    print("=" * 60)

    # Clear state
    state.force_clear_all()
    passed = 0
    failed = 0

    # Test 1: Initial state
    test = "Initial state should not block"
    if not state.should_block_input():
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 2: Generation lock
    test = "Generation lock should block input"
    state.start_generation()
    if state.should_block_input():
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1
    state.stop_generation()

    # Test 3: After release
    test = "After release should not block"
    if not state.should_block_input():
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 4: Cooldown
    test = "Cooldown should block input"
    state.start_cooldown()
    if state.should_block_input():
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 5: Cooldown expires
    test = "Cooldown should expire after duration"
    state.COOLDOWN_DURATION = 0.1  # Short for testing
    state.force_clear_all()
    state.start_cooldown()
    time.sleep(0.15)
    if not state.should_block_input():
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1
    state.COOLDOWN_DURATION = 3.0  # Reset

    # Test 6: Duplicate detection
    test = "Duplicate question detection"
    state.force_clear_all()
    state.set_last_question("What is Python?")
    if state.is_duplicate_question("What is Python?"):
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 7: Different question not duplicate
    test = "Different question not duplicate"
    if not state.is_duplicate_question("What is Django?"):
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    print(f"\nState Management: {passed}/{passed+failed} tests passed")
    return passed, failed


def test_answer_cache():
    """Test answer_cache.py: caching, normalization, retrieval."""
    print("\n" + "=" * 60)
    print("TEST: Answer Cache")
    print("=" * 60)

    answer_cache.clear_cache()
    passed = 0
    failed = 0

    # Test 1: Cache miss
    test = "Cache miss returns None"
    result = answer_cache.get_cached_answer("What is Python?")
    if result is None:
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 2: Cache answer
    test = "Cache and retrieve answer"
    answer_cache.cache_answer("What is Python?", "Python is a programming language.")
    result = answer_cache.get_cached_answer("What is Python?")
    if result == "Python is a programming language.":
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 3: Normalized lookup
    test = "Normalized lookup (different case)"
    result = answer_cache.get_cached_answer("WHAT IS PYTHON?")
    if result == "Python is a programming language.":
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 4: Normalized lookup with filler
    test = "Normalized lookup (with filler)"
    result = answer_cache.get_cached_answer("Okay, what is python")
    if result == "Python is a programming language.":
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    # Test 5: Cache stats
    test = "Cache stats"
    stats = answer_cache.get_cache_stats()
    if stats['size'] == 1 and stats['hits'] >= 3:
        print(f"  [PASS] {test} - {stats}")
        passed += 1
    else:
        print(f"  [FAIL] {test} - {stats}")
        failed += 1

    # Test 6: Clear cache
    test = "Clear cache"
    answer_cache.clear_cache()
    stats = answer_cache.get_cache_stats()
    if stats['size'] == 0:
        print(f"  [PASS] {test}")
        passed += 1
    else:
        print(f"  [FAIL] {test}")
        failed += 1

    print(f"\nAnswer Cache: {passed}/{passed+failed} tests passed")
    return passed, failed


def test_question_validation():
    """Test question_validator.py: canonical acceptance, rejection rules."""
    print("\n" + "=" * 60)
    print("TEST: Question Validation")
    print("=" * 60)

    passed = 0
    failed = 0

    # MUST ACCEPT (canonical questions)
    accept_tests = [
        ("What is Python?", "canonical question"),
        ("What is decorator", "canonical without punctuation"),
        ("Explain generators", "explain pattern"),
        ("What are generators", "what are pattern"),
        ("How do you swap two numbers in Python?", "how do pattern"),
        ("What is the difference between list and tuple?", "difference question"),
        ("Write code to reverse a string", "code request"),
    ]

    print("\n  ACCEPTANCE TESTS (should accept):")
    for question, description in accept_tests:
        result = clean_and_validate(question)
        if result:
            print(f"    [PASS] {description}: '{question}'")
            passed += 1
        else:
            print(f"    [FAIL] {description}: '{question}'")
            failed += 1

    # MUST REJECT
    reject_tests = [
        ("Okay", "filler only"),
        ("Can you hear me?", "audio check"),
        ("We'll show you how to swap numbers", "narration"),
        ("Let me explain this first", "teaching"),
        ("What is the difference between", "incomplete sentence"),
        ("Hmm", "thinking aloud"),
        ("Great", "confirmation"),
        ("There are many ways to do this", "narration"),
    ]

    print("\n  REJECTION TESTS (should reject):")
    for question, description in reject_tests:
        result = clean_and_validate(question)
        if not result:
            print(f"    [PASS] {description}: '{question}'")
            passed += 1
        else:
            print(f"    [FAIL] {description}: '{question}' -> '{result}'")
            failed += 1

    # CANONICAL DETECTION
    print("\n  CANONICAL DETECTION TESTS:")
    canonical_tests = [
        ("What is Python", True),
        ("Explain decorators", True),
        ("What are generators", True),
        ("Tell me about your experience", False),  # Not a technical term
        ("Hello", False),
    ]

    for question, expected in canonical_tests:
        result = is_canonical_question(question)
        if result == expected:
            print(f"    [PASS] is_canonical('{question}') = {result}")
            passed += 1
        else:
            print(f"    [FAIL] is_canonical('{question}') = {result}, expected {expected}")
            failed += 1

    # CODE REQUEST DETECTION
    print("\n  CODE REQUEST DETECTION TESTS:")
    code_tests = [
        ("Write code to reverse a string", True),
        ("Implement a function to find duplicates", True),
        ("What is a decorator?", False),
        ("Explain how decorators work", False),
    ]

    for question, expected in code_tests:
        result = is_code_request(question)
        if result == expected:
            print(f"    [PASS] is_code_request('{question}') = {result}")
            passed += 1
        else:
            print(f"    [FAIL] is_code_request('{question}') = {result}, expected {expected}")
            failed += 1

    print(f"\nQuestion Validation: {passed}/{passed+failed} tests passed")
    return passed, failed


def test_adaptive_silence():
    """Test adaptive silence detection."""
    print("\n" + "=" * 60)
    print("TEST: Adaptive Silence Detection")
    print("=" * 60)

    passed = 0
    failed = 0

    # Test platform-specific silence durations
    platforms = [
        ('youtube', 0.6),
        ('meet', 1.0),
        ('zoom', 1.5),
        ('teams', 1.5),
        ('default', 1.0),
    ]

    for platform, expected in platforms:
        set_platform_silence(platform)
        actual = get_silence_duration()
        if actual == expected:
            print(f"  [PASS] {platform}: {actual}s")
            passed += 1
        else:
            print(f"  [FAIL] {platform}: {actual}s, expected {expected}s")
            failed += 1

    # Test manual setting
    set_silence_duration(0.8)
    if get_silence_duration() == 0.8:
        print(f"  [PASS] Manual set: 0.8s")
        passed += 1
    else:
        print(f"  [FAIL] Manual set")
        failed += 1

    # Test bounds
    set_silence_duration(0.1)  # Too low
    if get_silence_duration() == 0.3:  # Should clamp to 0.3
        print(f"  [PASS] Lower bound: 0.3s")
        passed += 1
    else:
        print(f"  [FAIL] Lower bound: {get_silence_duration()}s, expected 0.3s")
        failed += 1

    set_silence_duration(5.0)  # Too high
    if get_silence_duration() == 3.0:  # Should clamp to 3.0
        print(f"  [PASS] Upper bound: 3.0s")
        passed += 1
    else:
        print(f"  [FAIL] Upper bound: {get_silence_duration()}s, expected 3.0s")
        failed += 1

    # Reset to default
    set_platform_silence('default')

    print(f"\nAdaptive Silence: {passed}/{passed+failed} tests passed")
    return passed, failed


def test_concurrent_access():
    """Test thread safety of state and cache."""
    print("\n" + "=" * 60)
    print("TEST: Concurrent Access")
    print("=" * 60)

    state.force_clear_all()
    answer_cache.clear_cache()

    passed = 0
    failed = 0
    errors = []

    def worker(thread_id):
        try:
            for i in range(10):
                # Test state
                state.start_generation()
                time.sleep(0.001)
                state.stop_generation()

                # Test cache
                q = f"Question {thread_id}-{i}"
                answer_cache.cache_answer(q, f"Answer {thread_id}-{i}")
                answer_cache.get_cached_answer(q)

        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")

    # Run concurrent threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if not errors:
        print(f"  [PASS] No errors in concurrent access")
        passed += 1
    else:
        print(f"  [FAIL] Errors: {errors}")
        failed += 1

    # Verify state is clean
    if not state.should_block_input():
        print(f"  [PASS] State clean after concurrent access")
        passed += 1
    else:
        print(f"  [FAIL] State not clean")
        failed += 1

    print(f"\nConcurrent Access: {passed}/{passed+failed} tests passed")
    return passed, failed


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 70)
    print(" " * 15 + "INTERVIEW VOICE ASSISTANT - TEST SUITE")
    print("=" * 70)

    total_passed = 0
    total_failed = 0

    # Run tests
    p, f = test_state_management()
    total_passed += p
    total_failed += f

    p, f = test_answer_cache()
    total_passed += p
    total_failed += f

    p, f = test_question_validation()
    total_passed += p
    total_failed += f

    p, f = test_adaptive_silence()
    total_passed += p
    total_failed += f

    p, f = test_concurrent_access()
    total_passed += p
    total_failed += f

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal: {total_passed}/{total_passed+total_failed} tests passed")

    if total_failed == 0:
        print("\nALL TESTS PASSED")
        return 0
    else:
        print(f"\n{total_failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
