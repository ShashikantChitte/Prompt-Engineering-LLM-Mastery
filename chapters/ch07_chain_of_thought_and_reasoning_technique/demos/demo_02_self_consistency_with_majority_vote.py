"""
Chapter 7: Chain-of-Thought and Reasoning Techniques
Demo 2 - Self-Consistency with Majority Vote

Auto-generated from the course document. Run: python demo_02_self_consistency_with_majority_vote.py
"""
# Note: We cover the OpenAI SDK and Python properly in Class 13. The reasoning paths below are
# static examples illustrating how self-consistency works.

# === Prompt: ===

# A train travels from city A to city B at 60 km/h.

# The return journey is at 90 km/h.

# What is the average speed for the entire round trip?

# Think step by step.

# === 5 sampled reasoning paths: ===

# Path 1:

# Let distance A->B = d km.

# Time A->B = d/60. Time B->A = d/90.

# Total distance = 2d. Total time = d/60 + d/90 = 3d/180 + 2d/180 = 5d/180.

# Average speed = 2d / (5d/180) = 72 km/h.

# Final answer: 72

# Path 2:

# Average speed = (60 + 90) / 2 = 75 km/h.

# Final answer: 75

# Path 3:

# Using harmonic mean for equal distances: 2 x 60 x 90 / (60 + 90) = 10800/150 = 72 km/h.

# Final answer: 72

# Path 4:

# Take d = 180 km. Time out = 3h. Time back = 2h.

# Total distance = 360 km. Total time = 5h. Average speed = 72 km/h.

# Final answer: 72

# Path 5:

# Average of 60 and 90 is 75.

# Final answer: 75

# Vote distribution: {72: 3, 75: 2}

# Self-consistency answer: 72 (appeared 3/5 times)

# *(Correct answer: 72 km/h - harmonic mean, not arithmetic mean. Paths 2 and 5 fall into the
# common trap of averaging the two speeds directly.)*

# This is a classic trap problem - students often average 60 and 90 to get 75, which is wrong.
# The correct answer is 72 km/h (harmonic mean of speeds). Watch whether the majority vote
# converges on 72 or 75. If some paths show 75 and others show 72, the correct paths outnumber
# the wrong ones - which is exactly what self-consistency relies on. Real improvement shows up
# most on problems where one-step shortcuts produce plausible but wrong results.
