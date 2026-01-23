#!/usr/bin/env python3
"""
Interview Assistant Pro - Client Application
Get AI-powered answers during technical interviews
"""

import os
import sys
import httpx

# Configuration
API_URL = "https://interview-assistant-api-pro.onrender.com"
VERSION = "1.0.0"

def get_api_key():
    """Get API key from environment or config file"""
    # Check environment
    api_key = os.environ.get("IVA_API_KEY", "")
    if api_key:
        return api_key

    # Check config file
    config_path = os.path.expanduser("~/.interview_assistant_pro/api_key")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return f.read().strip()

    return None


def save_api_key(api_key):
    """Save API key to config file"""
    config_path = os.path.expanduser("~/.interview_assistant_pro/api_key")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        f.write(api_key)


def verify_api_key(api_key):
    """Verify API key with server"""
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                f"{API_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


def ask_question(api_key, question, is_coding=False):
    """Send question to API and get answer"""
    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(
                f"{API_URL}/api/ask",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "question": question,
                    "is_coding": is_coding
                }
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                return {"error": "Monthly question limit reached. Upgrade to Pro!"}
            else:
                return {"error": f"Server error: {response.text}"}
    except httpx.TimeoutException:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        return {"error": str(e)}


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    print("\n" + "=" * 60)
    print("     INTERVIEW ASSISTANT PRO")
    print("     AI-Powered Interview Help")
    print("=" * 60)


def print_answer(answer):
    print("\n" + "-" * 60)
    print("  SUGGESTED ANSWER")
    print("-" * 60)
    print()
    print(answer)
    print()
    print("-" * 60)


def main():
    clear_screen()
    print_header()

    # Get API key
    api_key = get_api_key()

    if not api_key:
        print("\n  First time setup required!")
        print("\n  1. Create account at:")
        print(f"     {API_URL}/register")
        print("\n  2. Get your API key from the dashboard")
        print()
        api_key = input("  Enter your API key: ").strip()

        if not api_key:
            print("\n  No API key provided. Exiting.")
            sys.exit(1)

    # Verify API key
    print("\n  Verifying your account...")
    user = verify_api_key(api_key)

    if not user:
        print("\n  Invalid API key. Please check and try again.")
        print(f"  Get a new key at: {API_URL}/register")
        sys.exit(1)

    # Save valid key
    save_api_key(api_key)

    # Show user info
    clear_screen()
    print_header()
    print(f"\n  Welcome, {user.get('email', 'User')}!")
    print(f"  Plan: {user.get('subscription_tier', 'free').upper()}")
    print(f"  Questions remaining: {user.get('questions_limit', 0) - user.get('questions_this_month', 0)}")

    print("\n" + "=" * 60)
    print("  HOW TO USE")
    print("=" * 60)
    print("\n  Type the interview question and press Enter.")
    print("  For coding questions, start with 'code:'")
    print("  Type 'quit' to exit")
    print()

    # Main loop
    while True:
        try:
            print()
            question = input("  Question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n  Good luck with your interview!")
                break

            if not question:
                continue

            # Check for coding question
            is_coding = question.lower().startswith('code:')
            if is_coding:
                question = question[5:].strip()

            print("\n  Thinking...")
            result = ask_question(api_key, question, is_coding)

            if "error" in result:
                print(f"\n  Error: {result['error']}")
            else:
                print_answer(result.get("answer", "No answer received"))
                remaining = result.get("questions_remaining", "?")
                print(f"  ({remaining} questions remaining)")

        except KeyboardInterrupt:
            print("\n\n  Goodbye!")
            break
        except Exception as e:
            print(f"\n  Error: {e}")


if __name__ == "__main__":
    main()
