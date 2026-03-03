#!/usr/bin/env python3
"""
Test Suite: Google Meet & Teams Chat Capture + Keyboard Shortcuts

Tests the content.js logic (simulated), server API endpoints,
and different scenarios for CC/Chat capture on both platforms.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import signal
import re
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# =====================================================
# PART 1: JavaScript Syntax & Logic Validation
# =====================================================

def test_js_syntax():
    """Validate content.js has no syntax errors."""
    print("\n" + "=" * 60)
    print("TEST 1: JavaScript Syntax Validation")
    print("=" * 60)

    js_file = Path(__file__).parent / "chrome_extension" / "content.js"
    result = subprocess.run(
        ["node", "-c", str(js_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  PASS  content.js - no syntax errors")
        return True
    else:
        print(f"  FAIL  content.js syntax error: {result.stderr}")
        return False


def test_js_logic_patterns():
    """Validate key patterns exist in content.js after our fixes."""
    print("\n" + "=" * 60)
    print("TEST 2: JavaScript Logic Pattern Checks")
    print("=" * 60)

    js_file = Path(__file__).parent / "chrome_extension" / "content.js"
    content = js_file.read_text()

    checks = [
        # Fix 1: sendCapturedQuestion uses detectChatPlatform()
        (
            "sendCapturedQuestion uses detectChatPlatform",
            "const platform = detectChatPlatform()" in content and
            "platform: platform," in content
        ),
        # Fix 1 negative: no more hardcoded 'google-meet' in sendCapturedQuestion
        (
            "No hardcoded 'google-meet' in sendCapturedQuestion",
            "platform: 'google-meet'" not in content
        ),
        # Fix 2: isTeams() helper exists
        (
            "isTeams() helper function exists",
            "function isTeams()" in content
        ),
        # Fix 2: isSupportedMeetingPlatform() exists
        (
            "isSupportedMeetingPlatform() helper exists",
            "function isSupportedMeetingPlatform()" in content
        ),
        # Fix 2: startCCCapture uses isSupportedMeetingPlatform
        (
            "startCCCapture checks isSupportedMeetingPlatform",
            "if (!isSupportedMeetingPlatform())" in content
        ),
        # Fix 2: findCaptionContainer has Teams selectors
        (
            "findCaptionContainer has Teams caption selectors",
            "data-tid=\"closed-captions-renderer\"" in content
        ),
        # Fix 2: processAllExistingChatMessages handles Teams
        (
            "processAllExistingChatMessages handles non-Meet platforms",
            "getAllChatMessages(platform)" in content
        ),
        # Fix 2: checkPlatformChat (renamed from checkMeetChat)
        (
            "checkMeetChat renamed to checkPlatformChat",
            "function checkPlatformChat()" in content and
            "checkMeetChat" not in content
        ),
        # Fix 3: visibilitychange auto-resume
        (
            "visibilitychange has auto-resume logic",
            "ccWasPausedByVisibility" in content and
            "startCCCapture()" in content
        ),
        # Fix 4: Consolidated keyboard handler with Shift guard
        (
            "Keyboard handler guards against Shift key",
            "e.shiftKey || e.metaKey" in content or
            "!e.shiftKey" in content
        ),
        # Fix 4: Single handler with CC toggle
        (
            "CC toggle (Ctrl+Alt+C) in consolidated handler",
            "case 'c': // TOGGLE CC/CHAT CAPTURE" in content
        ),
        # Fix 4: No duplicate keydown for CC
        (
            "No separate CC keydown handler",
            content.count("document.addEventListener('keydown'") <= 2  # main handler + typing pause
        ),
        # Fix 5: Teams selectors updated in getChatMessage
        (
            "Teams getChatMessage has new Fluent UI selectors",
            "fui-ChatMessage__body" in content
        ),
        # Fix 5: Teams selectors in getAllChatMessages
        (
            "Teams getAllChatMessages has meeting chat selectors",
            "data-tid=\"meeting-chat-message\"" in content
        ),
        # Fix 9: triggerStart handles Teams
        (
            "triggerStart routes Teams to chat mode",
            "platform === 'teams'" in content
        ),
        # Proctoring check covers both platforms
        (
            "Proctoring check runs on supported platforms",
            "isSupportedMeetingPlatform()" in content
        ),
    ]

    passed = 0
    failed = 0
    for desc, result in checks:
        if result:
            print(f"  PASS  {desc}")
            passed += 1
        else:
            print(f"  FAIL  {desc}")
            failed += 1

    print(f"\n  Results: {passed}/{passed + failed} passed")
    return failed == 0


def test_typewriter_syntax():
    """Validate typewriter.js has no syntax errors."""
    print("\n" + "=" * 60)
    print("TEST 3: Typewriter.js Syntax Validation")
    print("=" * 60)

    js_file = Path(__file__).parent / "chrome_extension" / "typewriter.js"
    result = subprocess.run(
        ["node", "-c", str(js_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  PASS  typewriter.js - no syntax errors")
        return True
    else:
        print(f"  FAIL  typewriter.js syntax error: {result.stderr}")
        return False


def test_page_bridge_syntax():
    """Validate page_bridge.js has no syntax errors."""
    print("\n" + "=" * 60)
    print("TEST 4: Page Bridge Syntax Validation")
    print("=" * 60)

    js_file = Path(__file__).parent / "chrome_extension" / "page_bridge.js"
    result = subprocess.run(
        ["node", "-c", str(js_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  PASS  page_bridge.js - no syntax errors")
        return True
    else:
        print(f"  FAIL  page_bridge.js syntax error: {result.stderr}")
        return False


def test_background_syntax():
    """Validate background.js has no syntax errors."""
    print("\n" + "=" * 60)
    print("TEST 5: Background.js Syntax Validation")
    print("=" * 60)

    js_file = Path(__file__).parent / "chrome_extension" / "background.js"
    result = subprocess.run(
        ["node", "-c", str(js_file)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  PASS  background.js - no syntax errors")
        return True
    else:
        print(f"  FAIL  background.js syntax error: {result.stderr}")
        return False


# =====================================================
# PART 2: Python Server-Side Validation
# =====================================================

def test_question_validator():
    """Test question validator with Meet/Teams chat-style questions."""
    print("\n" + "=" * 60)
    print("TEST 6: Question Validator (Chat-style Questions)")
    print("=" * 60)

    from question_validator import validate_question, is_code_request

    chat_scenarios = [
        # (text, should_be_valid, description)
        ("What is a decorator in Python?", True, "Standard tech question"),
        ("Explain the difference between list and tuple", True, "Comparison question"),
        ("How does Django ORM handle migrations?", True, "Framework question"),
        ("Tell me about yourself", True, "HR behavioral question"),
        ("What is your experience with Kubernetes?", True, "DevOps question"),
        ("Write a function to reverse a linked list", True, "Coding question"),
        ("Can you explain CI/CD pipeline?", True, "DevOps pipeline"),
        ("What is Docker and how is it different from VM?", True, "Container question"),
        # These should be rejected
        ("okay", False, "Filler word"),
        ("can you hear me", False, "Audio check"),
        ("hi hello", False, "Greeting"),
        ("joined the meeting", False, "System notification"),
        ("In this video we will learn Python", False, "YouTube content"),
        ("Subscribe to my channel", False, "YouTube spam"),
        ("um", False, "Single filler"),
    ]

    passed = 0
    for text, expected, desc in chat_scenarios:
        is_valid, cleaned, reason = validate_question(text)
        status = "PASS" if is_valid == expected else "FAIL"
        if is_valid == expected:
            passed += 1
        extra = f" -> '{cleaned}'" if is_valid else f" (reason: {reason})"
        print(f"  {status}  [{desc}] '{text[:50]}'{extra}")

    # Test code detection
    code_scenarios = [
        ("Write a function to check palindrome", True, "Explicit code request"),
        ("Write code for fibonacci series", True, "Code keyword"),
        ("Explain decorators in Python", False, "Explanation, not code"),
        ("What is the difference between list and tuple", False, "Theory question"),
        ("Define a class for Employee", True, "Define class request"),
    ]

    print("\n  --- Code Request Detection ---")
    for text, expected, desc in code_scenarios:
        result = is_code_request(text)
        status = "PASS" if result == expected else "FAIL"
        if result == expected:
            passed += 1
        print(f"  {status}  [{desc}] '{text[:50]}' -> code={result}")

    total = len(chat_scenarios) + len(code_scenarios)
    print(f"\n  Results: {passed}/{total} passed")
    return passed == total


def test_server_cc_question_endpoint():
    """Test the /api/cc_question endpoint with different scenarios."""
    print("\n" + "=" * 60)
    print("TEST 7: Server /api/cc_question Endpoint")
    print("=" * 60)

    import requests

    base_url = "http://localhost:8000"

    # Check if server is running
    try:
        r = requests.get(f"{base_url}/api/answers", timeout=2)
        if r.status_code != 200:
            print("  SKIP  Server not responding properly")
            return None
    except requests.ConnectionError:
        print("  SKIP  Server not running (start with: python web/server.py)")
        return None

    scenarios = [
        # Scenario 1: Google Meet chat question
        {
            "name": "Google Meet chat - tech question",
            "payload": {
                "question": "What is the difference between abstract class and interface in Python?",
                "source": "chat",
                "platform": "google-meet",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["answered", "already_answered"]
        },
        # Scenario 2: Teams chat question
        {
            "name": "Teams chat - DevOps question",
            "payload": {
                "question": "How do you set up a Kubernetes deployment with rolling updates?",
                "source": "chat",
                "platform": "teams",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["answered", "already_answered"]
        },
        # Scenario 3: CC caption question
        {
            "name": "CC caption - interview question",
            "payload": {
                "question": "Can you explain how garbage collection works in Python?",
                "source": "cc",
                "platform": "google-meet",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["answered", "already_answered"]
        },
        # Scenario 4: Empty question (should fail)
        {
            "name": "Empty question (should reject)",
            "payload": {
                "question": "",
                "source": "chat",
                "platform": "teams",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["error"]
        },
        # Scenario 5: Noise/filler (should reject)
        {
            "name": "Filler text (should reject)",
            "payload": {
                "question": "okay yeah sure",
                "source": "chat",
                "platform": "google-meet",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["rejected"]
        },
        # Scenario 6: Duplicate question
        {
            "name": "Duplicate question (should skip)",
            "payload": {
                "question": "Can you explain how garbage collection works in Python?",
                "source": "cc",
                "platform": "google-meet",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["duplicate", "already_answered"]
        },
        # Scenario 7: Teams CC caption
        {
            "name": "Teams CC caption - coding question",
            "payload": {
                "question": "Write a Python function to find the longest common subsequence",
                "source": "cc",
                "platform": "teams",
                "timestamp": int(time.time() * 1000)
            },
            "expect_status": ["answered", "already_answered"]
        },
    ]

    passed = 0
    for scenario in scenarios:
        try:
            r = requests.post(
                f"{base_url}/api/cc_question",
                json=scenario["payload"],
                timeout=30
            )
            data = r.json()
            status = data.get("status", data.get("error", "unknown"))

            # Check if status matches any expected
            if any(exp in str(status).lower() or exp in str(r.status_code)
                   for exp in scenario["expect_status"]):
                print(f"  PASS  {scenario['name']}: status={status}")
                passed += 1
            elif r.status_code == 400 and "error" in scenario["expect_status"]:
                print(f"  PASS  {scenario['name']}: HTTP 400 (expected error)")
                passed += 1
            else:
                print(f"  FAIL  {scenario['name']}: status={status}, HTTP={r.status_code}")
                print(f"         Response: {json.dumps(data)[:100]}")
        except Exception as e:
            print(f"  FAIL  {scenario['name']}: {e}")

    print(f"\n  Results: {passed}/{len(scenarios)} passed")
    return passed == len(scenarios)


def test_server_control_endpoints():
    """Test the control endpoints (start, pause, stop, toggle_mode)."""
    print("\n" + "=" * 60)
    print("TEST 8: Server Control Endpoints")
    print("=" * 60)

    import requests

    base_url = "http://localhost:8000"

    try:
        r = requests.get(f"{base_url}/api/answers", timeout=2)
        if r.status_code != 200:
            print("  SKIP  Server not responding")
            return None
    except requests.ConnectionError:
        print("  SKIP  Server not running")
        return None

    endpoints = [
        ("POST", "/api/control/start", {}, "running"),
        ("POST", "/api/control/pause", {}, "paused"),
        ("POST", "/api/control/stop", {}, "stopped"),
        ("POST", "/api/control/toggle_mode", {}, None),  # Toggles, check 'mode' key
        ("POST", "/api/cc_control", {"action": "start"}, None),
        ("POST", "/api/cc_control", {"action": "stop"}, None),
        ("GET", "/api/cc_status", {}, None),
    ]

    passed = 0
    for method, path, payload, expect_status in endpoints:
        try:
            if method == "POST":
                r = requests.post(f"{base_url}{path}", json=payload, timeout=5)
            else:
                r = requests.get(f"{base_url}{path}", timeout=5)

            if r.status_code == 200:
                data = r.json()
                if expect_status:
                    actual = data.get("status", "")
                    if actual == expect_status:
                        print(f"  PASS  {method} {path} -> status={actual}")
                        passed += 1
                    else:
                        print(f"  FAIL  {method} {path} -> expected={expect_status}, got={actual}")
                else:
                    print(f"  PASS  {method} {path} -> {json.dumps(data)[:80]}")
                    passed += 1
            else:
                print(f"  FAIL  {method} {path} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"  FAIL  {method} {path} -> {e}")

    print(f"\n  Results: {passed}/{len(endpoints)} passed")
    return passed == len(endpoints)


def test_server_answer_by_index():
    """Test /api/get_answer_by_index for both Google Meet and Teams answers."""
    print("\n" + "=" * 60)
    print("TEST 9: Server /api/get_answer_by_index")
    print("=" * 60)

    import requests

    base_url = "http://localhost:8000"

    try:
        r = requests.get(f"{base_url}/api/answers", timeout=2)
        if r.status_code != 200:
            print("  SKIP  Server not responding")
            return None
    except requests.ConnectionError:
        print("  SKIP  Server not running")
        return None

    test_cases = [
        # Get latest answer
        ("index=0", "Latest answer (index 0)"),
        # Get first answer
        ("index=1", "First answer (index 1)"),
        # Out of bounds
        ("index=99999", "Out of bounds (should 404)"),
        # Invalid format
        ("index=abc", "Invalid format (should 400)"),
    ]

    passed = 0
    for params, desc in test_cases:
        try:
            r = requests.get(f"{base_url}/api/get_answer_by_index?{params}", timeout=5)
            data = r.json()

            if "99999" in params:
                if r.status_code == 404:
                    print(f"  PASS  {desc}: 404 as expected")
                    passed += 1
                else:
                    print(f"  FAIL  {desc}: expected 404, got {r.status_code}")
            elif "abc" in params:
                if r.status_code == 400:
                    print(f"  PASS  {desc}: 400 as expected")
                    passed += 1
                else:
                    print(f"  FAIL  {desc}: expected 400, got {r.status_code}")
            elif r.status_code == 200:
                found = data.get("found", False)
                if found:
                    q = data.get("question", "")[:40]
                    print(f"  PASS  {desc}: found=True, question='{q}...'")
                else:
                    print(f"  PASS  {desc}: found=False (no answers yet)")
                passed += 1
            elif r.status_code == 404:
                print(f"  PASS  {desc}: 404 (no answers stored yet)")
                passed += 1
            else:
                print(f"  FAIL  {desc}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  FAIL  {desc}: {e}")

    print(f"\n  Results: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


# =====================================================
# PART 3: Platform Detection Simulation
# =====================================================

def test_platform_detection_logic():
    """Test the platform detection logic (simulated from JS)."""
    print("\n" + "=" * 60)
    print("TEST 10: Platform Detection Logic (Simulated)")
    print("=" * 60)

    def detect_chat_platform(url):
        if 'meet.google.com' in url:
            return 'google-meet'
        if 'zoom.us' in url:
            return 'zoom'
        if 'teams.microsoft.com' in url or 'teams.live.com' in url:
            return 'teams'
        return None

    def is_supported_meeting_platform(url):
        p = detect_chat_platform(url)
        return p in ('google-meet', 'teams')

    test_urls = [
        ("https://meet.google.com/abc-defg-hij", "google-meet", True),
        ("https://teams.microsoft.com/l/meetup-join/...", "teams", True),
        ("https://teams.live.com/meet/123", "teams", True),
        ("https://zoom.us/j/123456", "zoom", False),
        ("https://www.hackerrank.com/challenges/...", None, False),
        ("https://leetcode.com/problems/two-sum/", None, False),
        ("https://www.codewars.com/kata/...", None, False),
    ]

    passed = 0
    for url, expected_platform, expected_supported in test_urls:
        platform = detect_chat_platform(url)
        supported = is_supported_meeting_platform(url)

        platform_ok = platform == expected_platform
        supported_ok = supported == expected_supported

        if platform_ok and supported_ok:
            print(f"  PASS  {url[:50]} -> platform={platform}, supported={supported}")
            passed += 1
        else:
            print(f"  FAIL  {url[:50]} -> platform={platform} (exp={expected_platform}), supported={supported} (exp={expected_supported})")

    print(f"\n  Results: {passed}/{len(test_urls)} passed")
    return passed == len(test_urls)


# =====================================================
# PART 4: Keyboard Shortcut Scenario Simulation
# =====================================================

def test_keyboard_shortcut_logic():
    """Test keyboard shortcut guard logic (simulated from JS)."""
    print("\n" + "=" * 60)
    print("TEST 11: Keyboard Shortcut Guard Logic (Simulated)")
    print("=" * 60)

    def should_handle_shortcut(ctrl, alt, shift, meta, key):
        """Mirrors the JS guard: must have Ctrl+Alt, must NOT have Shift or Meta."""
        if not ctrl or not alt or shift or meta:
            return None
        valid_keys = {'a': 'START', 'p': 'PAUSE', 's': 'STOP', 'm': 'TOGGLE_MODE', 'c': 'CC_TOGGLE'}
        return valid_keys.get(key.lower())

    test_combos = [
        # (ctrl, alt, shift, meta, key, expected_action)
        (True, True, False, False, 'a', 'START'),
        (True, True, False, False, 'p', 'PAUSE'),
        (True, True, False, False, 's', 'STOP'),
        (True, True, False, False, 'm', 'TOGGLE_MODE'),
        (True, True, False, False, 'c', 'CC_TOGGLE'),
        # Shift key pressed - should NOT trigger
        (True, True, True, False, 'a', None),
        (True, True, True, False, 's', None),
        (True, True, True, False, 'c', None),
        # Meta key pressed - should NOT trigger
        (True, True, False, True, 'a', None),
        # Missing Ctrl - should NOT trigger
        (False, True, False, False, 'a', None),
        # Missing Alt - should NOT trigger
        (True, False, False, False, 'a', None),
        # Invalid key - should NOT trigger
        (True, True, False, False, 'x', None),
        (True, True, False, False, 'z', None),
    ]

    passed = 0
    for ctrl, alt, shift, meta, key, expected in test_combos:
        result = should_handle_shortcut(ctrl, alt, shift, meta, key)
        mods = []
        if ctrl: mods.append("Ctrl")
        if alt: mods.append("Alt")
        if shift: mods.append("Shift")
        if meta: mods.append("Meta")
        combo_str = "+".join(mods) + f"+{key.upper()}"

        if result == expected:
            print(f"  PASS  {combo_str:30s} -> {result or 'BLOCKED'}")
            passed += 1
        else:
            print(f"  FAIL  {combo_str:30s} -> {result} (expected={expected})")

    print(f"\n  Results: {passed}/{len(test_combos)} passed")
    return passed == len(test_combos)


# =====================================================
# PART 5: Deduplication & Hash Logic
# =====================================================

def test_deduplication_logic():
    """Test the hash-based deduplication used for chat messages."""
    print("\n" + "=" * 60)
    print("TEST 12: Message Deduplication Logic")
    print("=" * 60)

    def hash_string(s):
        """Python port of the JS hashString function."""
        h = 0
        for ch in s:
            h = ((h << 5) - h) + ord(ch)
            h = h & 0xFFFFFFFF  # Convert to 32-bit
            if h >= 0x80000000:
                h -= 0x100000000
        return str(h)

    processed = set()

    messages = [
        "What is the difference between list and tuple in Python?",
        "How does Django handle migrations?",
        "What is the difference between list and tuple in Python?",  # Duplicate!
        "Explain decorators in Python",
        "How does Django handle migrations?",  # Duplicate!
        "What is REST API?",
    ]

    expected_processed = 4  # 4 unique messages
    actual_processed = 0

    for msg in messages:
        h = hash_string(msg)
        if h in processed:
            continue
        processed.add(h)
        actual_processed += 1

    if actual_processed == expected_processed:
        print(f"  PASS  Dedup: {len(messages)} messages -> {actual_processed} unique (expected {expected_processed})")
    else:
        print(f"  FAIL  Dedup: {len(messages)} messages -> {actual_processed} unique (expected {expected_processed})")

    # Test that different messages produce different hashes
    h1 = hash_string("What is Python?")
    h2 = hash_string("What is Django?")
    h3 = hash_string("What is Python?")

    hash_check = h1 != h2 and h1 == h3
    if hash_check:
        print(f"  PASS  Hash uniqueness: different messages = different hashes, same = same")
    else:
        print(f"  FAIL  Hash uniqueness: h1={h1}, h2={h2}, h3={h3}")

    result = actual_processed == expected_processed and hash_check
    print(f"\n  Results: {'2/2' if result else 'FAIL'} passed")
    return result


# =====================================================
# PART 6: Filler & System Message Detection
# =====================================================

def test_filler_and_system_detection():
    """Test filler/noise detection and system message filtering."""
    print("\n" + "=" * 60)
    print("TEST 13: Filler & System Message Detection")
    print("=" * 60)

    def is_filler_or_noise(text):
        lower = text.lower().strip()
        fillers = [
            'okay', 'ok', 'alright', 'right', 'yeah', 'yes', 'no', 'um', 'uh',
            'hmm', 'ah', 'oh', 'so', 'well', 'let me', 'one second', 'one moment',
            'can you hear me', 'hello', 'hi', 'hey',
        ]
        return any(lower == f or lower == f + '.' for f in fillers)

    def is_system_message(text):
        lower = text.lower()
        system_patterns = [
            'joined', 'left', 'muted', 'unmuted', 'is presenting',
            'started recording', 'stopped recording', 'ended the call',
            'recording started', 'recording stopped', 'recording in progress',
            'admitted', 'removed from', 'is now', 'has ended',
        ]
        return any(p in lower for p in system_patterns)

    filler_tests = [
        ("okay", True), ("OK", True), ("um", True), ("hello", True),
        ("What is Python?", False), ("Explain Django ORM", False),
        ("alright.", True), ("yeah", True),
    ]

    system_tests = [
        ("John joined the meeting", True),
        ("Sarah left the call", True),
        ("Recording started", True),
        ("Alice is presenting", True),
        ("What is the difference between abstract class and interface?", False),
        ("How do you handle merge conflicts?", False),
    ]

    passed = 0
    total = len(filler_tests) + len(system_tests)

    print("  --- Filler Detection ---")
    for text, expected in filler_tests:
        result = is_filler_or_noise(text)
        if result == expected:
            print(f"  PASS  '{text}' -> filler={result}")
            passed += 1
        else:
            print(f"  FAIL  '{text}' -> filler={result} (expected={expected})")

    print("\n  --- System Message Detection ---")
    for text, expected in system_tests:
        result = is_system_message(text)
        if result == expected:
            print(f"  PASS  '{text[:50]}' -> system={result}")
            passed += 1
        else:
            print(f"  FAIL  '{text[:50]}' -> system={result} (expected={expected})")

    print(f"\n  Results: {passed}/{total} passed")
    return passed == total


# =====================================================
# PART 7: Visibility Change Simulation
# =====================================================

def test_visibility_change_logic():
    """Test that visibility change pauses and resumes CC capture correctly."""
    print("\n" + "=" * 60)
    print("TEST 14: Visibility Change Pause/Resume Logic")
    print("=" * 60)

    # Simulate the state machine
    cc_capture_enabled = False
    cc_was_paused_by_visibility = False

    def start_cc():
        nonlocal cc_capture_enabled
        cc_capture_enabled = True

    def stop_cc():
        nonlocal cc_capture_enabled
        cc_capture_enabled = False

    def on_visibility_change(hidden):
        nonlocal cc_was_paused_by_visibility
        if hidden and cc_capture_enabled:
            cc_was_paused_by_visibility = True
            stop_cc()
        elif not hidden and cc_was_paused_by_visibility:
            cc_was_paused_by_visibility = False
            start_cc()

    # Scenario: Enable CC -> hide tab -> show tab -> should auto-resume
    start_cc()
    assert cc_capture_enabled == True, "CC should be enabled"

    on_visibility_change(hidden=True)
    assert cc_capture_enabled == False, "CC should be paused when hidden"
    assert cc_was_paused_by_visibility == True, "Flag should be set"

    on_visibility_change(hidden=False)
    assert cc_capture_enabled == True, "CC should auto-resume when visible"
    assert cc_was_paused_by_visibility == False, "Flag should be cleared"

    print("  PASS  Enable CC -> Hide -> Show = auto-resumes")

    # Scenario: CC manually stopped -> hide tab -> show tab -> should NOT resume
    stop_cc()
    cc_was_paused_by_visibility = False

    on_visibility_change(hidden=True)
    assert cc_capture_enabled == False, "Should stay off"
    assert cc_was_paused_by_visibility == False, "Flag should NOT be set"

    on_visibility_change(hidden=False)
    assert cc_capture_enabled == False, "Should NOT auto-resume"

    print("  PASS  CC manually off -> Hide -> Show = stays off")

    print(f"\n  Results: 2/2 passed")
    return True


# =====================================================
# MAIN
# =====================================================

def main():
    print("\n" + "#" * 60)
    print("#  GOOGLE MEET & TEAMS CHAT CAPTURE TEST SUITE")
    print("#  Testing: CC Capture, Chat, Keyboard, Server API")
    print("#" * 60)

    results = {}

    # Part 1: JS Validation
    results["JS Syntax (content.js)"] = test_js_syntax()
    results["JS Logic Patterns"] = test_js_logic_patterns()
    results["JS Syntax (typewriter.js)"] = test_typewriter_syntax()
    results["JS Syntax (page_bridge.js)"] = test_page_bridge_syntax()
    results["JS Syntax (background.js)"] = test_background_syntax()

    # Part 2: Python Server Tests
    results["Question Validator"] = test_question_validator()

    # Part 3: Simulated Logic
    results["Platform Detection"] = test_platform_detection_logic()
    results["Keyboard Shortcuts"] = test_keyboard_shortcut_logic()
    results["Deduplication"] = test_deduplication_logic()
    results["Filler/System Detection"] = test_filler_and_system_detection()
    results["Visibility Change"] = test_visibility_change_logic()

    # Part 4: Server API Tests (require running server)
    results["Server CC Question"] = test_server_cc_question_endpoint()
    results["Server Control"] = test_server_control_endpoints()
    results["Server Answer By Index"] = test_server_answer_by_index()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    total_pass = 0
    total_fail = 0
    total_skip = 0

    for name, result in results.items():
        if result is None:
            status = "SKIP"
            total_skip += 1
        elif result:
            status = "PASS"
            total_pass += 1
        else:
            status = "FAIL"
            total_fail += 1
        print(f"  {status:4s}  {name}")

    print(f"\n  Total: {total_pass} PASSED, {total_fail} FAILED, {total_skip} SKIPPED")
    print("=" * 60)

    return total_fail == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
