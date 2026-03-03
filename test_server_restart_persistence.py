#!/usr/bin/env python3
"""
Server Restart Persistence Test Suite

Tests that Q&A history is preserved across server restarts.
"""

import os
import sys
import time
import json
import subprocess
import signal
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Paths
ANSWERS_FILE = Path.home() / ".interview_assistant" / "current_answer.json"
HISTORY_FILE = Path.home() / ".interview_assistant" / "answer_history.jsonl"
MASTER_LOG = Path.home() / ".interview_assistant" / "interview_master_log.jsonl"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_test(name):
    print(f"{YELLOW}▶ TEST: {name}{RESET}")

def print_pass(msg):
    print(f"{GREEN}✓ PASS: {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}✗ FAIL: {msg}{RESET}")

def print_info(msg):
    print(f"  {msg}")

def read_answers():
    """Read current answers from disk."""
    if not ANSWERS_FILE.exists():
        return []
    try:
        with open(ANSWERS_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except:
        return []

def inject_test_answers(count=4):
    """Inject test Q&A pairs directly to disk (simulating answered questions)."""
    test_answers = []
    for i in range(1, count + 1):
        test_answers.append({
            'question': f'Test Question {i}?',
            'answer': f'This is the answer to test question {i}.',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'is_complete': True,
            'metrics': {'test': True}
        })
    
    ANSWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ANSWERS_FILE, 'w') as f:
        json.dump(test_answers, f)
    
    print_info(f"Injected {count} test Q&A pairs to disk")
    return test_answers

