def code_prompt(q):
    return (
        "STRUCTURE:\n"
        "1. DEFINITION: 1 sentence explaining the concept.\n"
        "2. CODE: Python example (Markdown ```python).\n"
        "3. KEY POINTS: 2 bullet points on when to use it.\n"
        "Mobile friendly (max 60 chars/line).\n\n"
        + q
    )
