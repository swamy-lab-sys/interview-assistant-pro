
import sys
import os
from llm_client import get_streaming_interview_answer

print("Testing LLM Streaming...")
question = "What is a decorator in Python?"
print(f"Question: {question}")

count = 0
try:
    for chunk in get_streaming_interview_answer(question):
        print(f"Chunk: '{chunk}'")
        count += 1
except Exception as e:
    print(f"Error: {e}")

print(f"Total chunks: {count}")
if count == 0:
    print("FAIL: No chunks received")
else:
    print("SUCCESS: Stream received")
