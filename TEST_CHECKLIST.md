# Interview Voice Assistant - Testing Checklist

## Quick Validation

Run the validator test suite first:
```bash
python question_validator.py
```

Expected: All tests pass (PASS/FAIL summary at bottom)

---

## Platform Testing

### 1. YouTube Fast Speaker
**Test**: Play a YouTube interview video with a fast-talking interviewer

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Fast direct question | "What is Python used for in web development?" | ACCEPT - Generate answer |
| Fast narration | "We'll show you how Python handles web requests" | REJECT - Silence |
| Fast incomplete | "The difference between Flask and" | REJECT - Silence |

### 2. Google Meet Slow Speaker
**Test**: Join a mock Meet call with deliberate pauses

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Question with pauses | "What is... [2s pause]... a decorator?" | ACCEPT - Wait for 1.5s silence, then answer |
| Long question | "Can you explain how Python's garbage collector works with reference counting and cyclic detection?" | ACCEPT - Full capture before answer |
| Slow incomplete | "Explain the... [trailing off]" | REJECT - Silence |

### 3. Zoom Long Pauses
**Test**: Zoom call with interviewer who thinks between sentences

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Multi-sentence with pause | "I'll ask about decorators. [3s pause] What is a decorator in Python?" | ACCEPT - Extract question only |
| Pause in middle | "How does Python... [2s pause]... handle memory management?" | ACCEPT - Captured as single question |
| Teaching statement | "So decorators are basically wrappers. [pause] They wrap functions." | REJECT - Narration detected |

### 4. Teams Compressed Audio
**Test**: Teams call (typically more compressed audio)

| Test Case | Input | Expected Behavior |
|-----------|-------|-------------------|
| Clear question | "What is the difference between list and tuple?" | ACCEPT |
| Muffled question | [Same question with audio quality degradation] | ACCEPT if transcription passes validator |
| Background noise + question | [Question with ambient office noise] | ACCEPT if VAD filters and transcription valid |

---

## Validation Rule Testing

### MUST REJECT (Silence = Correct)

#### Narration/Teaching Content
```
"We'll show you how to swap numbers in Python"           → REJECT
"Number swap can be done like this"                      → REJECT
"Let me explain this first"                              → REJECT
"In this problem we will see how to reverse a list"     → REJECT
"Swapping is done using tuple unpacking"                → REJECT
"Python has a simple way to swap variables"             → REJECT
"The best way to do this is using enumerate"            → REJECT
"First we will define the function"                     → REJECT
"As you can see the output is correct"                  → REJECT
"There are many ways to solve this"                     → REJECT
"The answer is using a dictionary"                      → REJECT
```

#### Incomplete Sentences (Trailing Words)
```
"What is the difference between"                        → REJECT
"Explain the concept of"                                → REJECT
"How do you handle errors in"                           → REJECT
"What happens when you use"                             → REJECT
"Can you explain the"                                   → REJECT
"The difference between list and"                       → REJECT
```

#### Too Short / No Interview Verb
```
"What is Python"                                        → REJECT (only 3 words)
"Explain decorators"                                    → REJECT (only 2 words)
"Python is great"                                       → REJECT (no interview verb)
"I use Python daily"                                    → REJECT (no interview verb)
```

#### Greetings/Fillers/Audio Checks
```
"Okay"                                                  → REJECT
"Alright"                                               → REJECT
"Can you hear me?"                                      → REJECT
"Let me think"                                          → REJECT
"Hmm"                                                   → REJECT
"Great"                                                 → REJECT
"One moment"                                            → REJECT
"That sounds good"                                      → REJECT
```

### MUST ACCEPT (Generate Answer)

#### Direct Questions
```
"What is Python and why is it popular?"                 → ACCEPT
"How do you swap two numbers in Python?"                → ACCEPT
"Explain how decorators work in Python"                 → ACCEPT
"What is the difference between list and tuple?"        → ACCEPT
"Why is Python called an interpreted language?"         → ACCEPT
```

#### Coding Requests
```
"Write code to swap two numbers"                        → ACCEPT (code mode)
"Implement a function to reverse a string"              → ACCEPT (code mode)
"Write a program to find duplicates in a list"          → ACCEPT (code mode)
```

#### Questions with Fillers (Cleaned)
```
"Okay, what is Python used for?"                        → ACCEPT
"Alright, explain list comprehensions in Python"        → ACCEPT
"The first question is what is pickling?"               → ACCEPT
```

---

## UI Behavior Testing

### Single-Answer Mode
| Test | Expected |
|------|----------|
| First question | Card appears with Q&A |
| Second question | Previous card REPLACED (not stacked) |
| Third question | Still only ONE card visible |
| Refresh page | Shows only current/latest answer |

### Streaming Behavior
| Test | Expected |
|------|----------|
| During generation | Blinking cursor at end |
| After complete | No cursor, clean text |
| Code blocks | Syntax highlighted, copy button works |
| Long answer | Scrollable, no truncation |

### No Flicker
| Test | Expected |
|------|----------|
| Streaming updates | Smooth text addition, no DOM thrash |
| New question | Clean transition to new card |

---

## State Machine Testing

### Cooldown Period
| Test | Expected |
|------|----------|
| Question immediately after answer | IGNORED (3s cooldown) |
| Question after 3s+ silence | ACCEPTED |

### Generation Lock
| Test | Expected |
|------|----------|
| New audio during generation | IGNORED |
| Audio after generation complete | PROCESSED |

---

## Back-to-Back Questions

| Sequence | Expected |
|----------|----------|
| Q1 → Answer → [3s] → Q2 | Both answered, Q2 replaces Q1 in UI |
| Q1 → Answer → [1s] → Q2 | Q2 ignored (cooldown), Q1 remains |
| Q1 (incomplete) → Q2 (valid) | Q1 rejected, Q2 answered |

---

## Failure Modes (Must NOT Happen)

| Failure | Description |
|---------|-------------|
| Answer stacking | Multiple Q&A cards visible at once |
| Partial trigger | Answer starts before question complete |
| Narration response | System answers teaching content |
| Incomplete response | System answers "what is the difference between" |
| Rapid re-trigger | Same question answered twice |
| UI flicker | Visible DOM thrashing during streaming |

---

## Command Reference

```bash
# Test mode (keyboard input)
python main.py text

# Voice mode (production)
python main.py voice

# Run validator tests
python question_validator.py

# View web UI
# Open: http://localhost:8000
```

---

## Checklist Summary

Before interview:
- [ ] `python main.py voice` starts without errors
- [ ] Web UI loads at http://localhost:8000
- [ ] System audio device correctly selected (not microphone)
- [ ] Test question generates answer
- [ ] Answer replaces (not stacks)

During interview:
- [ ] Only real questions trigger answers
- [ ] Narration/teaching is ignored
- [ ] Incomplete sentences are ignored
- [ ] Pauses handled correctly (slow speakers)
- [ ] 3s cooldown between questions works

Post-interview:
- [ ] No duplicate answers in UI
- [ ] History saved in ~/.interview_assistant/answer_history.jsonl
