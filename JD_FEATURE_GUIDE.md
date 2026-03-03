# Job Description Feature - Implementation Guide

## ✅ What's Been Added

### 1. Configuration
**File:** `config.py`
- Added `JD_PATH = "job_description.txt"`

### 2. JD Loader
**File:** `resume_loader.py`
- Added `load_job_description()` function

### 3. LLM Integration
**File:** `llm_client.py`
- Added JD awareness rule to prompt
- Updated `get_interview_answer()` to accept `job_description` parameter
- Updated `get_streaming_interview_answer()` to accept `job_description` parameter
- JD is appended to system prompt when provided

### 4. Main Application
**File:** `main.py`
- Added `job_description` global variable
- Added `load_job_description` import

### 5. Template File
**File:** `job_description.txt`
- Created template for users to paste JD

---

## 🚀 How to Use

### Step 1: Add Your Job Description
Edit `job_description.txt` and paste the actual job description:

```
Position: Senior Python Developer
Company: ABC Tech

Requirements:
- 5+ years Python experience
- Django/Flask expertise
- REST API development
- PostgreSQL/MySQL
- AWS/Docker experience

Responsibilities:
- Build scalable backend systems
- Design REST APIs
- Mentor junior developers
- Code reviews

Skills:
- Python, Django, Flask
- PostgreSQL, Redis
- Docker, Kubernetes
- CI/CD pipelines
```

### Step 2: Update main.py to Load JD
Add this function after `load_resume_context()`:

```python
def load_jd_context():
    """Load job description with error handling."""
    global job_description
    try:
        job_description = load_job_description(config.JD_PATH)
        if job_description.strip():
            print(f"✓ Job Description loaded ({len(job_description)} chars)")
        return True
    except Exception:
        return False
```

### Step 3: Call JD Loader on Startup
In `main()` function, add:

```python
def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    load_resume_context()
    load_jd_context()  # ← ADD THIS LINE
    start()
```

### Step 4: Pass JD to LLM Functions
Update the LLM calls in `handle_question()`:

**For streaming (line ~221):**
```python
for chunk in get_streaming_interview_answer(question_text, resume, job_description):
```

**For fallback (line ~233):**
```python
answer = get_interview_answer(question_text, resume, job_description, include_code=False)
```

---

## 📊 How It Works

### Before (No JD):
```
Q: Why should we hire you?
A: I have strong Python skills and backend experience.
```

### After (With JD):
```
Q: Why should we hire you?
A: I have 5+ years Python experience with Django/Flask, 
   exactly matching your requirements for REST API development 
   and AWS/Docker expertise.
```

---

## 🔧 Quick Implementation

Since the changes are spread across multiple files, here's a **simple manual fix**:

### Option 1: Manual Integration (Recommended)

1. **Edit `main.py` line ~547:**
```python
def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    load_resume_context()
    
    # Load JD
    global job_description
    try:
        job_description = load_job_description(config.JD_PATH)
        if job_description.strip():
            print(f"✓ JD loaded ({len(job_description)} chars)")
    except:
        pass
    
    start()
```

2. **Edit `main.py` line ~221 (streaming call):**
```python
for chunk in get_streaming_interview_answer(question_text, resume, job_description):
```

3. **Edit `main.py` line ~233 (fallback call):**
```python
answer = get_interview_answer(question_text, resume, job_description, include_code=False)
```

4. **Restart and test!**

---

## ✅ Testing

1. **Add JD to `job_description.txt`**
2. **Restart:** `python3 main.py voice`
3. **Ask:** "Why should we hire you?"
4. **Expected:** Answer tailored to JD requirements

---

## 📝 Summary

| Component | Status |
|-----------|--------|
| Config | ✅ Added JD_PATH |
| Loader | ✅ Added load_job_description() |
| LLM Prompt | ✅ Added JD awareness rule |
| LLM Functions | ✅ Accept job_description param |
| Template | ✅ Created job_description.txt |
| Integration | ⚠️ Needs manual update in main.py |

**Next:** Manually update the 3 lines in `main.py` as shown above, then restart!
