"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 1 - The 4-Part Prompt: Before vs After

Auto-generated from the course document. Run: python demo_01_the_4_part_prompt_before_vs_after.py
"""
# Install if needed: pip install openai

import openai
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def call_model(prompt, label):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    print(f"\n{'='*60}")
    print(f"PROMPT: {label}")
    print(f"{'='*60}")
    print(response.choices[0].message.content)

# BEFORE: vague, unstructured
vague_prompt = "Help me write a job description."

# AFTER: 4-part structure
structured_prompt = """Role: You are a technical recruiter at a mid-size SaaS company.
Task: Write a job description for a Senior Backend Engineer role.
Context: The role is on the payments team, requires 5+ years with Python and distributed systems, reports to VP of Engineering. Series B company, 200 people, remote-first.
Format: Sections: About the Role, What You Will Do (4 bullets), What We Are Looking For (4 bullets). Under 250 words. Plain text, no markdown."""

call_model(vague_prompt, "BEFORE - No Structure")
call_model(structured_prompt, "AFTER - 4-Part Structure")

# ---------------- Expected output ----------------
# ============================================================
# PROMPT: BEFORE - No Structure
# ============================================================
# Here are some tips for writing a great job description:
#
# 1. **Start with a clear title** — be specific about the role and level.
# 2. **Write a compelling company summary** — what do you do and why does it matter?
# 3. **List key responsibilities** — focus on outcomes, not just tasks.
# 4. **Specify required qualifications** — separate must-haves from nice-to-haves.
# 5. **Include salary range and benefits** — transparency attracts better candidates.
#
# Would you like me to draft one? If so, please tell me:
# - The job title and seniority level
# - The company and team
# - Required skills and experience
# - Location / remote policy
# - Any tone or style preferences
