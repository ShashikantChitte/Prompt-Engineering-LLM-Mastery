"""
Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI
Demo 2 - Prompt Chaining: 3-Step Pipeline (Conceptual Walkthrough)

Auto-generated from the course document. Run: python demo_02_prompt_chaining_3_step_pipeline_conceptu.py
"""
# Module 1 covers the CONCEPT. Live implementation is in Class 9 (Module 2).
# Note: we cover the OpenAI SDK and live API calls in Module 2 (Classes 13-20).
# This is a preview of what the code looks like - full runnable version is in Class 9.

# --- What a 3-step chaining pipeline does ---
#
# Input: RAW_IDEA = "Students forget to submit assignments. We want smart notifications."
#
# STEP 1 - Extract core problem
#   system_prompt = "Extract the single core user problem. Two sentences only."
#   user_content  = "Raw idea: <RAW_IDEA>"
#   -> output: "Students miss submission deadlines because they lack timely,
#               context-aware reminders. They need a notification system that
#               respects their working patterns."
#
# STEP 2 - Generate acceptance criteria (receives ONLY Step 1 output, not raw idea)
#   system_prompt = "Write 3-4 testable acceptance criteria from this problem."
#   user_content  = "Problem: <Step 1 output>"
#   -> output:
#     1. Notifications arrive within 24h of a missed submission window.
#     2. Students can set a preferred notification time.
#     3. No more than 2 notifications per assignment.
#     4. Students can opt out of notifications per course.
#
# STEP 3 - Format into a mini spec (receives Step 1 + Step 2 output, not raw idea)
#   system_prompt = "Format into: Feature Name, Problem, Success Criteria."
#   user_content  = "Problem: <Step 1> Criteria: <Step 2>"
#   -> output:
#     Feature Name: Smart Assignment Reminders
#     Problem: Students miss deadlines due to poorly timed generic notifications.
#     Success Criteria:
#       - Notifications are sent within 24h of deadline
#       - Students control notification timing
#       - Max 2 reminders per assignment
#       - Per-course opt-out available
#
# KEY INSIGHT: Step 3 never sees the raw idea. Each step does one thing.
# If Step 2 produces bad criteria, you fix only the Step 2 prompt.
# This is why chaining is easier to debug than one large prompt.
#
# Full runnable version with live API calls -> Class 9.

# Notice that Step 3 never sees the raw idea. It only sees the structured output of Steps 1
# and 2. Each step does one thing well. If Step 2 produces bad criteria, you fix the Step 2
# prompt without touching the others. This is why chaining is easier to debug than one large
# prompt.
