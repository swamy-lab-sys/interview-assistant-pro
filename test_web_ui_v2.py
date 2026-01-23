#!/usr/bin/env python3
"""
Test script for upgraded Web UI with syntax highlighting and SSE

Tests:
1. Structured answer storage (JSONL)
2. Code block detection
3. Web server with SSE
4. Syntax highlighting
5. Real-time updates
"""

import sys
import time
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, '/home/venkat/InterviewVoiceAssistant')

import answer_storage

def test_answer_storage():
    """Test structured answer storage"""
    print("=" * 60)
    print("Testing Structured Answer Storage")
    print("=" * 60)
    
    # Clear existing answers
    print("\n1. Clearing existing answers...")
    answer_storage.clear_answers()
    print("   ✓ Answers cleared")
    
    # Test 1: Simple answer
    print("\n2. Testing simple Q&A...")
    answer_storage.start_new_answer("What is Python?")
    answer_storage.append_answer_chunk("Python is a high-level, ")
    answer_storage.append_answer_chunk("interpreted programming language.")
    answer_storage.finalize_answer()
    print("   ✓ Simple answer saved")
    
    # Test 2: Answer with code block
    print("\n3. Testing answer with code block...")
    answer_storage.start_new_answer("Write a function to reverse a string")
    answer_storage.append_answer_chunk("Here's a Python function:\n\n")
    answer_storage.append_answer_chunk("```python\n")
    answer_storage.append_answer_chunk("def reverse_string(s):\n")
    answer_storage.append_answer_chunk("    return s[::-1]\n")
    answer_storage.append_answer_chunk("```\n\n")
    answer_storage.append_answer_chunk("This uses Python's slice notation.")
    answer_storage.finalize_answer()
    print("   ✓ Code block answer saved")
    
    # Test 3: Multi-paragraph answer
    print("\n4. Testing multi-paragraph answer...")
    answer_storage.start_new_answer("Explain REST API")
    answer_storage.append_answer_chunk("REST (Representational State Transfer) is an architectural style.\n\n")
    answer_storage.append_answer_chunk("Key principles:\n")
    answer_storage.append_answer_chunk("- Stateless communication\n")
    answer_storage.append_answer_chunk("- Resource-based URLs\n")
    answer_storage.append_answer_chunk("- HTTP methods (GET, POST, PUT, DELETE)")
    answer_storage.finalize_answer()
    print("   ✓ Multi-paragraph answer saved")
    
    # Verify storage
    print("\n5. Verifying stored answers...")
    answers = answer_storage.get_all_answers()
    print(f"   ✓ Retrieved {len(answers)} answers")
    
    if len(answers) >= 3:
        print(f"   ✓ First question: {answers[0]['question']}")
        print(f"   ✓ Second question: {answers[1]['question']}")
        print(f"   ✓ Third question: {answers[2]['question']}")
    
    # Check JSONL file
    print("\n6. Checking JSONL file...")
    jsonl_path = answer_storage.get_answers_file_path()
    print(f"   ✓ File path: {jsonl_path}")
    
    with open(jsonl_path, 'r') as f:
        lines = f.readlines()
        print(f"   ✓ File has {len(lines)} lines")
        
        # Verify each line is valid JSON
        for i, line in enumerate(lines):
            try:
                obj = json.loads(line)
                assert 'question' in obj
                assert 'answer' in obj
                assert 'timestamp' in obj
            except Exception as e:
                print(f"   ❌ Line {i+1} is invalid: {e}")
                return False
        
        print("   ✓ All lines are valid JSON")
    
    print("\n" + "=" * 60)
    print("✅ ALL STORAGE TESTS PASSED")
    print("=" * 60)
    
    return True


def test_web_server():
    """Test web server (requires manual verification)"""
    print("\n" + "=" * 60)
    print("Testing Web Server")
    print("=" * 60)
    
    print("\n📝 To test the web server:")
    print("\n1. In another terminal, run:")
    print("   cd /home/venkat/InterviewVoiceAssistant")
    print("   source venv/bin/activate")
    print("   python3 web/server.py")
    print("\n2. Open browser to: http://localhost:8000")
    print("\n3. Verify:")
    print("   ✓ Page loads with dark theme")
    print("   ✓ 3 Q&A cards are displayed")
    print("   ✓ Code block has syntax highlighting")
    print("   ✓ Latest card has blue border")
    print("   ✓ Live status indicator is pulsing")
    print("\n4. Test real-time updates:")
    print("   - Keep browser open")
    print("   - Run: python3 main.py text")
    print("   - Type a question")
    print("   - Watch answer appear in browser automatically")
    
    print("\n" + "=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        # Test storage
        if not test_answer_storage():
            sys.exit(1)
        
        # Show web server test instructions
        test_web_server()
        
        print("\n✅ Setup complete! Ready to test web UI.")
        print("\nNext steps:")
        print("1. Start web server: python3 web/server.py")
        print("2. Open browser: http://localhost:8000")
        print("3. Start interview: python3 main.py text")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
