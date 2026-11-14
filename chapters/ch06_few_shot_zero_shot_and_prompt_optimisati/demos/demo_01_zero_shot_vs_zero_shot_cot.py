"""
Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)
Demo 1 - Zero-Shot vs Zero-Shot CoT

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_01_zero_shot_vs_zero_shot_cot.py
"""
# Same question, same model, same temperature. Only difference: one asks directly, the other
# adds "think step by step."

def ask(prompt, label):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    print(f"--- {label} ---")
    print(response.choices[0].message.content)
    print()

problem = """
A farmer has 17 sheep. All but 9 die. How many sheep are left?
"""

# Zero-shot: direct question
ask(problem, "Zero-Shot (Direct)")

# Zero-shot CoT: same question, one added instruction
ask(problem + "\nThink step by step.", "Zero-Shot CoT")

# ---------------- Expected output ----------------
# --- Zero-Shot (Direct) ---
# 9 sheep are left. "All but 9 die" means all except 9 died, so 9 remain.
#
# --- Zero-Shot CoT ---
# Let me think step by step.
#
# 1. The farmer starts with 17 sheep.
# 2. "All but 9 die" means all the sheep except 9 die.
# 3. So 9 sheep survive.
# 4. 17 - 9 = 8 would be the number that died.
#
# Therefore, 9 sheep are left.
