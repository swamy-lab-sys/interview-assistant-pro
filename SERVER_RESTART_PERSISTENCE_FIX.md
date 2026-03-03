# Server Restart Persistence - Analysis & Fix

## Problem Statement
**Scenario**: During an interview, 4 questions have been asked and answered. The server restarts (crash, manual restart, etc.). 

**Current Behavior**: All 4 Q&A pairs are LOST - the UI shows empty state.

**Expected Behavior**: All 4 Q&A pairs should be preserved and displayed immediately after restart.

---

## Root Cause Analysis

### 1. **Startup Clears Everything** (`main.py` lines 540-545)
```python
def start(boot_start_time: float = None):
    # Fresh start - clear everything on restart
    state.force_clear_all()
    answer_cache.clear_cache()
    answer_storage.clear_all()  # ❌ THIS DELETES ALL Q&A HISTORY
    fragment_context.clear_context()
    dlog.clear_logs()
```

### 2. **Persistence Infrastructure EXISTS but is UNUSED**
`answer_storage.py` has:
- ✅ `MASTER_LOG_FILE` - Permanent storage (NEVER cleared)
- ✅ `CURRENT_ANSWER_FILE` - Session storage (JSON)
- ✅ `HISTORY_FILE` - Session storage (JSONL)
- ✅ `load_history_on_startup()` - Function to restore from disk
- ❌ **BUT**: `load_history_on_startup()` is NEVER CALLED

### 3. **Data Flow**
```
Question Asked → LLM Answer → answer_storage.set_complete_answer()
                                    ↓
                    Writes to 3 files:
                    1. CURRENT_ANSWER_FILE (JSON) - for Web UI
                    2. HISTORY_FILE (JSONL) - for session history
                    3. MASTER_LOG_FILE (JSONL) - PERMANENT (never cleared)
```

**On Restart**:
```
main.py start() → answer_storage.clear_all()
                        ↓
                  Deletes files 1 & 2
                  Keeps file 3 (MASTER_LOG)
                        ↓
                  Memory state (_all_answers) = []
                        ↓
                  Web UI shows: "Waiting for questions..."
```

---

## Solution Design

### Option 1: **Smart Restart** (Recommended)
- Keep `CURRENT_ANSWER_FILE` on restart
- Load history from disk if file exists
- Only clear if explicitly requested (new interview session)

### Option 2: **Always Restore from MASTER_LOG**
- Use `MASTER_LOG_FILE` as source of truth
- Restore last N questions on startup
- More robust but slower

### Option 3: **Session Management**
- Add session IDs
- Preserve current session across restarts
- Allow manual "New Session" button

---

## Implementation: Option 1 (Smart Restart)

### Changes Required

#### 1. **Modify `answer_storage.clear_all()`**
Add parameter to control clearing behavior:

```python
def clear_all(force_clear: bool = False):
    """Clear all stored answers.
    
    Args:
        force_clear: If True, delete files. If False, keep disk files for recovery.
    """
    global _current_answer, _all_answers, _answer_index, _dir_ensured
    
    _dir_ensured = False
    ensure_answers_dir()
    
    with _write_lock:
        _current_answer = {
            'question': '',
            'answer': '',
            'timestamp': '',
            'is_complete': False,
            'metrics': None,
        }
        _all_answers = []
        _answer_index = {}
        
        if force_clear:
            # Only delete files if explicitly requested
            try:
                with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False)
                
                if HISTORY_FILE.exists():
                    HISTORY_FILE.unlink()
            except Exception:
                pass
```

#### 2. **Modify `main.py` startup**
```python
def start(boot_start_time: float = None):
    print("\n" + "=" * 60)
    print("INTERVIEW VOICE ASSISTANT")
    print("=" * 60)
    
    # Clear state but preserve Q&A history
    state.force_clear_all()
    answer_cache.clear_cache()
    fragment_context.clear_context()
    dlog.clear_logs()
    
    # Try to restore previous session
    try:
        answer_storage.load_history_on_startup()
        restored_count = len(answer_storage._all_answers)
        if restored_count > 0:
            print(f"✓ Restored {restored_count} Q&A from previous session")
    except Exception as e:
        print(f"⚠ Could not restore history: {e}")
        # If restore fails, clear everything
        answer_storage.clear_all(force_clear=True)
    
    # ... rest of startup
```

#### 3. **Add Manual Clear Endpoint** (`web/server.py`)
```python
@app.route('/api/clear_session', methods=['POST'])
def clear_session():
    """Manually clear all Q&A (start fresh interview)."""
    answer_storage.clear_all(force_clear=True)
    print("[API] 🗑️ Session cleared manually")
    return jsonify({'status': 'cleared'})
```

