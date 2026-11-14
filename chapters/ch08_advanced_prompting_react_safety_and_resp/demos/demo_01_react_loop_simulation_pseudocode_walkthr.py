"""
Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI
Demo 1 - ReAct Loop Simulation (Pseudocode Walkthrough)

Auto-generated from the course document. Run: python demo_01_react_loop_simulation_pseudocode_walkthr.py
"""
# Note: we cover the OpenAI SDK and live API calls in Module 2 (Classes 13-20).
# Full ReAct agents are built in Module 5 (Classes 45-60).
# This pseudocode makes the Thought-Action-Observation loop concrete without live API calls.

# --- Setup ---
# REACT_SYSTEM_PROMPT =
#   "Solve the problem using the ReAct format.
#    At each step produce exactly:
#    Thought: [reasoning about what you know and what you need next]
#    Action: [one of: Search[query] | Calculate[expression] | Finish[answer]]
#    After each Action (except Finish), I will provide an Observation.
#    Do not produce Finish until you have enough information."
#
# QUESTION = "What year did the Attention is All You Need paper come out,
#             and how many years ago was that from 2024?"
#
# === TURN 1: Model output ===
#
# Thought: I need the publication year of 'Attention Is All You Need'.
#          I don't have this memorised with certainty so I'll search.
# Action: Search["Attention Is All You Need paper publication year"]
#
# [Tool returns result]
# Observation: The paper 'Attention Is All You Need' by Vaswani et al.
#              was published in 2017.
#
# === TURN 2: Model output (Observation now in context) ===
#
# Thought: I have the publication year: 2017. The question asks how many years
#          ago that was from 2024. I can calculate this directly.
# Action: Calculate[2024 - 2017]
#
# Observation: 7
#
# === TURN 3: Model output ===
#
# Thought: I have both pieces of information. The paper came out in 2017,
#          which is 7 years before 2024.
# Action: Finish["The Attention Is All You Need paper was published in 2017,
#                 which is 7 years before 2024."]
#
# --- What to notice ---
# Turn 1 Thought: identifies what is unknown and decides to search.
# Turn 2 Thought: updates reasoning from the Observation, then calculates.
# Turn 3 Thought: confirms enough information to stop.
# The loop terminates at Finish - not at a fixed number of steps.
# Compare to CoT: a pure CoT response would guess 2017 directly. If it guessed
# wrong, every subsequent step would compound that error. ReAct grounds
# reasoning in a retrieved fact before computing the answer.
