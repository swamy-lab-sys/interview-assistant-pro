#!/usr/bin/env python3
"""
Test script for Web UI functionality

Tests:
1. Web UI starts successfully
2. Answers log is created
3. Web server responds
4. HTML is rendered correctly
"""

import time
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, '/home/venkat/InterviewVoiceAssistant')

import web_ui
import output_manager

def test_web_ui():
    """Test web UI functionality"""
    print("=" * 60)
    print("Testing Web UI Functionality")
    print("=" * 60)
    
    # Test 1: Ensure directory exists
    print("\n1. Testing directory creation...")
    output_manager.ensure_answers_dir()
    if web_ui.ANSWERS_DIR.exists():
        print("   ✓ Answers directory exists")
    else:
        print("   ❌ Failed to create answers directory")
        return False
    
    # Test 2: Write test data
    print("\n2. Writing test Q&A data...")
    output_manager.clear_answer_buffer()
    output_manager.write_header("What is Python?")
    output_manager.write_answer_chunk("Python is a high-level, interpreted programming language.")
    output_manager.write_footer()
    
    output_manager.write_header("Explain REST API")
    output_manager.write_answer_chunk("REST (Representational State Transfer) is an architectural style for designing networked applications.")
    output_manager.write_footer()
    
    print("   ✓ Test data written to answers.log")
    
    # Test 3: Parse answers log
    print("\n3. Testing log parser...")
    qa_pairs = web_ui.parse_answers_log()
    if len(qa_pairs) >= 2:
        print(f"   ✓ Parsed {len(qa_pairs)} Q&A pairs")
        print(f"   ✓ First question: {qa_pairs[0]['question'][:50]}...")
    else:
        print(f"   ❌ Expected 2+ Q&A pairs, got {len(qa_pairs)}")
        return False
    
    # Test 4: Start web server
    print("\n4. Starting web server...")
    web_ui.start_web_ui()
    time.sleep(2)  # Give server time to start
    print("   ✓ Web server started (background thread)")
    
    # Test 5: Test HTTP endpoint
    print("\n5. Testing HTTP endpoint...")
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:8080', timeout=5)
        html = response.read().decode('utf-8')
        
        if 'Interview Assistant' in html:
            print("   ✓ Web page loads successfully")
        else:
            print("   ❌ Web page missing expected content")
            return False
            
        if 'What is Python?' in html:
            print("   ✓ Q&A data appears in HTML")
        else:
            print("   ❌ Q&A data not found in HTML")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to connect to web server: {e}")
        return False
    
    # Test 6: Get web UI URL
    print("\n6. Testing URL helper...")
    url = web_ui.get_web_ui_url()
    print(f"   ✓ Web UI URL: {url}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print(f"\n📱 Open in browser: {url}")
    print("\nPress Ctrl+C to stop the web server...")
    
    # Keep server running for manual testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Stopping test server...")
    
    return True

if __name__ == "__main__":
    try:
        success = test_web_ui()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
