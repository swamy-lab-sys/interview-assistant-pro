# URL / Platform-Based Coding Mode

I have implemented the **URL-Based Text Interview Mode** as requested.

## 🚀 How to Use

1.  **Open any Coding Platform** (LeetCode, HackerRank, Codility, etc.).
2.  **Ensure Extension is Active**: Open your browser's extension manager and **Refresh** the "Programiz Code Typer" (or whatever name matches the ID) to load the new permissions.
3.  **Start Coding**:
    - Click inside the code editor.
    - Type **`##start`**.
4.  **Watch Magic**:
    - The `##start` trigger will vanish.
    - The assistant will read the problem description from the current page.
    - The assistant will generate a Python solution using the exact function signature provided.
    - The code will be "typed" out naturally into the editor.

## 🛑 Controls

- **`##stop`**: Immediately aborts the generation/typing.
- **Page/Tab Switch**: Also aborts the process (safety kill-switch).

## ⚠️ Important

- **Restart Server**: You **MUST** restart the python server for the new API to work.
  ```bash
  python3 main.py voice
  ```
- **Permission**: The extension now asks for `<all_urls>` permission. You might need to re-enable it if Chrome disables it due to permission changes.
