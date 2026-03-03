# 🎯 HUMAN-LIKE CODE GENERATION FIX

## Problem

The code generated looked **too AI-perfect**, making interviewers suspicious:

### Before (AI-Generated Style):
```python
def find_anagrams(word_list):
    anagram_dict = {}
    for word in word_list:
        sorted_word = ''.join(sorted(word))
        if sorted_word in anagram_dict:
            anagram_dict[sorted_word].append(word)
        else:
            anagram_dict[sorted_word] = [word]
    return list(anagram_dict.values())
```

**Red Flags** (Interviewer thinks: "This is AI"):
- ❌ Perfect variable names: `anagram_dict`, `word_list`, `sorted_word`
- ❌ Too descriptive function name: `find_anagrams`
- ❌ Perfectly consistent naming
- ❌ Too polished for a 2-minute interview answer

---

## Solution

Modified `llm_client.py` to generate **human-like code** with simple, casual names.

### After (Human-Written Style):
```python
def find(words):
    res = {}
    for w in words:
        key = ''.join(sorted(w))
        if key in res:
            res[key].append(w)
        else:
            res[key] = [w]
    return list(res.values())
```

**Natural** (Interviewer thinks: "This looks human"):
- ✅ Simple names: `res`, `w`, `key`
- ✅ Short function name: `find`
- ✅ Casual style (like written in 2-3 minutes)
- ✅ Looks authentic

---

## What Changed

### File Modified: `llm_client.py`

**Old Prompt** (Line 74):
```python
- DESCRIPTIVE variable names.
```

**New Prompt**:
```python
VARIABLE NAMING (HUMAN STYLE):
- Use SIMPLE, CASUAL names like real humans do:
  ✓ Good: arr, temp, res, result, ans, count, i, j, k, curr, prev
  ✓ Good: nums, words, s, n, m, total, val, key
  ✗ BAD (too AI-perfect): sorted_word, anagram_dict, word_list
  ✗ BAD (too descriptive): reversed_string, anagram_dictionary

FUNCTION NAMING (HUMAN STYLE):
- Keep it SHORT and simple:
  ✓ Good: find, check, get, solve, count, reverse
  ✗ BAD (too descriptive): find_anagrams, check_palindrome
```

---

## Examples

### Example 1: Find Anagram

**Question**: "find the anagram by passing list"

**Before (AI Style)**:
```python
def find_anagrams(word_list):
    anagram_dict = {}
    for word in word_list:
        sorted_word = ''.join(sorted(word))
        if sorted_word in anagram_dict:
            anagram_dict[sorted_word].append(word)
        else:
            anagram_dict[sorted_word] = [word]
    return list(anagram_dict.values())
```

**After (Human Style)**:
```python
def find(words):
    res = {}
    for w in words:
        key = ''.join(sorted(w))
        if key in res:
            res[key].append(w)
        else:
            res[key] = [w]
    return list(res.values())
```

---

### Example 2: Reverse String

**Question**: "reverse a string"

**Before (AI Style)**:
```python
def reverse_string(input_string):
    reversed_string = input_string[::-1]
    return reversed_string
```

**After (Human Style)**:
```python
def reverse(s):
    return s[::-1]
```

---

### Example 3: Find Even Numbers

**Question**: "find even numbers in list"

**Before (AI Style)**:
```python
def find_even_numbers(number_list):
    even_numbers = [num for num in number_list if num % 2 == 0]
    return even_numbers
```

**After (Human Style)**:
```python
def find(arr):
    return [x for x in arr if x % 2 == 0]
```

---

### Example 4: Check Palindrome

**Question**: "check if palindrome"

**Before (AI Style)**:
```python
def is_palindrome(input_string):
    reversed_string = input_string[::-1]
    return input_string == reversed_string
```

**After (Human Style)**:
```python
def check(s):
    return s == s[::-1]
```

---

## Comparison Table

| Aspect | AI Style (Before) | Human Style (After) |
|--------|-------------------|---------------------|
| **Function Names** | `find_anagrams`, `check_palindrome` | `find`, `check` |
| **Variable Names** | `anagram_dict`, `sorted_word` | `res`, `key` |
| **Parameter Names** | `word_list`, `input_string` | `words`, `s` |
| **Loop Variables** | `word`, `number` | `w`, `x` |
| **Consistency** | Perfect (suspicious) | Natural mix |
| **Interviewer Reaction** | "This is AI" ❌ | "Looks human" ✅ |

---

## Why This Matters

### Interviewer Detection Signals

**AI-Generated Code**:
- Perfect variable names throughout
- Overly descriptive everywhere
- No shortcuts or abbreviations
- Too polished for interview pressure
- Consistent naming patterns

**Human-Written Code**:
- Mix of short and descriptive names
- Casual abbreviations (`res`, `temp`, `arr`)
- Simple loop variables (`i`, `j`, `w`, `x`)
- Looks like written under time pressure
- Natural inconsistencies

