"""
Chapter 7: Chain-of-Thought and Reasoning Techniques
Demo 4 - Reflection and Self-Critique

Auto-generated from the course document. Run: python demo_04_reflection_and_self_critique.py
"""
# Note: We cover the OpenAI SDK properly in Class 13. The three passes below are static
# examples showing the generate-critique-revise loop.

# === Task: ===

# Write a Python function that takes a list of student scores

# and returns a summary dict with: mean, median, highest, lowest,

# and the count of students who scored above 75.

# === Pass 1 - Initial generation: ===

# def summarize_scores(scores):

# scores_sorted = sorted(scores)

# n = len(scores)

# mean = sum(scores) / n

# mid = n // 2

# median = scores_sorted[mid] if n % 2 != 0 else (scores_sorted[mid-
# 1] + scores_sorted[mid]) / 2

# return {

# 'mean': mean,

# 'median': median,

# 'highest': scores_sorted[-1],

# 'lowest': scores_sorted[0],

# 'above_75': sum(1 for s in scores if s > 75)

# }

# === Pass 2 - Self-critique: ===

# Issues found:

# 1. Edge case: if scores is empty, len(scores) = 0 and sum(scores)/0 raises ZeroDivisionError
# .

# 2. All required keys are present: mean, median, highest, lowest, above_75. No missing keys.

# Recommendation: add an empty-list guard at the top.

# === Pass 3 - Revised output: ===

def summarize_scores(scores):
    if not scores:
        return {}
    scores_sorted = sorted(scores)
    n = len(scores)
    mean = sum(scores) / n
    mid = n // 2
    median = scores_sorted[mid] if n % 2 != 0 else (scores_sorted[mid-1] + scores_sorted[mid]) / 2
    return {
        'mean': round(mean, 2),
        'median': median,
        'highest': scores_sorted[-1],
        'lowest': scores_sorted[0],
        'above_75': sum(1 for s in scores if s > 75)
    }

# Compare Pass 1 and Pass 3 carefully. The critique step often surfaces missing edge case
# handling (empty list raises ZeroDivisionError on mean calculation) and missing dictionary
# keys. The revised version typically adds if not scores: return {} guards and confirms all
# required keys are present. This is a reliable pattern for any output that has explicit
# completeness criteria - you can encode your requirements in the critique prompt and the
# model will check itself against them.

# === All Four Techniques on the Same Problem ===

# Note: We cover the OpenAI SDK properly in Class 13. The outputs below are static examples
# showing how each technique handles the same logic puzzle.

# === Puzzle: ===

# Four people - Arjun, Bhavna, Chetan, Divya - each prefer a different programming language:

# Python, JavaScript, Java, or Go.

# Clues:

# 1. Arjun does not use Python or JavaScript.

# 2. Bhavna uses a language that starts with 'J'.

# 3. Chetan and Divya do not use Go.

# 4. Bhavna does not use Java.

# === Technique 1 - Direct answer: ===

# Arjun: Go, Bhavna: JavaScript, Chetan: Python, Divya: Java.

# *(May be correct, but no work shown - no way to verify the reasoning or catch errors.)*

# === Technique 2 - Standard CoT: ===

# Clue 2: Bhavna uses a language starting with 'J' - either JavaScript or Java.

# Clue 4: Bhavna does not use Java. So Bhavna uses JavaScript.

# Clue 1: Arjun does not use Python or JavaScript. Remaining for Arjun: Java or Go.

# Clue 3: Chetan and Divya do not use Go.

# - If Arjun takes Java, then Go must go to Chetan or Divya - but clue 3 forbids that.

# - So Arjun takes Go.

# Remaining: Python and Java for Chetan and Divya. No further constraints on these two.

# Assign Chetan: Python, Divya: Java.

# Answer: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java.

# === Technique 3 - Self-consistency (3 paths): ===

# Path 1 final: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java

# Path 2 final: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java

# Path 3 final: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java

# Majority vote: unanimous.

# *(This puzzle is deterministic - all paths converge. Self-consistency adds most value on
# problems with numerical ambiguity where wrong paths produce plausible but different wrong
# answers.)*

# === Technique 4 - Reflection: ===

# Draft: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java.

# Critique - checking each clue:

# 1. Arjun does not use Python or JavaScript. Arjun=Go. Satisfied.

# 2. Bhavna uses a language starting with 'J'. Bhavna=JavaScript. Satisfied.

# 3. Chetan and Divya do not use Go. Chetan=Python, Divya=Java. Satisfied.

# 4. Bhavna does not use Java. Bhavna=JavaScript. Satisfied.

# All clues satisfied. No revision needed.

# Final: Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java.

# This is the core comparison cell. For this puzzle, standard CoT and reflection should both
# reach the correct answer (Arjun=Go, Bhavna=JavaScript, Chetan=Python, Divya=Java - or
# similar valid assignment). The direct answer may be right or wrong depending on whether the
# model has seen similar puzzles. Self-consistency across 3 paths should converge. The useful
# observation here is not which one wins on this example - it is understanding why each
# technique is structured the way it is.
