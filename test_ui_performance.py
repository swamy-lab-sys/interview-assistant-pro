#!/usr/bin/env python3
"""
UI Performance Test - Real Interview Simulation
================================================

Tests the UI's ability to deliver answers quickly during a real interview.
Measures:
1. Answer retrieval speed
2. UI update latency
3. Server response time
4. End-to-end performance (question → answer visible on UI)

Simulates a real interview where you need answers FAST!
"""

import os
import sys
import time
import json
import requests
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from threading import Thread

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Configuration
SERVER_URL = "http://localhost:8000"
ANSWERS_FILE = Path.home() / ".interview_assistant" / "current_answer.json"

# Performance thresholds (based on real interview needs)
THRESHOLD_CRITICAL = 1.0  # Must get answer within 1 second
THRESHOLD_GOOD = 0.5      # Good performance
THRESHOLD_EXCELLENT = 0.3 # Excellent performance


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_test(name):
    print(f"{CYAN}▶ TEST: {name}{RESET}")


def print_metric(name, value, threshold=None):
    if threshold:
        if value <= THRESHOLD_EXCELLENT:
            color = GREEN
            rating = "EXCELLENT"
        elif value <= THRESHOLD_GOOD:
            color = GREEN
            rating = "GOOD"
        elif value <= THRESHOLD_CRITICAL:
            color = YELLOW
            rating = "ACCEPTABLE"
        else:
            color = RED
            rating = "TOO SLOW"
        print(f"  {name}: {color}{value:.3f}s{RESET} ({rating})")
    else:
        print(f"  {name}: {value:.3f}s")


