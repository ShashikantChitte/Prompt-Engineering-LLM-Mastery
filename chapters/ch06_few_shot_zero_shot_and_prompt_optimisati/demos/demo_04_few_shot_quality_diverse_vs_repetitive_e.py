"""
Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)
Demo 4 - Few-Shot Quality: Diverse vs Repetitive Examples

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_04_few_shot_quality_diverse_vs_repetitive_e.py
"""
# Same number of examples (3), same task. One set uses diverse examples, one uses repetitive
# examples from the same sub-type.

# Task: extract the action item from a meeting note

query_note = "Priya mentioned that the onboarding flow needs a loading state before the dashboard renders."

# Repetitive examples: all about UI bugs
repetitive_examples = """
Note: "The button color is wrong on the settings page."
Action item: Fix button color on settings page.

Note: "The modal closes too slowly on mobile."
Action item: Improve modal close animation speed on mobile.

Note: "The font size is too small in the footer."
Action item: Increase footer font size.
"""

# Diverse examples: different domains, different types of action items
diverse_examples = """
Note: "We need to migrate the old user data before the next release."
Action item: Complete user data migration before next release.

Note: "The API response time is above 2 seconds for the search endpoint."
Action item: Optimize search endpoint to reduce response time below 2 seconds.

Note: "Sales wants a weekly report on new signups sent every Monday."
Action item: Set up automated weekly signup report for Sales, delivered Mondays.
"""

for set_name, examples in [("Repetitive (all UI bugs)", repetitive_examples), ("Diverse (varied domains)", diverse_examples)]:
    prompt = f"{examples}\nNote: \"{query_note}\"\nAction item:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    result = response.choices[0].message.content.strip()
    print(f"--- {set_name} ---")
    print(result)
    print()

# ---------------- Expected output ----------------
# --- Repetitive (all UI bugs) ---
# Add a loading state to the onboarding flow before the dashboard renders.
#
# --- Diverse (varied domains) ---
# Add a loading state to the onboarding flow before the dashboard renders.
