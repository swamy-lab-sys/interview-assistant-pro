#!/usr/bin/env python3
"""
Interview Assistant Pro - Client
Connects to the SaaS backend for AI responses.
Audio processing happens locally for privacy.
"""

import os
import sys
import httpx
import asyncio
from pathlib import Path

# Configuration
API_URL = os.environ.get("IVA_API_URL", "https://interview-assistant-api.onrender.com")
API_KEY = os.environ.get("IVA_API_KEY", "")

CONFIG_FILE = Path.home() / ".interview_assistant" / "config"


def load_api_key():
    global API_KEY
    if API_KEY:
        return API_KEY
    if CONFIG_FILE.exists():
        API_KEY = CONFIG_FILE.read_text().strip()
        return API_KEY
    return None


def save_api_key(key: str):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(key)


class InterviewClient:
    def __init__(self):
        self.api_key = load_api_key()
        self.resume = ""
        self.headers = {}
        if self.api_key:
            self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def set_resume(self, resume_text: str):
        self.resume = resume_text

    async def login(self, email: str, password: str) -> dict:
        """Login and get API key"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.api_key = data["user"]["api_key"]
                self.headers = {"Authorization": f"Bearer {self.api_key}"}
                save_api_key(self.api_key)
                return data
            else:
                raise Exception(f"Login failed: {response.text}")

    async def register(self, email: str, password: str, full_name: str = None) -> dict:
        """Register new account"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/auth/register",
                json={"email": email, "password": password, "full_name": full_name}
            )
            if response.status_code == 200:
                data = response.json()
                self.api_key = data["user"]["api_key"]
                self.headers = {"Authorization": f"Bearer {self.api_key}"}
                save_api_key(self.api_key)
                return data
            else:
                raise Exception(f"Registration failed: {response.text}")

    async def get_account_info(self) -> dict:
        """Get account info and usage"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/auth/me",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get account info: {response.text}")

    async def ask_question(self, question: str, is_coding: bool = False) -> str:
        """Send question to AI and get response"""
        if not self.api_key:
            raise Exception("Not logged in. Run: interview-assistant login")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_URL}/api/ask",
                headers=self.headers,
                json={
                    "question": question,
                    "resume": self.resume,
                    "is_coding": is_coding
                }
            )
            if response.status_code == 200:
                data = response.json()
                return data["answer"]
            elif response.status_code == 429:
                raise Exception("Monthly limit reached. Upgrade to Pro for unlimited access.")
            else:
                raise Exception(f"API error: {response.text}")

    async def get_checkout_url(self) -> str:
        """Get Stripe checkout URL for upgrade"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/billing/create-checkout",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()["checkout_url"]
            else:
                raise Exception(f"Failed to create checkout: {response.text}")


# ============ CLI Interface ============

async def main():
    client = InterviewClient()

    if len(sys.argv) < 2:
        print("""
Interview Assistant Pro - Client

Usage:
  interview-assistant login              Login to your account
  interview-assistant register           Create new account
  interview-assistant status             Check account status
  interview-assistant upgrade            Upgrade to Pro
  interview-assistant ask "question"     Ask a question
  interview-assistant voice              Start voice mode (requires local STT)
  interview-assistant text               Start interactive text mode

Environment Variables:
  IVA_API_KEY    Your API key (or login to save automatically)
  IVA_API_URL    API server URL (default: production)
        """)
        return

    command = sys.argv[1]

    if command == "login":
        email = input("Email: ")
        password = input("Password: ")
        try:
            data = await client.login(email, password)
            print(f"\n✓ Logged in as {data['user']['email']}")
            print(f"  Tier: {data['user']['subscription_tier']}")
            print(f"  Questions this month: {data['user']['questions_this_month']}/{data['user']['questions_limit']}")
            print(f"\nAPI Key saved to ~/.interview_assistant/config")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif command == "register":
        email = input("Email: ")
        password = input("Password: ")
        full_name = input("Full Name (optional): ") or None
        try:
            data = await client.register(email, password, full_name)
            print(f"\n✓ Account created!")
            print(f"  Email: {data['user']['email']}")
            print(f"  Free tier: {data['user']['questions_limit']} questions/month")
            print(f"\nAPI Key saved. You can now use 'interview-assistant voice'")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif command == "status":
        try:
            data = await client.get_account_info()
            print(f"\n📊 Account Status")
            print(f"  Email: {data['email']}")
            print(f"  Tier: {data['subscription_tier'].upper()}")
            print(f"  Questions: {data['questions_this_month']}/{data['questions_limit']} this month")
            remaining = data['questions_limit'] - data['questions_this_month']
            print(f"  Remaining: {remaining}")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif command == "upgrade":
        try:
            url = await client.get_checkout_url()
            print(f"\n🚀 Upgrade to Pro ($29/month)")
            print(f"  - Unlimited questions")
            print(f"  - Priority support")
            print(f"\nOpen this URL to upgrade:")
            print(f"  {url}")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: interview-assistant ask \"your question here\"")
            return
        question = " ".join(sys.argv[2:])
        try:
            print("Thinking...")
            answer = await client.ask_question(question)
            print(f"\n{answer}")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif command == "text":
        print("\n🎤 Interview Assistant - Text Mode")
        print("Type questions and press Enter. Type 'quit' to exit.\n")

        # Load resume if exists
        resume_file = Path("resume.txt")
        if resume_file.exists():
            client.set_resume(resume_file.read_text())
            print("✓ Loaded resume.txt\n")

        while True:
            try:
                question = input("\n❓ Question: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                if not question:
                    continue

                print("Thinking...")
                answer = await client.ask_question(question)
                print(f"\n💡 Answer:\n{answer}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"✗ Error: {e}")

        print("\nGoodbye!")

    elif command == "voice":
        print("\n🎤 Voice mode requires the full local installation.")
        print("This connects local audio capture to the cloud API.")
        print("\nRun the main application with:")
        print("  python main.py voice --api-mode")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