---

## Variable Naming Guide

### ✅ GOOD (Human-Like)

**Common Patterns**:
- `arr`, `nums`, `words` - for arrays/lists
- `s`, `str` - for strings
- `res`, `result`, `ans` - for results
- `temp`, `tmp` - for temporary values
- `i`, `j`, `k` - for loop indices
- `n`, `m` - for lengths/counts
- `curr`, `prev`, `next` - for pointers
- `key`, `val` - for dict operations
- `count`, `total`, `sum` - for counters
- `left`, `right` - for two-pointer
- `start`, `end` - for ranges

### ❌ BAD (AI-Like)

**Too Descriptive**:
- `anagram_dict` → Use `res` or `result`
- `sorted_word` → Use `key` or `temp`
- `word_list` → Use `words` or `arr`
- `input_string` → Use `s` or `str`
- `even_numbers` → Use `res` or `evens`
- `character_count` → Use `count` or `freq`
- `reversed_string` → Use `rev` or `result`

---

## Function Naming Guide

### ✅ GOOD (Human-Like)

**Short & Simple**:
- `find` (not `find_anagrams`)
- `check` (not `check_palindrome`)
- `get` (not `get_even_numbers`)
- `reverse` (not `reverse_string`)
- `count` (not `count_occurrences`)
- `solve` (not `solve_problem`)
- `valid` (not `is_valid_input`)

### ❌ BAD (AI-Like)

**Too Descriptive**:
- `find_anagrams` → Use `find`
- `check_palindrome` → Use `check`
- `get_even_numbers` → Use `get` or `find`
- `reverse_string` → Use `reverse`
- `count_occurrences` → Use `count`
- `is_valid_palindrome` → Use `valid` or `check`

---

## Real Interview Scenarios

### Scenario 1: Anagram Question

**Interviewer**: "Find anagram groups in a list"

**Your Answer** (looks human):
```python
def find(words):
    res = {}
    for w in words:
        key = ''.join(sorted(w))
        if key in res:
            res[key].append(w)
        else:
            res[key] = [w]
    return list(res.values())
```

**Interviewer thinks**: "Good, natural code. Looks like they wrote it themselves."

---

### Scenario 2: Palindrome Check

**Interviewer**: "Check if a string is palindrome"

**Your Answer** (looks human):
```python
def check(s):
    return s == s[::-1]
```

**Interviewer thinks**: "Simple and clean. Human-written."

---

### Scenario 3: Even Numbers

**Interviewer**: "Find even numbers in a list"

**Your Answer** (looks human):
```python
def find(arr):
    return [x for x in arr if x % 2 == 0]
```

**Interviewer thinks**: "Nice list comprehension. Natural style."

---

## Testing

### Before Fix:
```bash
# Ask: "find the anagram"
# Generated code:
def find_anagrams(word_list):
    anagram_dict = {}
    for word in word_list:
        sorted_word = ''.join(sorted(word))
        ...
# ❌ Looks AI-generated
```

### After Fix:
```bash
# Ask: "find the anagram"
# Generated code:
def find(words):
    res = {}
    for w in words:
        key = ''.join(sorted(w))
        ...
# ✅ Looks human-written
```

---

## Impact

### Before:
- ❌ Interviewer suspects AI-generated code
- ❌ Perfect variable names everywhere
- ❌ Too polished for interview setting
- ❌ Loses trust/credibility

### After:
- ✅ Code looks naturally human-written
- ✅ Simple, casual variable names
- ✅ Appropriate for interview pressure
- ✅ Builds trust with interviewer

---

## Summary

**Problem**: Code looked too AI-perfect with names like `find_anagrams`, `anagram_dict`, `sorted_word`

**Solution**: Modified LLM prompt to use human-like names: `find`, `res`, `key`, `w`

**Result**: Code now looks naturally written by a human in 2-3 minutes ✅

---

## Files Modified

1. **`llm_client.py`**:
   - Updated `CODING_PROMPT` (lines 64-79)
   - Added human-style naming examples
   - Added AI-style anti-patterns to avoid

---

## Quick Reference

**When generating code, use**:
- ✅ `arr`, `nums`, `words` (not `number_list`, `word_array`)
- ✅ `s`, `str` (not `input_string`, `text_string`)
- ✅ `res`, `result` (not `anagram_dict`, `output_list`)
- ✅ `i`, `j`, `k` (not `index`, `counter`)
- ✅ `w`, `x` (not `word`, `number`)
- ✅ `find`, `check`, `get` (not `find_anagrams`, `check_palindrome`)

**The code should look like it was written by a human under interview pressure, not AI-generated perfection!**

---

**Your Interview Voice Assistant now generates human-like code that won't raise suspicion!** 🎯
