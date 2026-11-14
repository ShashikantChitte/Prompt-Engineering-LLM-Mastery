"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 5 - Full 4-Part Prompt: All Components Together

Auto-generated from the course document. Run: python demo_05_full_4_part_prompt_all_components_togeth.py
"""
# Task: generate a structured interview brief from a job description

import openai
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

job_description = """
We are hiring a Senior Data Engineer for our ML Platform team.
The role involves building and maintaining data pipelines,
working with Apache Spark and dbt, and collaborating with
ML engineers on feature engineering infrastructure.
Required: 5+ years experience, strong Python, SQL, and experience
with cloud data platforms (AWS or GCP).
"""

# 4-part prompt assembled
role = "You are a technical recruiter at a Series B startup preparing an interview brief for a hiring manager."

task = "Generate a structured interview brief for the following job description."

context = f"The hiring manager is technical (former engineer). They need to run a 45-minute first-round interview. The company has used Databricks and is migrating to dbt. Compensation band is $150k-$180k.\n\nJob description:\n{job_description}"

format_instruction = """Format the brief as follows (use these exact headings):
**Role Summary** - 2 sentences max
**Must-Have Skills** - 4 bullet points, be specific
**Red Flags to Watch For** - 3 bullet points
**Suggested Interview Questions** - 5 questions, each under 20 words
**Hiring Signal** - one sentence: what a strong yes looks like

Respond with markdown only. No preamble."""

# Assemble full prompt
full_prompt = f"""{role}

{task}

Context: {context}

Output format: {format_instruction}"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": full_prompt}],
    max_tokens=400
)

print("FULL 4-PART PROMPT OUTPUT")
print("="*60)
print(response.choices[0].message.content)

# ---------------- Expected output ----------------
# FULL 4-PART PROMPT OUTPUT
# ============================================================
#
# **Role Summary**
# Senior Data Engineer on the ML Platform team, responsible for data
# pipelines, Spark/dbt infrastructure, and feature engineering support
# for ML engineers.
#
# **Must-Have Skills**
# - 5+ years building production data pipelines (batch and/or streaming)
# - Strong Python for pipeline code, plus advanced SQL (window functions, query tuning)
# - Hands-on Apache Spark (PySpark preferred) — not just tutorials, real cluster work
# - Cloud data platform experience on AWS or GCP (Redshift, BigQuery, EMR, or Databricks)
#
# **Red Flags to Watch For**
# - Only dbt or only Spark experience — the role spans both, migration in progress
# - Cannot explain *why* a pipeline design was chosen, only *what* it does
# - No evidence of collaboration with ML or data science teams
#
# **Suggested Interview Questions**
# 1. Walk me through a data pipeline you built end-to-end. What broke, and how did you fix it?
# 2. How do you decide between Spark and dbt for a given transformation?
# 3. Describe a time you debugged a data quality issue in production. What was the root cause?
# 4. How have you collaborated with ML engineers on feature engineering?
# 5. You're migrating a team from Databricks to dbt — what's your first 30 days?
#
# **Hiring Signal**
# A strong yes is someone who can explain trade-offs across Spark and dbt, has
# shipped pipelines that ML teams actually depend on, and is comfortable owning
# the Databricks → dbt migration as an engineering problem, not just a tool swap.
