# Frontend Job Description Update ✅

I've added the requested **"Job Description" text box** to the frontend!

## ✨ New Features

1.  **"Job Description" Button**: Located in the top header.
2.  **Popup Modal**: Click the button to open a text box.
3.  **Paste & Save**: Paste your JD directly in the browser and click "Save".
4.  **Instant Update**: The AI picks up the new JD **immediately** for the next question (no restart needed!).

## 📁 Files Modified

1.  **`web/server.py`**: Added API endpoints `/api/save_jd` and `/api/get_jd`.
2.  **`main.py`**: Updated to reload JD dynamically for every question.
3.  **`web/templates/index.html`**: Added Modal UI, CSS, and JavaScript.

## 🚀 How to Use

1.  Refresh your browser at `http://localhost:8000`.
2.  Click the **"Job Description"** button in the header.
3.  Paste your job description.
4.  Click **"Save JD"**.
5.  Ask a question! The AI is now JD-aware.

**Example:**
- Paste a JD requiring "FastAPI experience".
- Ask: "What are your skills?"
- AI will emphasize FastAPI!
