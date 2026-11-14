"""
Chapter 7: Chain-of-Thought and Reasoning Techniques
Demo 1 - Direct Answer vs Chain-of-Thought

Auto-generated from the course document. Run: python demo_01_direct_answer_vs_chain_of_thought.py
"""
# Note: We cover the OpenAI SDK properly in Class 13. The prompts and outputs below are static
# examples so you can follow the concept now.

# === The same problem, two prompt styles: ===

# Problem:

# A shop sells notebooks for 45 rupees each and pens for 12 rupees each.

# Rohan buys 3 notebooks and some pens. He pays 201 rupees in total.

# How many pens did he buy?

# === Direct prompt: Answer: ===

# Sample model output:

# 5 pens.

# CoT prompt: Solve this step by step, then give the final answer.

# Sample model output:

# Step 1: Cost of 3 notebooks = 3 x 45 = 135 rupees.

# Step 2: Remaining amount for pens = 201 - 135 = 66 rupees.

# Step 3: Number of pens = 66 / 12 = 5.5.

# Wait - 5.5 is not a whole number. Re-checking: 3 x 45 = 135. 201 - 135 = 66. 66 / 12 = 5.5.

# The CoT trace surfaces this ambiguity explicitly, whereas the direct answer just states a nu
# mber

# with no way to verify whether the model's arithmetic was correct.

# Look at the direct answer - it may be correct or wrong, but notice there is no work shown.
# In the CoT output, the model calculates notebook cost (3 x 45 = 135), subtracts from total
# (201 - 135 = 66), then divides by pen price (66 / 12 = 5.5). Each step anchors the next. If
# the direct answer is wrong, the CoT version will typically be right and will show exactly
# where the reasoning diverges.
