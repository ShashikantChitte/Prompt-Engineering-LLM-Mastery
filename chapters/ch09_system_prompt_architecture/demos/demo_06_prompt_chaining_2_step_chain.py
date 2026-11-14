"""
Chapter 9: System Prompt Architecture
Demo 6 - Prompt Chaining: 2-Step Chain

Auto-generated from the course document. Run: python demo_06_prompt_chaining_2_step_chain.py
"""
# Step 1: Extract the core problem from a rough idea
# Step 2: Generate a one-paragraph feature brief from the problem statement
# Each step only sees what it needs from the previous step.
import anthropic
import os
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
RAW_IDEA = """
Students keep forgetting to submit assignments. We want some kind of notification
that knows when they usually work so we don't spam them all day.
"""
# Step 1: Extract the problem
step1_response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=100,
    system="Extract the single core user problem. Two sentences max: what users experience and what outcome they need. No solutions.",
    messages=[{"role": "user", "content": f"Idea: {RAW_IDEA}"}]
)
problem = step1_response.content[0].text
print("STEP 1 - Problem:")
print(problem)
# Step 2: Generate feature brief from the problem (does NOT see the raw idea)
step2_response = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=150,
    system="Write a one-paragraph feature brief from a problem statement. State the problem, the proposed solution, and one measurable success metric. Under 100 words.",
    messages=[{"role": "user", "content": f"Problem: {problem}"}]
)
brief = step2_response.content[0].text
print("\nSTEP 2 - Feature Brief:")
print(brief)
print("\nNote: Step 2 never saw the raw idea - only the structured output of Step 1.")

# ---------------- Expected output ----------------
# STEP 1 - Problem:
# Students frequently forget to submit assignments before deadlines, missing opportunities to earn credit. They need a reliable reminder system that reaches them at the right time without becoming intrusive or noisy.
#
# STEP 2 - Feature Brief:
# Students frequently forget to submit assignments before deadlines, losing credit they were otherwise entitled to. The proposed solution is an adaptive notification system that learns each student's typical working hours and delivers a single, well-timed reminder before the deadline rather than repeated generic alerts — reducing missed submissions without notification fatigue. Success metric: reduce missed-submission rate by 20% while keeping notification opt-outs below 5%.
#
# Note: Step 2 never saw the raw idea - only the structured output of Step 1.
