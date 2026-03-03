#!/usr/bin/env python3
"""
Web Server for Interview Voice Assistant

Provides real-time UI for viewing interview answers.

Features:
- Server-Sent Events (SSE) for real-time updates
- Syntax highlighting for code blocks
- Mobile-first responsive design
- Performance metrics display
"""

import sys
import os
import json
import time
import hashlib
import re
import argparse
from pathlib import Path
from flask import Flask, render_template, Response, jsonify, request

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
import answer_storage
import llm_client # Needed for direct API calls
import fragment_context

# Import debug logger
try:
    import debug_logger as dlog
    LOGGING_ENABLED = True
except ImportError:
    LOGGING_ENABLED = False
    class DlogStub:
        def log(self, *args, **kwargs): pass
    dlog = DlogStub()

# Configuration
DEFAULT_PORT = 8000
app = Flask(__name__)

# Disable Flask logging
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Global state for latest generated code AND control
latest_code = {
    'code': '',
    'timestamp': 0,
    'platform': '',
    'source': '',      # 'chat', 'editor', 'url'
    'status': 'idle',  # idle, generating, paused, complete, error
    'mode': 'auto',    # 'auto' (auto-type) or 'view' (view-only)
    'control': 'stopped'  # 'stopped', 'running', 'paused'
}

# Deduplication: track recent problems to avoid duplicates
recent_problems = {
    'last_hash': '',
    'last_time': 0,
}
DEDUP_WINDOW_SECONDS = 10  # Ignore same problem within 10 seconds


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    # No Cache headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/')
def index():
    """Serve main page."""
    return render_template('index.html')


@app.route('/api/answers')
def get_answers():
    """Get all answers."""
    answers = answer_storage.get_all_answers()
    return jsonify(answers)


UPLOADED_RESUME_PATH = Path.home() / ".interview_assistant" / "uploaded_resume.txt"

