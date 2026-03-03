#!/usr/bin/env python3
"""Test all chat/CC scenarios - Google Meet, Teams, edge cases."""
import sys, os, json

# Load env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_validator import validate_question, is_code_request, clean_and_validate

# ============================================================
# TEST SCENARIOS
# ============================================================

# (message, should_accept, description)
SCENARIOS = {
    "Meeting Notifications (should REJECT)": [
        ("Venkata chalapathi Endluru joined the conversation", False, "Join notification"),
        ("John left the meeting", False, "Leave notification"),
        ("Meeting started", False, "Meeting start"),
        ("7:48 AM Meeting started", False, "Timestamped meeting start"),
        ("Recording started", False, "Recording notification"),
        ("You created this meeting14Febtesting for assistant8:00 AM - 8:30 AM, Sat", False, "Meeting creation info"),
        ("Venkata chalapathi Endluru named the meeting testing for assistant", False, "Meeting rename"),
        ("10:23 AM", False, "Timestamp only"),
        ("Meeting ended at 9:30 AM", False, "Meeting end time"),
        ("John is presenting now", False, "Presenting notification"),
        ("Someone muted their microphone", False, "Mute notification"),
    ],

    "Greetings & Filler (should REJECT)": [
        ("Hi", False, "Simple greeting"),
        ("Hello everyone", False, "Group greeting"),
        ("Good morning", False, "Morning greeting"),
        ("Thanks", False, "Thanks"),
        ("Okay", False, "Okay"),
        ("Yes", False, "Yes"),
        ("Sure", False, "Sure"),
        ("Alright", False, "Alright"),
        ("Can you hear me?", False, "Audio check"),
        ("Is my screen visible?", False, "Screen check"),
        ("Let me share my screen", False, "Screen share"),
        ("One moment please", False, "Wait request"),
    ],

    "Python Theory (should ACCEPT)": [
        ("What is the difference between list and tuple in Python?", True, "List vs tuple"),
        ("Explain decorators in Python", True, "Decorators"),
        ("What is encapsulation in Python?", True, "Encapsulation"),
        ("How does garbage collection work in Python?", True, "GC"),
        ("What is the GIL in Python?", True, "GIL"),
        ("What are generators and why do we use them?", True, "Generators"),
        ("Difference between deep copy and shallow copy?", True, "Deep vs shallow copy"),
        ("What is a context manager in Python?", True, "Context manager"),
        ("Explain *args and **kwargs", True, "Args kwargs"),
        ("What is the difference between class method and static method?", True, "Class vs static method"),
    ],

    "Django Theory (should ACCEPT)": [
        ("What is Django ORM?", True, "Django ORM"),
        ("Explain Django middleware", True, "Middleware"),
        ("What are Django signals?", True, "Signals"),
        ("Difference between Django and Flask?", True, "Django vs Flask"),
        ("What is Django REST framework?", True, "DRF"),
        ("How does Django handle migrations?", True, "Migrations"),
        ("What is CSRF protection in Django?", True, "CSRF"),
    ],

    "DevOps/Cloud (should ACCEPT)": [
        ("Explain Kubernetes architecture", True, "K8s architecture"),
        ("What is a ConfigMap in Kubernetes?", True, "ConfigMap"),
        ("Difference between Docker and Kubernetes?", True, "Docker vs K8s"),
        ("What is a pod lifecycle in Kubernetes?", True, "Pod lifecycle"),
        ("What is CI/CD pipeline?", True, "CI/CD"),
        ("How does Terraform work?", True, "Terraform"),
        ("What is infrastructure as code?", True, "IaC"),
    ],

    "Code Requests (should ACCEPT + detect as code)": [
        ("Write a function to find anagrams in a list", True, "Anagram code"),
        ("Write a Python function to check palindrome", True, "Palindrome code"),
        ("Write code to find factorial of a number", True, "Factorial code"),
        ("Define a class with getString and printString methods", True, "Class definition"),
        ("Write a program to sort words alphabetically", True, "Sort words code"),
        ("Use a list comprehension to square odd numbers", True, "List comprehension"),
        ("Write a function to find even numbers in a list", True, "Even numbers code"),
        ("Write an Ansible playbook to create EC2 instance", True, "Ansible code"),
    ],

    "HR/Behavioral (should ACCEPT)": [
        ("Tell me about yourself", True, "Self intro"),
        ("Why are you looking for a change?", True, "Job change"),
        ("What are your strengths and weaknesses?", True, "Strengths"),
        ("Where do you see yourself in 5 years?", True, "5 year plan"),
        ("Why do you want to join our company?", True, "Why join"),
        ("What is your notice period?", True, "Notice period"),
        ("What is your expected CTC?", True, "CTC"),
        ("Describe your current responsibilities", True, "Responsibilities"),
    ],

    "Teams-specific formats (should handle)": [
        ("John Doe: What is Python?", True, "Prefixed with name"),
        ("[10:23 AM] What is Django ORM?", True, "Timestamped question"),
        ("Interviewer: Explain Kubernetes architecture", True, "Interviewer prefix"),
        ("HR: Tell me about yourself", True, "HR prefix"),
        ("What is REST API? Please explain", True, "Question with please"),
        ("Can you explain microservices architecture?", True, "Polite question"),
    ],

    "Edge Cases (should REJECT)": [
        ("the", False, "Single article"),
        ("a", False, "Single letter"),
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        ("ok ok ok", False, "Repeated filler"),
        ("hahaha", False, "Laughter"),
        ("Subscribe to my channel", False, "YouTube spam"),
        ("In this video we will learn", False, "Tutorial intro"),
        ("Let's get started with today's lesson", False, "Lesson intro"),
        ("Click the link below", False, "Click bait"),
        ("What is, What is, What is", False, "Repeated hallucination"),
    ],

    "Tricky Edge Cases (boundary)": [
        ("What is?", False, "Too vague - no subject"),
        ("What is Python and", False, "Incomplete question"),
        ("How do you implement it?", False, "Vague pronoun only"),
        ("Can you explain that?", False, "Vague - no tech term"),
        ("What about the other one?", False, "Vague reference"),
        ("What is the purpose of virtual environments in Python?", True, "Valid long question"),
        ("How to deploy Django application on AWS?", True, "Multi-tech question"),
    ],
}

