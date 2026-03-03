#!/usr/bin/env python3
"""Test all 24 coding questions through the system."""
import sys, os

# Load env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import get_coding_answer, get_interview_answer, clear_session
from question_validator import is_code_request

QUESTIONS = [
    # Level 1
    ("Q1 L1", "Write a program which will find all such numbers which are divisible by 7 but are not a multiple of 5, between 2000 and 3200 (both included). Print in comma-separated sequence."),
    ("Q2 L1", "Write a program which can compute the factorial of a given number."),
    ("Q3 L1", "Write a program to generate a dictionary that contains (i, i*i) for integral number between 1 and n (both included)."),
    ("Q4 L1", "Write a program which accepts a comma separated sequence of numbers and generates a list and a tuple."),
    ("Q5 L1", "Define a class which has getString method to get a string from input and printString method to print the string in upper case."),
    # Level 2
    ("Q6 L2", "Write a program that calculates Q = Square root of [(2 * C * D)/H] where C=50, H=30, D is input as comma-separated values."),
    ("Q7 L2", "Write a program which takes 2 digits X,Y as input and generates a 2-dimensional array where element in i-th row and j-th column is i*j."),
    ("Q8 L2", "Write a program that accepts a comma separated sequence of words and prints them sorted alphabetically."),
    ("Q9 L2", "Write a program that accepts lines as input and prints them in upper case."),
    ("Q10 L2", "Write a program that accepts whitespace separated words and prints them after removing duplicates and sorting alphanumerically."),
    ("Q11 L2", "Write a program which accepts comma separated 4 digit binary numbers and prints the ones divisible by 5."),
    ("Q12 L2", "Write a program to find all numbers between 1000 and 3000 where each digit is even. Print comma-separated."),
    ("Q13 L2", "Write a program that accepts a sentence and calculates the number of letters and digits."),
    ("Q14 L2", "Write a program that accepts a sentence and calculates upper case and lower case letters count."),
    ("Q15 L2", "Write a program that computes the value of a+aa+aaa+aaaa with a given digit a."),
    ("Q16 L2", "Use a list comprehension to square each odd number in a list. Input is comma-separated numbers."),
    ("Q17 L2", "Write a program that computes net bank account amount from transaction log. D means deposit, W means withdrawal."),
    # Level 3
    ("Q18 L3", "Write a program to check password validity: at least 1 lowercase, 1 uppercase, 1 digit, 1 special char from $#@, length 6-12. Accept comma-separated passwords."),
    ("Q19 L3", "Write a program to sort (name, age, height) tuples by name then age then height. Input from console."),
    ("Q20 L3", "Define a class with a generator which can iterate numbers divisible by 7 between 0 and n."),
    ("Q21 L3", "Write a program to compute distance from origin after robot movements UP/DOWN/LEFT/RIGHT with steps."),
    ("Q22 L3", "Write a program to compute word frequency from input text and output sorted by key."),
    ("Q23 L1", "Write a method which can calculate square value of a number."),
    ("Q24 L1", "Write a program to print Python built-in function documents like abs(), int(). Add docstring for your own function."),
]

def main():
    print("=" * 70)
    print("ALL 24 QUESTIONS - CODE GENERATION TEST")
    print("=" * 70)

    issues = []
    total = len(QUESTIONS)
    good = 0

    for qid, question in QUESTIONS:
        clear_session()
        print(f"\n{'=' * 70}")
        print(f"{qid}: {question[:70]}...")
        print("-" * 70)

        # Check detection
        is_code = is_code_request(question)

        if is_code:
            answer = get_coding_answer(question)
            mode = "CODE"
        else:
            answer = get_interview_answer(question)
            mode = "INTERVIEW"

        if not is_code:
            issues.append(f"{qid}: NOT detected as code (went to {mode})")

        print(f"[{mode}]")
        print(answer)

        # Quality checks
        if not answer:
            issues.append(f"{qid}: EMPTY answer")
        elif is_code:
            # Check for preamble text
            first_line = answer.split('\n')[0].strip()
            if first_line and not any(first_line.startswith(k) for k in ['def ', 'class ', 'import ', 'from ', 'l=', 'l =', 'n=', 'n =', 's=', 's =', 'a=', 'a =', 'values', 'items', 'input', 'netAmount', 'pos', 'freq', 'value', 'print', 'for ', 'while ', 'if ', 'd=', 'd =', 'd{', '#', '---', '- hosts']):
                has_preamble = any(w in first_line.lower() for w in ["here", "this", "the ", "python", "below", "following"])
                if has_preamble:
                    issues.append(f"{qid}: Has text preamble: '{first_line[:50]}'")

            # Check indentation (should have some indented lines for functions)
            lines = answer.split('\n')
            has_indent = any(l.startswith('    ') or l.startswith('\t') for l in lines)
            if len(lines) > 2 and not has_indent:
                issues.append(f"{qid}: No indentation detected")

            good += 1
        else:
            good += 1

    print(f"\n\n{'=' * 70}")
    print(f"RESULTS: {good}/{total} produced code")
    print(f"{'=' * 70}")
    if issues:
        print(f"\nISSUES ({len(issues)}):")
        for issue in issues:
            print(f"  ! {issue}")
    else:
        print("\nALL CLEAN!")

if __name__ == "__main__":
    main()
