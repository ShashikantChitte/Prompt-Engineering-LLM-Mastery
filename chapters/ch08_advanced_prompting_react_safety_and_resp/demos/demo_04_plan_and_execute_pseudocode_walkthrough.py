"""
Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI
Demo 4 - Plan-and-Execute (Pseudocode Walkthrough)

Auto-generated from the course document. Run: python demo_04_plan_and_execute_pseudocode_walkthrough.py
"""
# Note: we cover the OpenAI SDK and live API calls in Module 2 (Classes 13-20).
# This pseudocode shows the two-phase structure - runnable version arrives in Module 2.

# --- Goal ---
# GOAL = "Create a brief onboarding plan for a new 18-year-old student joining
#          our online B.Tech program. Starts in one week. Never used an LMS."
#
# === PHASE 1: Planner call ===
#
# PLANNER_SYSTEM_PROMPT =
#   "Break the goal into 3-4 concrete sub-tasks. Numbered list only.
#    Each item is one clear action. Do not execute. Only plan."
#
# -> Planner output (example):
#   1. Send a welcome email with login credentials and LMS access link.
#   2. Create a first-day checklist covering profile setup and course navigation.
#   3. Schedule a 30-minute orientation video call with a mentor.
#   4. Share a curated list of 3 beginner resources for the first week.
#
# === PHASE 2: Executor calls (one per task) ===
#
# EXECUTOR_SYSTEM_PROMPT =
#   "You are executing one task in an onboarding plan.
#    Complete the task concisely. 2-4 sentences max. Be specific and actionable."
#
# Task 1 -> "Send a welcome email with login credentials and LMS access link."
#   Execution: "Send a personalised welcome email on Day -7 (one week before start)
#               with temporary login credentials, the LMS URL, and a link to a
#               2-minute setup video. Include a reply link so the student can
#               confirm receipt and flag any access issues."
#
# Task 2 -> "Create a first-day checklist covering profile setup and course navigation."
#   Execution: "Prepare a 5-item checklist: upload profile photo, complete bio,
#               enroll in Week 1 modules, watch the orientation video, and post
#               a 2-sentence intro in the class discussion forum."
#
# ... (similar for tasks 3 and 4)
#
# KEY INSIGHT: Planner and executor are SEPARATE calls with SEPARATE system prompts.
# If the plan is wrong, fix only the planner prompt.
# If one execution step fails, retry only that step.
# This failure localisation is the primary advantage over a monolithic prompt.

# === ReAct Preview (Optional) ===

# The pseudocode below simulates a ReAct trace to make the Thought-Action-Observation loop
# concrete. Read through it after completing the Quick Check.

# Note: we cover the OpenAI SDK and live API calls in Module 2 (Classes 13-20). Full ReAct
# agents are built in Module 5 (Classes 45-60).