def main():
    print("=" * 70)
    print("CHAT/CC SCENARIO TEST")
    print("=" * 70)

    total = 0
    passed = 0
    failures = []

    for category, tests in SCENARIOS.items():
        print(f"\n{'=' * 70}")
        print(f"  {category}")
        print(f"{'=' * 70}")

        for text, expected_accept, desc in tests:
            total += 1

            # Test validate_question
            is_valid, cleaned, reason = validate_question(text)

            # For code requests, also check detection
            code_check = ""
            if is_valid and expected_accept:
                is_code = is_code_request(cleaned)
                if "write" in text.lower() or "define" in text.lower() or "use a list" in text.lower():
                    if is_code:
                        code_check = " [CODE ✓]"
                    else:
                        code_check = " [CODE MISS!]"
                        failures.append(f"{desc}: Not detected as code - '{text[:50]}'")

            # Check result
            if is_valid == expected_accept:
                status = "✓"
                passed += 1
            else:
                status = "✗"
                if expected_accept:
                    failures.append(f"{desc}: WRONGLY REJECTED ({reason}) - '{text[:50]}'")
                else:
                    failures.append(f"{desc}: WRONGLY ACCEPTED - '{text[:50]}'")

            # Print result
            reject_info = f" ({reason})" if not is_valid and reason else ""
            clean_info = f" → '{cleaned[:40]}'" if cleaned and cleaned != text else ""
            print(f"  {status} {desc:30s} | {'ACCEPT' if is_valid else 'REJECT':6s}{reject_info}{clean_info}{code_check}")

    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {passed}/{total} correct ({total-passed} failures)")
    print(f"{'=' * 70}")

    if failures:
        print(f"\n  FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  ! {f}")
    else:
        print("\n  ALL SCENARIOS PASS!")

if __name__ == "__main__":
    main()
