#!/usr/bin/env python3
"""Test interview answers directly via llm_client."""
import sys
import os

# Load env from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import get_interview_answer, get_coding_answer, clear_session
from question_validator import is_code_request

# Load resume and JD
resume_text = ""
jd_text = ""
try:
    uploaded = os.path.expanduser("~/.interview_assistant/uploaded_resume.txt")
    if os.path.exists(uploaded):
        with open(uploaded) as f:
            resume_text = f.read()
except: pass
try:
    with open("job_description.txt") as f:
        jd_text = f.read()
except: pass

QUESTIONS = {
    "Python Theory": [
        "What is the difference between list and tuple in Python?",
        "What is encapsulation in Python?",
        "Explain decorators in Python?",
        "What is the difference between deep copy and shallow copy?",
        "What are generators in Python and why do we use them?",
        "What is the GIL in Python?",
    ],
    "Django Theory": [
        "What is Django ORM?",
        "Explain Django signals?",
        "What is middleware in Django?",
        "Difference between Django and Flask?",
        "What is Django REST framework?",
    ],
    "DevOps/Kubernetes": [
        "Explain Kubernetes architecture?",
        "What is a pod lifecycle in Kubernetes?",
        "What is the difference between Docker and Kubernetes?",
    ],
    "Coding": [
        "Write a function to find the factorial of a number",
        "Write a Python function to check if a string is a palindrome",
        "Write code to find the second largest number in a list",
    ],
}

def main():
    print("=" * 70)
    print("INTERVIEW ANSWER QUALITY TEST")
    print("=" * 70)

    issues = []
    total = 0
    good = 0

    for category, questions in QUESTIONS.items():
        print(f"\n{'=' * 70}")
        print(f"  {category}")
        print(f"{'=' * 70}")

        for q in questions:
            total += 1
            clear_session()
            print(f"\nQ: {q}")
            print("-" * 50)

            code_req = is_code_request(q)

            if code_req:
                answer = get_coding_answer(q)
                mode = "CODE"
            else:
                answer = get_interview_answer(q, resume_text, jd_text)
                mode = "INTERVIEW"

            print(f"[{mode}]\n{answer}\n")

            # Quality checks
            if not answer:
                issues.append(f"EMPTY: {q}")
            elif not code_req:
                has_issue = False
                if ". d" in answer and "etcd" not in answer.lower():
                    issues.append(f"etcd BUG: {q}")
                    has_issue = True
                if "let's explain" in answer.lower() or "concise explanation" in answer.lower():
                    issues.append(f"PREAMBLE: {q}")
                    has_issue = True
                if "I don't have" in answer or "There is no concept" in answer:
                    issues.append(f"REFUSES: {q}")
                    has_issue = True
                if len(answer) > 800:
                    issues.append(f"TOO LONG ({len(answer)} chars): {q}")
                    has_issue = True
                # Count bullets
                bullet_count = answer.count("\n-") + (1 if answer.startswith("-") else 0)
                if bullet_count < 2:
                    issues.append(f"FEW BULLETS ({bullet_count}): {q}")
                    has_issue = True
                if bullet_count > 6:
                    issues.append(f"TOO MANY BULLETS ({bullet_count}): {q}")
                    has_issue = True
                if not has_issue:
                    good += 1
            else:
                good += 1

    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {good}/{total} good answers")
    print(f"{'=' * 70}")
    if issues:
        print("  Issues:")
        for issue in issues:
            print(f"  ! {issue}")

if __name__ == "__main__":
    main()
