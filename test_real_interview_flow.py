#!/usr/bin/env python3
"""
Real Interview Flow Test
========================

Simulates a realistic interview with mixed questions:
- Theory questions (PUT vs PATCH, Django signals)
- Coding questions (reverse string, find palindrome)
- Framework questions (Django, REST API)

Tests:
1. Answer quality (humanized, useful)
2. Performance (time to display in UI)
3. Code style (human-like variable names)
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

SERVER_URL = "http://localhost:8000"

# Realistic interview scenario
INTERVIEW_QUESTIONS = [
    {
        "type": "theory",
        "question": "What is the difference between PUT and PATCH?",
        "expected_keywords": ["PUT", "PATCH", "update", "replace", "partial"],
        "max_time": 3.0  # seconds
    },
    {
        "type": "coding",
        "question": "Write a function to reverse a string",
        "expected_keywords": ["def", "reverse", "return"],
        "check_human_style": True,
        "avoid_ai_names": ["reverse_string", "input_string", "reversed_string"],
        "max_time": 2.0
    },
    {
        "type": "theory",
        "question": "What are Django signals?",
        "expected_keywords": ["Django", "signal", "event", "receiver"],
        "max_time": 3.0
    },
    {
        "type": "coding",
        "question": "Find palindrome in a string",
        "expected_keywords": ["def", "palindrome", "return"],
        "check_human_style": True,
        "avoid_ai_names": ["is_palindrome", "input_string", "check_palindrome"],
        "max_time": 2.0
    },
    {
        "type": "theory",
        "question": "Explain REST API authentication methods",
        "expected_keywords": ["authentication", "token", "JWT", "session"],
        "max_time": 3.0
    },
    {
        "type": "coding",
        "question": "Find even numbers in a list",
        "expected_keywords": ["def", "even", "return"],
        "check_human_style": True,
        "avoid_ai_names": ["find_even_numbers", "number_list", "even_numbers"],
        "max_time": 2.0
    },
    {
        "type": "theory",
        "question": "What is the difference between list and tuple in Python?",
        "expected_keywords": ["list", "tuple", "mutable", "immutable"],
        "max_time": 3.0
    },
]


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_test(num, total, question):
    print(f"\n{CYAN}{'─'*80}{RESET}")
    print(f"{CYAN}Question {num}/{total}: {question['type'].upper()}{RESET}")
    print(f"{CYAN}{'─'*80}{RESET}")
    print(f"{BOLD}Q: {question['question']}{RESET}")


def print_metric(name, value, threshold=None, unit="s"):
    if threshold:
        if value <= threshold:
            color = GREEN
            status = "✓ GOOD"
        else:
            color = YELLOW
            status = "⚠ SLOW"
        print(f"  {name}: {color}{value:.3f}{unit}{RESET} ({status}, target: <{threshold}{unit})")
    else:
        print(f"  {name}: {value:.3f}{unit}")


def print_pass(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_fail(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def send_question_via_api(question_text, source="chat"):
    """Send question via API (simulates chat/CC)."""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/cc_question",
            json={
                "question": question_text,
                "source": source,
                "platform": "test"
            },
            timeout=15
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)


def get_latest_answer():
    """Get the latest answer from API."""
    try:
        response = requests.get(f"{SERVER_URL}/api/answers", timeout=5)
        if response.status_code == 200:
            answers = response.json()
            if answers:
                return answers[0]  # Latest answer (newest first)
        return None
    except Exception as e:
        return None


def check_answer_quality(answer_text, question_config):
    """Check if answer is humanized and useful."""
    issues = []
    
    # Check for expected keywords
    found_keywords = []
    missing_keywords = []
    for keyword in question_config.get("expected_keywords", []):
        if keyword.lower() in answer_text.lower():
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Check for AI-style names (if coding question)
    if question_config.get("check_human_style"):
        ai_names_found = []
        for ai_name in question_config.get("avoid_ai_names", []):
            if ai_name in answer_text:
                ai_names_found.append(ai_name)
        
        if ai_names_found:
            issues.append(f"AI-style names found: {', '.join(ai_names_found)}")
    
    # Check for bullet format (theory questions)
    if question_config["type"] == "theory":
        bullet_count = answer_text.count('\n-')
        if bullet_count < 2:
            issues.append(f"Expected bullet points, found {bullet_count}")
    
    # Check for code format (coding questions)
    if question_config["type"] == "coding":
        if "def " not in answer_text:
            issues.append("Missing function definition")
    
    return {
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "issues": issues,
        "quality_score": len(found_keywords) / max(len(question_config.get("expected_keywords", [1])), 1)
    }


def test_interview_scenario():
    """Run complete interview scenario test."""
    print_header("REAL INTERVIEW FLOW TEST")
    print(f"{CYAN}Simulating realistic interview with {len(INTERVIEW_QUESTIONS)} questions{RESET}\n")
    
    # Check server is running
    try:
        response = requests.get(f"{SERVER_URL}/api/ip", timeout=2)
        if response.status_code != 200:
            print_fail("Server not responding")
            return False
    except:
        print_fail("Server not running. Start with: ./run.sh")
        return False
    
    print_pass("Server is running")
    
    results = []
    total_time = 0
    
    for i, question_config in enumerate(INTERVIEW_QUESTIONS, 1):
        print_test(i, len(INTERVIEW_QUESTIONS), question_config)
        
        # Send question
        start_time = time.time()
        success, response = send_question_via_api(question_config["question"])
        
        if not success:
            print_fail(f"Failed to send question: {response}")
            results.append({
                "question": question_config["question"],
                "success": False,
                "error": str(response)
            })
            continue
        
        # Wait a bit for processing
        time.sleep(0.5)
        
        # Get answer
        answer = get_latest_answer()
        end_time = time.time()
        elapsed = end_time - start_time
        total_time += elapsed
        
        if not answer:
            print_fail("No answer received")
            results.append({
                "question": question_config["question"],
                "success": False,
                "error": "No answer"
            })
            continue
        
        # Check answer quality
        quality = check_answer_quality(answer.get("answer", ""), question_config)
        
        # Display results
        print(f"\n{BOLD}Answer:{RESET}")
        answer_text = answer.get("answer", "")
        
        # Truncate for display
        if len(answer_text) > 300:
            print(f"{answer_text[:300]}...")
        else:
            print(answer_text)
        
        print(f"\n{BOLD}Metrics:{RESET}")
        print_metric("Response time", elapsed, question_config.get("max_time"))
        print_metric("Quality score", quality["quality_score"], 0.7, unit="")
        
        if quality["found_keywords"]:
            print_pass(f"Keywords found: {', '.join(quality['found_keywords'])}")
        
        if quality["missing_keywords"]:
            print_warning(f"Missing keywords: {', '.join(quality['missing_keywords'])}")
        
        if quality["issues"]:
            for issue in quality["issues"]:
                print_warning(issue)
        else:
            print_pass("No quality issues")
        
        # Check human-style code
        if question_config.get("check_human_style"):
            if not quality["issues"]:
                print_pass("Code uses human-like variable names ✓")
        
        results.append({
            "question": question_config["question"],
            "type": question_config["type"],
            "success": True,
            "time": elapsed,
            "quality": quality,
            "answer_length": len(answer_text)
        })
        
        # Small delay between questions (realistic)
        time.sleep(1)
    
    # Summary
    print_header("TEST SUMMARY")
    
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    theory_times = [r["time"] for r in results if r.get("type") == "theory" and r.get("success")]
    coding_times = [r["time"] for r in results if r.get("type") == "coding" and r.get("success")]
    
    print(f"{BOLD}Overall Results:{RESET}")
    print(f"  Questions answered: {successful}/{total}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time per question: {total_time/max(total, 1):.2f}s")
    
    if theory_times:
        print(f"\n{BOLD}Theory Questions:{RESET}")
        print(f"  Count: {len(theory_times)}")
        print(f"  Average time: {sum(theory_times)/len(theory_times):.2f}s")
        print(f"  Fastest: {min(theory_times):.2f}s")
        print(f"  Slowest: {max(theory_times):.2f}s")
    
    if coding_times:
        print(f"\n{BOLD}Coding Questions:{RESET}")
        print(f"  Count: {len(coding_times)}")
        print(f"  Average time: {sum(coding_times)/len(coding_times):.2f}s")
        print(f"  Fastest: {min(coding_times):.2f}s")
        print(f"  Slowest: {max(coding_times):.2f}s")
    
    # Quality analysis
    quality_scores = [r["quality"]["quality_score"] for r in results if r.get("success") and "quality" in r]
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n{BOLD}Answer Quality:{RESET}")
        print(f"  Average quality score: {avg_quality:.2f}")
        if avg_quality >= 0.8:
            print_pass("Excellent quality")
        elif avg_quality >= 0.6:
            print_pass("Good quality")
        else:
            print_warning("Quality needs improvement")
    
    # Human-style code check
    coding_results = [r for r in results if r.get("type") == "coding" and r.get("success")]
    if coding_results:
        human_style_count = sum(1 for r in coding_results if not r["quality"]["issues"])
        print(f"\n{BOLD}Code Style:{RESET}")
        print(f"  Human-like code: {human_style_count}/{len(coding_results)}")
        if human_style_count == len(coding_results):
            print_pass("All code uses human-like names ✓")
        elif human_style_count > len(coding_results) / 2:
            print_pass("Most code uses human-like names")
        else:
            print_warning("Some code uses AI-style names")
    
    # Final verdict
    print(f"\n{BOLD}{'='*80}{RESET}")
    if successful == total and avg_quality >= 0.7:
        print(f"{GREEN}{BOLD}✓ INTERVIEW READY!{RESET}")
        print(f"{GREEN}All questions answered with good quality{RESET}")
        print(f"{GREEN}Performance is acceptable for real interviews{RESET}")
        return True
    elif successful >= total * 0.8:
        print(f"{YELLOW}{BOLD}⚠ MOSTLY READY{RESET}")
        print(f"{YELLOW}Most questions answered, some improvements needed{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}✗ NEEDS IMPROVEMENT{RESET}")
        print(f"{RED}Several issues detected{RESET}")
        return False


if __name__ == "__main__":
    try:
        success = test_interview_scenario()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}Test failed with error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
