
import time
import os
import sys

# Mock configuration
class Config:
    VERBOSE = True
    LLM_MAX_TOKENS_INTERVIEW = 100
    LLM_MODEL = "claude-3-haiku-20240307"

# Mock audio for "What is CI/CD?"
# Just checking logical flow speed, not actual STT (since we can't emit audio here)
def test_logical_speed():
    print("--- TESTING LOGICAL PIPELINE SPEED ---")
    
    # 1. Import Time
    import llm_client
    start_time = time.time()
    
    question = "What is CI/CD?"
    print(f"Question: {question}")
    
    # 2. LLM Call
    print("Generating Answer (Haiku)...")
    llm_start = time.time()
    answer = llm_client.get_interview_answer(question, "Resume text", "JD text")
    llm_end = time.time()
    
    print(f"Answer: {answer[:100]}...")
    print(f"LLM Time: {(llm_end - llm_start)*1000:.0f}ms")
    
    if (llm_end - llm_start) < 2.5:
        print("PASS: LLM is fast enough (< 2.5s)")
    else:
        print("FAIL: LLM is too slow")

if __name__ == "__main__":
    test_logical_speed()