@app.route('/api/upload_resume', methods=['POST'])
def upload_resume():
    """Upload resume file. Saves as plain text to shared location."""
    from flask import request
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            from resume_loader import invalidate_resume_cache

            UPLOADED_RESUME_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Read file content as text
            content = file.read()
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            # Skip binary PDF content - extract only readable text
            if text.startswith('%PDF'):
                # Try pdftotext if available
                import subprocess, tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                try:
                    result = subprocess.run(['pdftotext', tmp_path, '-'], capture_output=True, text=True, timeout=10)
                    text = result.stdout.strip()
                except Exception:
                    text = ""
                finally:
                    os.unlink(tmp_path)

            if not text.strip():
                return jsonify({'error': 'Could not extract text from file'}), 400

            # Save as plain text
            with open(UPLOADED_RESUME_PATH, 'w', encoding='utf-8') as f:
                f.write(text)

            invalidate_resume_cache()
            print(f"[SERVER] Resume uploaded: {len(text)} chars")
            return jsonify({'success': True, 'message': f'Resume uploaded ({len(text)} chars)'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Unknown error'}), 400


@app.route('/api/resume_status')
def resume_status():
    """Check if resume was uploaded via UI."""
    uploaded = UPLOADED_RESUME_PATH.exists() and UPLOADED_RESUME_PATH.stat().st_size > 0
    return jsonify({'uploaded': uploaded})


@app.route('/api/save_jd', methods=['POST'])
def save_jd():
    """Save job description text."""
    from flask import request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        from config import JD_PATH
        jd_path = Path.cwd() / JD_PATH
        with open(jd_path, 'w') as f:
            f.write(data['text'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_jd')
def get_jd():
    """Get current job description."""
    try:
        from config import JD_PATH
        jd_path = Path.cwd() / JD_PATH
        if jd_path.exists():
            with open(jd_path, 'r') as f:
                return jsonify({'text': f.read()})
        return jsonify({'text': ''})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ip')
def get_ip():
    """Get server LAN IP address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    
    response = jsonify({'ip': IP})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/stream')
def stream():
    """SSE stream for real-time updates - OPTIMIZED for low latency."""
    def event_stream():
        last_data = ""
        last_mtime = 0.0
        answer_file = str(answer_storage.CURRENT_ANSWER_FILE)

        while True:
            try:
                # Check file mtime first to avoid unnecessary reads
                try:
                    mtime = os.path.getmtime(answer_file)
                except OSError:
                    mtime = 0.0

                if mtime != last_mtime:
                    last_mtime = mtime
                    answers = answer_storage.get_all_answers()
                    current_data = json.dumps(answers)

                    if current_data != last_data:
                        yield f"data: {current_data}\n\n"
                        last_data = current_data
            except GeneratorExit:
                return
            except Exception:
                pass

            time.sleep(0.1)  # 100ms polling with mtime guard

    response = Response(event_stream(), mimetype='text/event-stream')
    # Disable buffering for real-time streaming
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
    response.headers['Connection'] = 'keep-alive'
    return response


@app.route('/api/stt_model', methods=['GET'])
def get_stt_model():
    """Get current STT model name."""
    try:
        import stt
        return jsonify({'model': stt.model_name or config.STT_MODEL})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stt_model', methods=['POST'])
def set_stt_model():
    """Change STT model. Reloads the Whisper model."""
    data = request.get_json()
    if not data or 'model' not in data:
        return jsonify({'error': 'No model specified'}), 400

    new_model = data['model']
    allowed = ['tiny.en', 'base.en', 'small.en', 'medium.en']
    if new_model not in allowed:
        return jsonify({'error': f'Invalid model. Allowed: {allowed}'}), 400

    try:
        import stt
        old_model = stt.model_name or config.STT_MODEL
        if new_model == old_model:
            return jsonify({'model': old_model, 'changed': False})

        print(f"[SERVER] STT model change: {old_model} -> {new_model}")
        config.STT_MODEL = new_model
        stt.DEFAULT_MODEL = new_model
        stt.load_model(new_model)
        print(f"[SERVER] STT model loaded: {new_model}")
        return jsonify({'model': new_model, 'changed': True})
    except Exception as e:
        print(f"[SERVER] STT model change failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs')
def get_logs():
    """Get recent debug logs."""
    try:
        log_file = Path.home() / ".interview_assistant" / "logs" / "debug.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({"logs": [l.strip() for l in lines[-100:]]})
        return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/performance')
def get_performance():
    """Get recent performance logs."""
    try:
        log_file = Path.home() / ".interview_assistant" / "logs" / "performance.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return jsonify({"logs": [l.strip() for l in lines[-50:]]})
        return jsonify({"logs": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clear_session', methods=['POST'])
def clear_session():
    """Manually clear all Q&A history (start fresh interview session)."""
    try:
        answer_storage.clear_all(force_clear=True)
        print("[API] 🗑️  Session cleared manually - starting fresh")
        return jsonify({'status': 'cleared', 'message': 'All Q&A history cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _ensure_example_call(lines):
    """LLM now generates code with examples, so just return as-is."""
    return lines


def extract_code_from_answer(answer_text):
    """Parse markdown code blocks from an answer into clean lines.

    Returns (language, lines) or (None, []) if no code block found.
    """
    match = re.search(r'```(\w*)\n(.*?)```', answer_text, re.DOTALL)
    if match:
        lang = match.group(1) or 'python'
        code = match.group(2).rstrip('\n')
        lines = code.split('\n')
        return lang, _ensure_example_call(lines)
    
    stripped = answer_text.strip()
    if not stripped:
        return None, []
    
    if (
        re.match(r'^(def |class |import |from |for |while |if |print\()', stripped) or
        '\ndef ' in stripped or
        '\nclass ' in stripped or
        '\nprint(' in stripped or
        (stripped.count('\n') >= 2 and '(' in stripped and ':' in stripped)
    ):
        lines = stripped.split('\n')
        return 'python', _ensure_example_call(lines)
    
    return None, []


@app.route('/api/code_payload')
def code_payload():
    """Return the latest code answer for the Chrome extension."""
    answers = answer_storage.get_all_answers()
    # Find the most recent answer that contains code
    for ans in answers:
        if not ans.get('answer') or not ans.get('is_complete'):
            continue
        lang, lines = extract_code_from_answer(ans['answer'])
        if lines:
            code_text = '\n'.join(lines)
            code_id = hashlib.md5(code_text.encode()).hexdigest()[:12]
            return jsonify({
                'has_code': True,
                'code_id': code_id,
                'language': lang,
                'lines': lines,
                'question': ans.get('question', ''),
                'timestamp': ans.get('timestamp', ''),
            })
    return jsonify({
        'has_code': False,
        'code_id': None,
        'language': None,
        'lines': [],
        'question': None,
        'timestamp': None,
    })


@app.route('/api/code_payloads')
def code_payloads():
    """Return ALL code answers numbered for the Chrome extension.

    Codes are numbered in chronological order (oldest = #1).
    """
    answers = answer_storage.get_all_answers()
    # get_all_answers returns newest-first, reverse to get chronological
    answers = list(reversed(answers))
    codes = []
    index = 1
    for ans in answers:
        if not ans.get('answer') or not ans.get('is_complete'):
            continue
        lang, lines = extract_code_from_answer(ans['answer'])
        if lines:
            code_text = '\n'.join(lines)
            code_id = hashlib.md5(code_text.encode()).hexdigest()[:12]
            codes.append({
                'index': index,
                'code_id': code_id,
                'language': lang,
                'lines': lines,
                'question': ans.get('question', ''),
                'timestamp': ans.get('timestamp', ''),
            })
            index += 1
    return jsonify({'codes': codes, 'count': len(codes)})


@app.route('/api/coding_state')
def coding_state():
    """Return whether a coding answer is currently being generated."""
    answers = answer_storage.get_all_answers()
    is_generating = False
    last_code_ts = None
    for ans in answers:
        if not ans.get('is_complete') and ans.get('answer'):
            _, lines = extract_code_from_answer(ans['answer'])
            if lines:
                is_generating = True
                break
        if ans.get('is_complete') and ans.get('answer'):
            _, lines = extract_code_from_answer(ans['answer'])
            if lines and not last_code_ts:
                last_code_ts = ans.get('timestamp')
    return jsonify({
        'is_generating': is_generating,
        'last_code_timestamp': last_code_ts,
    })


@app.route('/api/solve_problem', methods=['POST'])
def solve_problem():
    """
    Solve a coding problem from URL/Extension.
    Input: JSON { 'problem': str, 'editor': str, 'url': str }
    Output: JSON { 'solution': str }
    """
    global recent_problems
    from flask import request
    import time as time_module
    import hashlib

    data = request.get_json()
    if not data or 'problem' not in data:
        return jsonify({'error': 'No problem text provided'}), 400

    problem_text = data.get('problem', '')
    editor_content = data.get('editor', '')
    url = data.get('url', '')
    source = data.get('source', 'editor')  # 'chat' or 'editor'

    # Deduplication check
    problem_hash = hashlib.md5((problem_text[:500] + url).encode()).hexdigest()
    now = time_module.time()

    if (problem_hash == recent_problems['last_hash'] and
        now - recent_problems['last_time'] < DEDUP_WINDOW_SECONDS):
        print(f"[API] ⏭️  DUPLICATE - Skipping (same problem within {DEDUP_WINDOW_SECONDS}s)")
        return jsonify({'solution': '', 'duplicate': True})

    recent_problems['last_hash'] = problem_hash
    recent_problems['last_time'] = now

    # Log the request
    print(f"\n[API] ⚡ SOLVE REQUEST RECEIVED")
    print(f"      Source: {source}")
    print(f"      URL: {url}")
    dlog.log(f"[API] Solve request from {source} for {url}", "INFO")
    
    # Mark as generating
    global latest_code
    import time as time_module
    latest_code['status'] = 'generating'
    latest_code['platform'] = url
    latest_code['source'] = source
    latest_code['timestamp'] = time_module.time()
    
    # CHAT MODE: Force view-only
    if source == 'chat':
        latest_code['mode'] = 'view'
        print(f"      [CHAT MODE] Forced to VIEW-ONLY (never types into chat)")

    # Call LLM
    try:
        print(f"\n{'='*50}")
        print(f" QUESTION (Extracted Problem Text):")
        print(f"{'-'*50}\n{problem_text}\n{'-'*50}")
        
        solution = llm_client.get_platform_solution(problem_text, editor_content, url)
        
        # Store the generated code for display on localhost:8000
        latest_code['code'] = solution
        latest_code['status'] = 'complete'
        latest_code['timestamp'] = time_module.time()
        
        # ALSO store in answer_storage so it appears on homepage!
        # Extract a short question title from the problem
        q_lines = problem_text.strip().split('\n')
        short_question = q_lines[0][:100] if q_lines else 'Coding Problem'
        if url:
            # Extract platform from URL
            import re
            platform_match = re.search(r'(hackerrank|leetcode|codewars|codility|codesignal)', url.lower())
            if platform_match:
                short_question = f"[{platform_match.group(1).upper()}] {short_question}"
        
        answer_storage.set_complete_answer(
            question_text=short_question,
            answer_text=solution,
            metrics={'source': source, 'url': url[:50] if url else None}
        )
        
        print(f"\n ANSWER (Generated Code):")
        print(f"{'-'*50}\n{solution}\n{'-'*50}")
        print(f"✅ Solution generated ({len(solution)} chars)")
        print(f"{'='*50}\n")
        
        response = jsonify({'solution': solution})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        latest_code['status'] = 'error'
        dlog.log_error("[API] Solve failed", e)
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500


@app.route('/api/latest_code')
def get_latest_code():
    """Get the latest generated code for dual display."""
    global latest_code
    return jsonify(latest_code)


@app.route('/api/control/start', methods=['POST'])
def control_start():
    """Start/Resume code generation."""
    global latest_code
    latest_code['control'] = 'running'
    print("[CONTROL] ▶ START/RESUME")
    return jsonify({'status': 'running', 'mode': latest_code['mode']})


@app.route('/api/control/pause', methods=['POST'])
def control_pause():
    """Pause code generation."""
    global latest_code
    latest_code['control'] = 'paused'
    print("[CONTROL] ⏸ PAUSE")
    return jsonify({'status': 'paused', 'mode': latest_code['mode']})


@app.route('/api/control/stop', methods=['POST'])
def control_stop():
    """Stop code generation (hard kill)."""
    global latest_code
    latest_code['control'] = 'stopped'
    latest_code['status'] = 'idle'
    print("[CONTROL] ⛔ STOP")
    return jsonify({'status': 'stopped', 'mode': latest_code['mode']})


@app.route('/api/control/toggle_mode', methods=['POST'])
def control_toggle_mode():
    """Toggle between auto-type and view-only modes."""
    global latest_code
    latest_code['mode'] = 'view' if latest_code['mode'] == 'auto' else 'auto'
    mode_name = 'AUTO-TYPE' if latest_code['mode'] == 'auto' else 'VIEW-ONLY'
    print(f"[CONTROL] 🔁 MODE → {mode_name}")
    return jsonify({'mode': latest_code['mode'], 'status': latest_code['control']})


# ═══════════════════════════════════════════════
# GOOGLE MEET CC + CHAT CAPTURE API
# ═══════════════════════════════════════════════

cc_capture_state = {
    'enabled': False,
    'last_question': '',
    'last_timestamp': 0,
}


@app.route('/api/get_answer_by_index', methods=['GET'])
def get_answer_by_index():
    """
    Get a specific answer by its 1-based index (cronological).
    #1 = First question asked
    #2 = Second question asked
    #-1 or #0 = Latest question
    """
    try:
        from flask import request
        index_str = request.args.get('index', '0')
        index = int(index_str)
        
        # Get all answers (Newest -> Oldest)
        all_answers = answer_storage.get_all_answers()
        
        if not all_answers:
            return jsonify({'found': False, 'error': 'No questions found'}), 404
            
        # Chronological list (Oldest -> Newest)
        chronological_answers = list(reversed(all_answers))
        
        target_answer = None
        real_index = 0
        
        if index <= 0:
            # Get latest
            target_answer = chronological_answers[-1]
            real_index = len(chronological_answers)
        else:
            # 1-based index
            if 1 <= index <= len(chronological_answers):
                target_answer = chronological_answers[index - 1]
                real_index = index
            else:
                return jsonify({'found': False, 'error': f'Index {index} out of bounds (1-{len(chronological_answers)})'}), 404
        
        if target_answer:
            raw_answer = target_answer.get('answer', '')
            code = raw_answer

            # 1. Try to extract markdown code block first
            import re
            # Match ```python ... ``` or just ``` ... ```
            code_match = re.search(r'```(?:python|py)?\n(.*?)```', raw_answer, re.DOTALL | re.IGNORECASE)
            if code_match:
                code = code_match.group(1)
            else:
                # 2. If no markdown, but it looks like code (def function), use it all
                # Otherwise, if it's just text, it will be commented out by content.js
                pass

            return jsonify({
                'found': True,
                'index': real_index,
                'total': len(chronological_answers),
                'question': target_answer.get('question', ''),
                'code': code.strip()
            })
            
        return jsonify({'found': False, 'error': 'Answer not found'}), 404
        
    except ValueError:
        return jsonify({'found': False, 'error': 'Invalid index format'}), 400
    except Exception as e:
        return jsonify({'found': False, 'error': str(e)}), 500


@app.route('/api/cc_control', methods=['POST'])
def cc_control():
    """Control CC/Chat capture state."""
    global cc_capture_state
    from flask import request
    data = request.get_json() or {}
    action = data.get('action', '')

    if action == 'start':
        cc_capture_state['enabled'] = True
        print("[CC] 🎙️ CC/Chat capture ENABLED")
    elif action == 'stop':
        cc_capture_state['enabled'] = False
        print("[CC] ⏹️ CC/Chat capture DISABLED")
    elif action == 'status':
        pass

    return jsonify({
        'enabled': cc_capture_state['enabled'],
        'last_question': cc_capture_state['last_question'][:50] if cc_capture_state['last_question'] else '',
    })


@app.route('/api/cc_question', methods=['POST'])
def cc_question():
    """
    Receive a question captured from Google Meet CC/Chat.
    Process through the same pipeline as audio STT.
    """
    global cc_capture_state
    from flask import request
    import time as time_module

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    question_text = data.get('question', '').strip()
    source = data.get('source', 'cc')  # 'cc' or 'chat'
    platform = data.get('platform', 'google-meet')

    if not question_text:
        return jsonify({'error': 'Empty question'}), 400

    # Deduplicate (same question within 5 seconds)
    if (question_text == cc_capture_state['last_question'] and
        time_module.time() - cc_capture_state['last_timestamp'] < 5):
        return jsonify({'status': 'duplicate', 'skipped': True})

    cc_capture_state['last_question'] = question_text
    cc_capture_state['last_timestamp'] = time_module.time()

    print(f"\n[CC] 📝 Question from {source.upper()}: {question_text[:80]}...")

    # Fragment merging: merge with recent voice/chat context
    merged_text, was_merged = fragment_context.merge_with_context(question_text)
    if was_merged:
        print(f"[CC] 🔗 Fragment merged: '{question_text[:40]}' -> '{merged_text[:60]}'")
        question_text = merged_text

    # Validate question using existing validator
    try:
        from question_validator import validate_question
        is_valid, cleaned_question, rejection_reason = validate_question(question_text)

        if not is_valid:
            print(f"[CC] ❌ Question rejected: {rejection_reason}")
            return jsonify({
                'status': 'rejected',
                'reason': rejection_reason,
                'original': question_text[:50]
            })

        question_text = cleaned_question
        print(f"[CC] ✅ Question validated: {question_text[:60]}...")

    except ImportError:
        # If validator not available, proceed with original
        print("[CC] ⚠️ Validator not available, proceeding with original")

    # CHECK IF ALREADY ANSWERED - O(1) lookup via index dict
    existing = answer_storage.is_already_answered(question_text)
    if existing:
        print(f"[CC] Already answered, showing existing: {question_text[:40]}...")
        return jsonify({
            'status': 'already_answered',
            'question': question_text[:50],
            'answer_preview': existing.get('answer', '')[:100]
        })

    # Load resume (only if uploaded via UI) and JD for context
    try:
        from config import JD_PATH
        from resume_loader import load_resume, load_job_description
        resume_text = load_resume(UPLOADED_RESUME_PATH) if UPLOADED_RESUME_PATH.exists() else ""
        jd_text = load_job_description(Path.cwd() / JD_PATH)
    except:
        resume_text = ""
        jd_text = ""


    # Get answer from LLM
    # Chat questions are typically coding-focused (interviewers paste code/problems in chat)
    # So we prioritize coding answers for chat, theory for voice
    try:
        from question_validator import is_code_request
        
        # Check if it's explicitly a code request
        wants_code = is_code_request(question_text)
        
        # For CHAT questions: default to coding unless it's clearly a theory question
        if source == 'chat' and not wants_code:
            # Check if it's clearly a theory/explanation question
            theory_indicators = [
                'what is', 'what are', 'explain', 'describe', 'difference between',
                'why', 'how does', 'when would', 'tell me about', 'what does'
            ]
            is_theory = any(question_text.lower().strip().startswith(ind) for ind in theory_indicators)
            
            if not is_theory:
                # Chat question without clear theory indicator → treat as coding
                wants_code = True
                print(f"[CC] 💬 Chat question → treating as coding request")

        if wants_code:
            print(f"[CC] 💻 Code request detected")
            answer = llm_client.get_coding_answer(question_text)
        else:
            answer = llm_client.get_interview_answer(
                question_text,
                resume_text=resume_text,
                job_description=jd_text
            )

        if answer:
            # Store answer for display using the correct function
            answer_storage.set_complete_answer(
                question_text=question_text,
                answer_text=answer,
                metrics={'source': f'cc-{source}'}
            )
            # Save context for cross-source fragment merging
            fragment_context.save_context(question_text, f"chat-{source}")
            print(f"[CC] 💬 Answer generated ({len(answer)} chars)")

            return jsonify({
                'status': 'answered',
                'question': question_text[:50],
                'answer_length': len(answer),
            })
        else:
            print("[CC] 🔇 Empty answer (silence)")
            return jsonify({'status': 'silence'})

    except Exception as e:
        print(f"[CC] ❌ LLM error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cc_status')
def cc_status():
    """Get current CC capture status."""
    return jsonify({
        'enabled': cc_capture_state['enabled'],
        'last_question': cc_capture_state['last_question'][:50] if cc_capture_state['last_question'] else '',
        'last_timestamp': cc_capture_state['last_timestamp'],
    })


# ═══════════════════════════════════════════════
# VOICE MODE - PUSH-TO-TALK INTERFACE
# ═══════════════════════════════════════════════

@app.route('/voice')
def voice_ui():
    """Serve push-to-talk voice interface."""
    return render_template('voice.html')


@app.route('/voice/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Transcribe audio from browser MediaRecorder.
    Accepts audio blob, returns transcription.
    """
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400

    audio_file = request.files['audio']
    
    try:
        # Save temporary audio file
        import tempfile
        import numpy as np
        from pydub import AudioSegment
        
        # Save uploaded audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # Convert to the format expected by Whisper
            audio = AudioSegment.from_file(tmp_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
            
            # Transcribe using existing STT engine
            from stt import transcribe
            transcription, confidence = transcribe(samples)
            
            # Clean up
            os.unlink(tmp_path)
            
            if transcription and len(transcription.strip()) > 0:
                return jsonify({
                    'success': True,
                    'transcription': transcription.strip(),
                    'confidence': float(confidence)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Could not transcribe audio'
                }), 400
                
        except Exception as e:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
            
    except Exception as e:
        print(f"[VOICE] Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Transcription failed: {str(e)}'
        }), 500


@app.route('/api/solve', methods=['POST'])
def solve_voice_question():
    """
    Solve a question from voice mode.
    Input: JSON { 'problem': str, 'source': 'voice' }
    Output: JSON { 'solution': str }
    """
    data = request.get_json()
    if not data or 'problem' not in data:
        return jsonify({'error': 'No question provided'}), 400

    question_text = data.get('problem', '').strip()
    source = data.get('source', 'voice')

    if not question_text:
        return jsonify({'error': 'Empty question'}), 400

    print(f"\n[VOICE] 🎤 Question received: {question_text}")

    # Load context (resume only if uploaded via UI)
    try:
        from config import JD_PATH
        from resume_loader import load_resume, load_job_description
        resume_text = load_resume(UPLOADED_RESUME_PATH) if UPLOADED_RESUME_PATH.exists() else ""
        jd_text = load_job_description(Path.cwd() / JD_PATH)
    except:
        resume_text = ""
        jd_text = ""

    # Generate answer
    try:
        # Check if it's a coding question
        from question_validator import is_code_request
        if is_code_request(question_text):
            answer = llm_client.get_coding_answer(question_text)
        else:
            answer = llm_client.get_interview_answer(
                question_text,
                resume_text=resume_text,
                job_description=jd_text,
                include_code=False
            )

        if answer:
            # Store for display on main UI too
            answer_storage.set_complete_answer(
                question_text=question_text,
                answer_text=answer,
                metrics={'source': source}
            )
            print(f"[VOICE] ✅ Answer generated ({len(answer)} chars)")

            return jsonify({
                'success': True,
                'solution': answer
            })
        else:
            return jsonify({'error': 'No answer generated'}), 500

    except Exception as e:
        print(f"[VOICE] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500



def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Interview Assistant Web UI')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    args = parser.parse_args()

    print("=" * 60)
    print("Interview Voice Assistant - Web UI Server")
    print("=" * 60)
    print(f"\nServer: http://{args.host}:{args.port}")
    print(f"Mobile: http://<your-ip>:{args.port}")
    print(f"Data: {answer_storage.get_answers_file_path()}")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60 + "\n")

    try:
        # Use threaded mode for better SSE performance
        from werkzeug.serving import WSGIRequestHandler
        WSGIRequestHandler.protocol_version = "HTTP/1.1"  # Enable keep-alive
        app.run(host=args.host, port=args.port, debug=False, threaded=True, use_reloader=False)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\nError: Port {args.port} in use")
            print(f"Try: python3 web/server.py --port {args.port + 1}")
        else:
            print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()