def print_pass(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_fail(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"  {msg}")


def start_server():
    """Start server in background."""
    print_info("Starting server...")
    proc = subprocess.Popen(
        ['python3', 'main.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    time.sleep(4)  # Wait for full startup
    return proc


def stop_server(proc):
    """Stop server gracefully."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        time.sleep(2)
    except:
        pass


def inject_interview_question(question, answer):
    """Inject a Q&A pair to simulate answered question."""
    ANSWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    qa = {
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().isoformat(),
        'is_complete': True,
        'metrics': {'llm_ms': 1200}
    }
    
    # Read existing
    existing = []
    if ANSWERS_FILE.exists():
        try:
            with open(ANSWERS_FILE, 'r') as f:
                data = json.load(f)
                existing = data if isinstance(data, list) else [data]
        except:
            pass
    
    # Add new
    existing.append(qa)
    
    # Write back
    with open(ANSWERS_FILE, 'w') as f:
        json.dump(existing, f, indent=2)
    
    return qa


def measure_api_response_time(endpoint):
    """Measure API response time."""
    start = time.time()
    try:
        response = requests.get(f"{SERVER_URL}{endpoint}", timeout=5)
        elapsed = time.time() - start
        return elapsed, response.status_code == 200, response
    except Exception as e:
        return time.time() - start, False, None


def measure_answer_retrieval(question):
    """Measure how fast we can retrieve an answer for a question."""
    start = time.time()
    
    try:
        response = requests.get(f"{SERVER_URL}/api/answers", timeout=5)
        if response.status_code == 200:
            answers = response.json()
            for ans in answers:
                if ans.get('question') == question:
                    elapsed = time.time() - start
                    return elapsed, True, ans.get('answer')
        
        elapsed = time.time() - start
        return elapsed, False, None
    except Exception as e:
        return time.time() - start, False, None


# ═══════════════════════════════════════════════════════════════════════
# TEST 1: API RESPONSE TIME
# ═══════════════════════════════════════════════════════════════════════

def test_api_response_time():
    """Test basic API response times."""
    print_test("API Response Time")
    
    endpoints = [
        ('/api/answers', 'Get all answers'),
        ('/api/ip', 'Get server IP'),
        ('/api/resume_status', 'Resume status'),
    ]
    
    results = []
    for endpoint, description in endpoints:
        elapsed, success, _ = measure_api_response_time(endpoint)
        print_metric(f"  {description}", elapsed, threshold=True)
        results.append((description, elapsed, success))
    
    # All should be fast
    avg_time = sum(r[1] for r in results) / len(results)
    print_metric("Average API response", avg_time, threshold=True)
    
    if avg_time <= THRESHOLD_CRITICAL:
        print_pass("API response time acceptable for real-time interview")
        return True
    else:
        print_fail("API too slow for real-time interview use")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TEST 2: ANSWER RETRIEVAL SPEED
# ═══════════════════════════════════════════════════════════════════════

def test_answer_retrieval_speed():
    """Test how fast we can retrieve answers during interview."""
    print_test("Answer Retrieval Speed (Real Interview Simulation)")
    
    # Simulate 5 questions already answered
    questions = [
        ("What is Python's GIL?", "The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects..."),
        ("Explain decorators", "Decorators are functions that modify the behavior of other functions..."),
        ("What is a generator?", "A generator is a function that yields values lazily using the yield keyword..."),
        ("Difference between list and tuple?", "Lists are mutable and use [], tuples are immutable and use ()..."),
        ("How does async/await work?", "Async/await provides syntactic sugar for asynchronous programming...")
    ]
    
    print_info(f"Injecting {len(questions)} answered questions...")
    for q, a in questions:
        inject_interview_question(q, a)
    
    time.sleep(0.5)  # Let server process
    
    # Now measure retrieval time for each
    print_info("\nMeasuring retrieval time for each question:")
    retrieval_times = []
    
    for q, _ in questions:
        elapsed, success, answer = measure_answer_retrieval(q)
        retrieval_times.append(elapsed)
        
        if success:
            print_metric(f"  '{q[:40]}...'", elapsed, threshold=True)
        else:
            print_fail(f"  Failed to retrieve: {q[:40]}")
            return False
    
    # Statistics
    avg_retrieval = sum(retrieval_times) / len(retrieval_times)
    max_retrieval = max(retrieval_times)
    min_retrieval = min(retrieval_times)
    
    print(f"\n{CYAN}Statistics:{RESET}")
    print_metric("  Average retrieval time", avg_retrieval, threshold=True)
    print_metric("  Fastest retrieval", min_retrieval)
    print_metric("  Slowest retrieval", max_retrieval)
    
    if avg_retrieval <= THRESHOLD_CRITICAL:
        print_pass(f"Answer retrieval fast enough for real-time interview")
        return True
    else:
        print_fail(f"Answer retrieval too slow (avg: {avg_retrieval:.3f}s)")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TEST 3: CONCURRENT ACCESS (MULTIPLE TABS)
# ═══════════════════════════════════════════════════════════════════════

def test_concurrent_access():
    """Test UI performance with multiple tabs open (realistic scenario)."""
    print_test("Concurrent Access (Multiple Tabs)")
    
    print_info("Simulating 3 browser tabs accessing UI simultaneously...")
    
    def fetch_answers():
        """Fetch answers (simulates a browser tab)."""
        start = time.time()
        try:
            response = requests.get(f"{SERVER_URL}/api/answers", timeout=5)
            return time.time() - start, response.status_code == 200
        except:
            return time.time() - start, False
    
    # Launch 3 concurrent requests
    threads = []
    results = []
    
    for i in range(3):
        def worker(tab_id):
            elapsed, success = fetch_answers()
            results.append((tab_id, elapsed, success))
        
        t = Thread(target=worker, args=(i+1,))
        threads.append(t)
        t.start()
    
    # Wait for all
    for t in threads:
        t.join()
    
    # Analyze results
    for tab_id, elapsed, success in results:
        status = "SUCCESS" if success else "FAILED"
        print_metric(f"  Tab {tab_id}", elapsed, threshold=True)
    
    avg_concurrent = sum(r[1] for r in results) / len(results)
    all_success = all(r[2] for r in results)
    
    print_metric("  Average (concurrent)", avg_concurrent, threshold=True)
    
    if all_success and avg_concurrent <= THRESHOLD_CRITICAL:
        print_pass("Server handles concurrent access well")
        return True
    else:
        print_fail("Server struggles with concurrent access")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TEST 4: REAL INTERVIEW SCENARIO (END-TO-END)
# ═══════════════════════════════════════════════════════════════════════

def test_real_interview_scenario():
    """
    Simulate a real interview scenario:
    1. Interviewer asks question
    2. You need to check answer on phone
    3. Measure total time from question to answer visible
    """
    print_test("Real Interview Scenario (End-to-End)")
    
    print_info("Scenario: Interviewer asks 'What is Python's GIL?'")
    print_info("You need to quickly check your phone for the answer...")
    
    # Clear existing answers
    if ANSWERS_FILE.exists():
        ANSWERS_FILE.unlink()
    
    # Step 1: Question is asked and answered (simulated)
    question = "What is Python's GIL and why does it matter?"
    answer = """The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously.

Why it matters:
- Limits true parallelism in multi-threaded Python programs
- CPU-bound tasks don't benefit from multi-threading
- I/O-bound tasks can still benefit from threading
- Workarounds: multiprocessing, async/await, or C extensions

Example impact:
```python
# This won't run in parallel due to GIL
threads = [Thread(target=cpu_intensive_task) for _ in range(4)]
```"""
    
    # Inject answer
    start_total = time.time()
    inject_interview_question(question, answer)
    inject_time = time.time() - start_total
    
    # Step 2: Retrieve answer (you checking phone)
    time.sleep(0.1)  # Small delay (realistic)
    
    start_retrieval = time.time()
    elapsed, success, retrieved_answer = measure_answer_retrieval(question)
    retrieval_time = time.time() - start_retrieval
    
    # Step 3: Total time
    total_time = time.time() - start_total
    
    print(f"\n{CYAN}Timing Breakdown:{RESET}")
    print_metric("  1. Answer stored", inject_time)
    print_metric("  2. Answer retrieved", retrieval_time, threshold=True)
    print_metric("  3. Total (question → answer visible)", total_time, threshold=True)
    
    if success and total_time <= THRESHOLD_CRITICAL:
        print_pass(f"Fast enough for real interview (total: {total_time:.3f}s)")
        print_info(f"  Answer preview: {retrieved_answer[:100]}...")
        return True
    else:
        print_fail(f"Too slow for real interview (total: {total_time:.3f}s)")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TEST 5: STRESS TEST (MANY QUESTIONS)
# ═══════════════════════════════════════════════════════════════════════

def test_stress_many_questions():
    """Test performance with many questions (long interview)."""
    print_test("Stress Test (Long Interview - 20 Questions)")
    
    # Clear existing
    if ANSWERS_FILE.exists():
        ANSWERS_FILE.unlink()
    
    # Inject 20 questions
    print_info("Injecting 20 questions...")
    questions = []
    for i in range(1, 21):
        q = f"Interview Question {i}: Explain concept {i}"
        a = f"This is a detailed answer to question {i}. " * 10  # ~500 chars each
        questions.append((q, a))
        inject_interview_question(q, a)
    
    time.sleep(0.5)
    
    # Measure retrieval time for first, middle, and last question
    test_indices = [0, 10, 19]  # First, middle, last
    
    print_info("\nMeasuring retrieval time at different positions:")
    for idx in test_indices:
        q, _ = questions[idx]
        elapsed, success, _ = measure_answer_retrieval(q)
        position = ["First", "Middle", "Last"][test_indices.index(idx)]
        print_metric(f"  {position} question (#{idx+1})", elapsed, threshold=True)
    
    # Measure full list retrieval
    start = time.time()
    response = requests.get(f"{SERVER_URL}/api/answers", timeout=10)
    full_retrieval = time.time() - start
    
    if response.status_code == 200:
        all_answers = response.json()
        print_metric(f"  Full list ({len(all_answers)} answers)", full_retrieval, threshold=True)
        
        if full_retrieval <= THRESHOLD_CRITICAL:
            print_pass(f"Handles {len(all_answers)} questions efficiently")
            return True
        else:
            print_fail(f"Slow with many questions ({full_retrieval:.3f}s)")
            return False
    else:
        print_fail("Failed to retrieve full list")
        return False


# ═══════════════════════════════════════════════════════════════════════
# TEST 6: UI REFRESH RATE (SSE STREAM)
# ═══════════════════════════════════════════════════════════════════════

def test_ui_refresh_rate():
    """Test Server-Sent Events stream performance."""
    print_test("UI Refresh Rate (SSE Stream)")
    
    print_info("Testing real-time update stream...")
    
    # Inject a new question
    inject_interview_question(
        "Test question for SSE",
        "Test answer for SSE streaming"
    )
    
    # Measure SSE connection time
    start = time.time()
    try:
        # SSE endpoint should respond quickly
        response = requests.get(
            f"{SERVER_URL}/api/stream",
            stream=True,
            timeout=2
        )
        
        if response.status_code == 200:
            # Read first event
            for line in response.iter_lines():
                if line:
                    elapsed = time.time() - start
                    print_metric("  SSE first event", elapsed, threshold=True)
                    break
            
            response.close()
            
            if elapsed <= THRESHOLD_CRITICAL:
                print_pass("SSE stream responds quickly")
                return True
            else:
                print_fail("SSE stream too slow")
                return False
        else:
            print_fail("SSE endpoint not responding")
            return False
            
    except Exception as e:
        print_fail(f"SSE test failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════

def cleanup():
    """Clean up test files."""
    if ANSWERS_FILE.exists():
        ANSWERS_FILE.unlink()


def main():
    print_header("UI PERFORMANCE TEST - REAL INTERVIEW SIMULATION")
    print(f"{CYAN}Testing UI speed and performance for real interview use{RESET}\n")
    
    # Check we're in the right directory
    if not Path('main.py').exists():
        print_fail("Must run from project root directory")
        sys.exit(1)
    
    # Start server
    print_info("Starting server for testing...")
    proc = start_server()
    
    # Wait for server to be ready
    print_info("Waiting for server to be ready...")
    max_wait = 10
    for i in range(max_wait):
        try:
            response = requests.get(f"{SERVER_URL}/api/ip", timeout=1)
            if response.status_code == 200:
                print_pass("Server ready!")
                break
        except:
            time.sleep(1)
    else:
        print_fail("Server failed to start")
        stop_server(proc)
        sys.exit(1)
    
    results = []
    
    try:
        # Run all tests
        results.append(("API Response Time", test_api_response_time()))
        cleanup()
        
        results.append(("Answer Retrieval Speed", test_answer_retrieval_speed()))
        cleanup()
        
        results.append(("Concurrent Access", test_concurrent_access()))
        cleanup()
        
        results.append(("Real Interview Scenario", test_real_interview_scenario()))
        cleanup()
        
        results.append(("Stress Test (20 Questions)", test_stress_many_questions()))
        cleanup()
        
        results.append(("UI Refresh Rate (SSE)", test_ui_refresh_rate()))
        cleanup()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        cleanup()
        stop_server(proc)
        sys.exit(1)
    except Exception as e:
        print_fail(f"Test suite error: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        stop_server(proc)
        sys.exit(1)
    finally:
        stop_server(proc)
    
    # Summary
    print_header("PERFORMANCE TEST RESULTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status} - {name}")
    
    print(f"\n{CYAN}{'─'*70}{RESET}")
    print(f"{CYAN}Results: {passed}/{total} tests passed{RESET}")
    print(f"{CYAN}{'─'*70}{RESET}\n")
    
    # Performance rating
    if passed == total:
        print(f"{GREEN}{'='*70}")
        print(f"🚀 EXCELLENT PERFORMANCE!")
        print(f"Your UI is fast enough for real-time interview use")
        print(f"")
        print(f"Performance Summary:")
        print(f"  ✓ API responses: < 1 second")
        print(f"  ✓ Answer retrieval: < 1 second")
        print(f"  ✓ Concurrent access: Handled well")
        print(f"  ✓ Real interview scenario: Fast enough")
        print(f"  ✓ Stress test: Handles many questions")
        print(f"  ✓ UI refresh: Real-time updates work")
        print(f"{'='*70}{RESET}\n")
        sys.exit(0)
    else:
        print(f"{YELLOW}{'='*70}")
        print(f"⚠️  PERFORMANCE NEEDS IMPROVEMENT")
        print(f"Some tests failed - review implementation")
        print(f"{'='*70}{RESET}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