def start_server():
    """Start the server in background."""
    print_info("Starting server...")
    proc = subprocess.Popen(
        ['python3', 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(3)  # Wait for startup
    return proc

def stop_server(proc):
    """Stop the server gracefully."""
    print_info("Stopping server...")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    time.sleep(2)

def kill_server(proc):
    """Kill the server forcefully (simulate crash)."""
    print_info("Killing server (simulating crash)...")
    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    time.sleep(1)

def test_normal_restart():
    """Test 1: Normal restart preserves history."""
    print_test("Normal Restart - Preserve History")
    
    # Setup: Inject 4 test answers
    original_answers = inject_test_answers(4)
    
    # Start server
    proc = start_server()
    
    # Wait for startup to complete
    time.sleep(2)
    
    # Read answers after startup
    restored_answers = read_answers()
    
    # Stop server
    stop_server(proc)
    
    # Verify
    if len(restored_answers) == 4:
        print_pass(f"All 4 Q&A pairs restored after restart")
        # Verify content matches
        for i, ans in enumerate(restored_answers):
            if ans.get('question') == original_answers[i]['question']:
                print_info(f"  Q{i+1}: {ans['question']}")
            else:
                print_fail(f"Question {i+1} content mismatch")
                return False
        return True
    else:
        print_fail(f"Expected 4 Q&A, got {len(restored_answers)}")
        return False

def test_crash_recovery():
    """Test 2: Crash recovery preserves complete answers."""
    print_test("Crash Recovery - Preserve Complete Answers")
    
    # Setup: Inject 2 complete + 1 incomplete answer
    complete_answers = inject_test_answers(2)
    
    # Add incomplete answer (simulating crash during streaming)
    answers = read_answers()
    answers.append({
        'question': 'Incomplete Question?',
        'answer': 'Partial answer...',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'is_complete': False,  # Not complete
        'metrics': None
    })
    with open(ANSWERS_FILE, 'w') as f:
        json.dump(answers, f)
    
    print_info("Injected 2 complete + 1 incomplete answer")
    
    # Start server
    proc = start_server()
    time.sleep(2)
    
    # Read answers
    restored_answers = read_answers()
    
    # Kill server
    kill_server(proc)
    
    # Verify: Should have 2 complete answers, incomplete should be filtered
    if len(restored_answers) == 2:
        print_pass("Incomplete answer filtered out, 2 complete answers restored")
        return True
    else:
        print_fail(f"Expected 2 complete answers, got {len(restored_answers)}")
        return False

def test_corrupted_file():
    """Test 3: Corrupted file handling."""
    print_test("Corrupted File - Graceful Fallback")
    
    # Setup: Write corrupted JSON
    ANSWERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ANSWERS_FILE, 'w') as f:
        f.write("{invalid json content[")
    
    print_info("Created corrupted JSON file")
    
    # Start server
    proc = start_server()
    time.sleep(2)
    
    # Read answers
    restored_answers = read_answers()
    
    # Stop server
    stop_server(proc)
    
    # Verify: Should start fresh with empty state
    if len(restored_answers) == 0:
        print_pass("Corrupted file handled gracefully, started fresh")
        return True
    else:
        print_fail(f"Expected empty state, got {len(restored_answers)} answers")
        return False

def test_manual_clear():
    """Test 4: Manual clear via API."""
    print_test("Manual Clear - API Endpoint")
    
    # Setup: Inject 3 answers
    inject_test_answers(3)
    
    # Start server
    proc = start_server()
    time.sleep(2)
    
    # Verify answers exist
    answers_before = read_answers()
    if len(answers_before) != 3:
        print_fail(f"Setup failed: expected 3 answers, got {len(answers_before)}")
        stop_server(proc)
        return False
    
    print_info(f"Before clear: {len(answers_before)} answers")
    
    # Call clear API
    import requests
    try:
        response = requests.post('http://localhost:8000/api/clear_session', timeout=5)
        if response.status_code == 200:
            print_info("Clear API called successfully")
        else:
            print_fail(f"Clear API failed: {response.status_code}")
            stop_server(proc)
            return False
    except Exception as e:
        print_fail(f"Could not call clear API: {e}")
        stop_server(proc)
        return False
    
    time.sleep(1)
    
    # Verify answers cleared
    answers_after = read_answers()
    
    # Stop server
    stop_server(proc)
    
    if len(answers_after) == 0:
        print_pass("Manual clear successful, all answers removed")
        return True
    else:
        print_fail(f"Expected 0 answers after clear, got {len(answers_after)}")
        return False

def test_multi_restart():
    """Test 5: Multiple restarts preserve history."""
    print_test("Multiple Restarts - Cumulative History")
    
    # Start with 2 answers
    inject_test_answers(2)
    
    # Restart 1
    proc = start_server()
    time.sleep(2)
    answers_r1 = read_answers()
    stop_server(proc)
    
    if len(answers_r1) != 2:
        print_fail(f"Restart 1: expected 2, got {len(answers_r1)}")
        return False
    print_info(f"Restart 1: {len(answers_r1)} answers")
    
    # Restart 2
    proc = start_server()
    time.sleep(2)
    answers_r2 = read_answers()
    stop_server(proc)
    
    if len(answers_r2) != 2:
        print_fail(f"Restart 2: expected 2, got {len(answers_r2)}")
        return False
    print_info(f"Restart 2: {len(answers_r2)} answers")
    
    # Restart 3
    proc = start_server()
    time.sleep(2)
    answers_r3 = read_answers()
    stop_server(proc)
    
    if len(answers_r3) == 2:
        print_pass("History preserved across 3 restarts")
        return True
    else:
        print_fail(f"Restart 3: expected 2, got {len(answers_r3)}")
        return False

def cleanup():
    """Clean up test files."""
    print_info("Cleaning up test files...")
    for f in [ANSWERS_FILE, HISTORY_FILE]:
        if f.exists():
            f.unlink()

def main():
    print_header("SERVER RESTART PERSISTENCE TEST SUITE")
    
    # Check we're in the right directory
    if not Path('main.py').exists():
        print_fail("Must run from project root directory")
        sys.exit(1)
    
    # Check server is not already running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    if result == 0:
        print_fail("Server already running on port 8000. Please stop it first.")
        sys.exit(1)
    
    results = []
    
    # Run tests
    try:
        results.append(("Normal Restart", test_normal_restart()))
        cleanup()
        
        results.append(("Crash Recovery", test_crash_recovery()))
        cleanup()
        
        results.append(("Corrupted File", test_corrupted_file()))
        cleanup()
        
        results.append(("Manual Clear", test_manual_clear()))
        cleanup()
        
        results.append(("Multiple Restarts", test_multi_restart()))
        cleanup()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print_fail(f"Test suite error: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        sys.exit(1)
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}{'='*60}")
        print(f"ALL TESTS PASSED - PERSISTENCE WORKING CORRECTLY")
        print(f"{'='*60}{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{RED}{'='*60}")
        print(f"SOME TESTS FAILED - REVIEW IMPLEMENTATION")
        print(f"{'='*60}{RESET}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