---

## Testing Scenarios

### Test 1: **Normal Restart (Preserve History)**
```bash
# 1. Start server
./run.sh

# 2. Ask 4 questions via voice/chat
# Verify all 4 appear on http://localhost:8000

# 3. Restart server (Ctrl+C, then ./run.sh)

# 4. Check http://localhost:8000
# ✅ EXPECTED: All 4 Q&A still visible
# ❌ CURRENT: Empty state
```

### Test 2: **Crash Recovery**
```bash
# 1. Start server
./run.sh

# 2. Ask 2 questions

# 3. Kill server (kill -9 <pid>)

# 4. Restart
./run.sh

# 5. Check UI
# ✅ EXPECTED: 2 Q&A restored
```

### Test 3: **Manual Clear**
```bash
# 1. Server running with 4 Q&A

# 2. Call clear endpoint
curl -X POST http://localhost:8000/api/clear_session

# 3. Check UI
# ✅ EXPECTED: Empty state (fresh start)
```

### Test 4: **Multi-Process Sync**
```bash
# 1. Server running

# 2. Ask question via voice (main.py process)

# 3. Ask question via extension (server.py process)

# 4. Restart server

# 5. Check UI
# ✅ EXPECTED: Both questions visible
```

---

## Edge Cases to Handle

### 1. **Corrupted Disk File**
```python
# In load_history_on_startup()
try:
    data = json.loads(content)
except json.JSONDecodeError:
    # Corrupted file - clear and start fresh
    print("[STORAGE] Corrupted history file, starting fresh")
    clear_all(force_clear=True)
    return
```

### 2. **Partial Answer on Crash**
```python
# If server crashed while streaming an answer
# The last answer will be incomplete (is_complete=False)
# Solution: Filter out incomplete answers on load

def load_history_on_startup():
    # ... existing code ...
    _all_answers = [
        a for a in data 
        if isinstance(a, dict) 
        and a.get('question')
        and a.get('is_complete', True)  # Only load complete answers
    ]
```

### 3. **Disk Space Full**
```python
# In _write_current()
try:
    with open(CURRENT_ANSWER_FILE, 'w', encoding='utf-8') as f:
        json.dump(display_list, f, ensure_ascii=False)
except OSError as e:
    if e.errno == 28:  # No space left on device
        print("[STORAGE] ⚠️ Disk full, using in-memory only")
        # Continue with in-memory state
```

---

## Performance Considerations

### Startup Time
- **Current**: ~0.5s (no disk I/O)
- **With Restore**: ~0.6s (read + parse JSON)
- **Impact**: Negligible (50-100ms for 100 Q&A)

### Memory Usage
- **Per Q&A**: ~2KB (question + answer + metadata)
- **100 Q&A**: ~200KB
- **Impact**: Negligible

### Disk Usage
- **CURRENT_ANSWER_FILE**: ~200KB for 100 Q&A
- **MASTER_LOG_FILE**: Grows indefinitely (append-only)
- **Solution**: Add log rotation for MASTER_LOG

---

## Rollback Plan

If the fix causes issues:

1. **Revert to current behavior**:
```python
# In main.py start()
answer_storage.clear_all(force_clear=True)  # Always clear
```

2. **Disable auto-restore**:
```python
# Comment out load_history_on_startup() call
# answer_storage.load_history_on_startup()
```

3. **Manual restore via API**:
```python
@app.route('/api/restore_session', methods=['POST'])
def restore_session():
    answer_storage.load_history_on_startup()
    return jsonify({'status': 'restored'})
```

---

## Implementation Checklist

- [ ] Modify `answer_storage.clear_all()` to accept `force_clear` parameter
- [ ] Update `main.py` startup to call `load_history_on_startup()`
- [ ] Add `/api/clear_session` endpoint to `web/server.py`
- [ ] Add UI button for "Clear Session" (optional)
- [ ] Test all 4 scenarios above
- [ ] Test edge cases (corrupted file, partial answer, disk full)
- [ ] Update documentation
- [ ] Add logging for restore operations

---

## Success Criteria

✅ **After server restart**:
1. All previous Q&A pairs are visible in Web UI
2. New questions can be asked and answered
3. No duplicate questions appear
4. Performance is not degraded
5. Manual clear still works

✅ **After crash**:
1. Complete answers are restored
2. Incomplete answers are discarded
3. System continues to work normally

✅ **User Experience**:
1. Transparent recovery (user doesn't notice restart)
2. Manual clear option available if needed
3. No data loss during normal operation
