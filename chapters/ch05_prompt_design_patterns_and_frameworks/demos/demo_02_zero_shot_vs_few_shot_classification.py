"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 2 - Zero-Shot vs Few-Shot Classification

Auto-generated from the course document. Run: python demo_02_zero_shot_vs_few_shot_classification.py
"""
import openai
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

tickets = [
    "My app keeps crashing whenever I open settings.",
    "How do I add a second user to my account?",
    "I was charged twice last month.",
    "The export button does nothing when I click it."
]

zero_shot_template = "Classify this support ticket into a category: \"{ticket}\""

few_shot_template = """Classify support tickets. Respond with ONLY the category label.

Input: "My password reset email never arrived."
Category: ACCOUNT_ACCESS

Input: "How do I connect my calendar?"
Category: HOW_TO

Input: "The dashboard takes 30 seconds to load."
Category: PERFORMANCE

Input: "{ticket}"
Category:"""

print("ZERO-SHOT vs FEW-SHOT - Support Ticket Classification")
print("="*60)

for ticket in tickets:
    zs_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": zero_shot_template.format(ticket=ticket)}],
        max_tokens=20
    )
    fs_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": few_shot_template.format(ticket=ticket)}],
        max_tokens=10
    )
    print(f"\nTicket: {ticket}")
    print(f"  Zero-shot: {zs_resp.choices[0].message.content.strip()}")
    print(f"  Few-shot:  {fs_resp.choices[0].message.content.strip()}")

# ---------------- Expected output ----------------
# ZERO-SHOT vs FEW-SHOT - Support Ticket Classification
# ============================================================
#
# Ticket: My app keeps crashing whenever I open settings.
#   Zero-shot: Bug Report
#   Few-shot:  BUG
#
# Ticket: How do I add a second user to my account?
#   Zero-shot: Account Management
#   Few-shot:  HOW_TO
#
# Ticket: I was charged twice last month.
#   Zero-shot: Billing Issue
#   Few-shot:  BILLING
#
# Ticket: The export button does nothing when I click it.
#   Zero-shot: Bug Report
#   Few-shot:  BUG
