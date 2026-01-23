def is_coding_question(text):
    keys = ["write", "code", "function", "program"]
    t = text.lower()
    return any(k in t for k in keys)
