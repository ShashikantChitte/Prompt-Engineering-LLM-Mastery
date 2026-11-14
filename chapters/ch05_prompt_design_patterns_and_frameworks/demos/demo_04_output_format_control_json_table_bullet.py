"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 4 - Output Format Control: JSON, Table, Bullet List

Auto-generated from the course document. Run: python demo_04_output_format_control_json_table_bullet.py
"""
import openai
import json
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

raw_info = """Priya Sharma, Senior Engineer, 6 years experience, Python and Go,
previously at Flipkart and Razorpay, looking for staff-level roles, open to remote."""

# Format 1: JSON
json_prompt = f"""Extract candidate information from the text below and return ONLY a raw JSON object.
No markdown, no code blocks, just the JSON.

Required schema:
{{
  "name": "full name as string",
  "title": "current title as string",
  "years_experience": "number",
  "skills": ["list of strings"],
  "previous_companies": ["list of strings"],
  "target_level": "string",
  "remote_preference": "string"
}}

Text: {raw_info}"""

# Format 2: Markdown Table
table_prompt = f"""Extract candidate information from the text below.
Respond with ONLY a markdown table. Columns: Field | Value.
No preamble, no explanation.

Text: {raw_info}"""

# Format 3: Bullet Summary
bullet_prompt = f"""Summarise this candidate in exactly 4 bullet points.
Each bullet: max 12 words. Start each bullet with a category label in bold (e.g. **Role:**).
No preamble.

Text: {raw_info}"""

for label, prompt in [("JSON", json_prompt), ("Table", table_prompt), ("Bullets", bullet_prompt)]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    output = resp.choices[0].message.content
    print(f"\n{'='*50}")
    print(f"FORMAT: {label}")
    print(f"{'='*50}")
    print(output)
    if label == "JSON":
        try:
            parsed = json.loads(output)
            print(f"\n[JSON valid - {len(parsed)} keys parsed]")
        except json.JSONDecodeError as e:
            print(f"\n[JSON parse error: {e}]")

# ---------------- Expected output ----------------
# ==================================================
# FORMAT: JSON
# ==================================================
# {"name": "Priya Sharma", "title": "Senior Engineer", "years_experience": 6, "skills": ["Python", "Go"], "previous_companies": ["Flipkart", "Razorpay"], "target_level": "Staff", "remote_preference": "Remote"}
#
# [JSON valid - 7 keys parsed]
#
# ==================================================
# FORMAT: Table
# ==================================================
# | Field | Value |
# |-------|-------|
# | Name | Priya Sharma |
# | Title | Senior Engineer |
# | Experience | 6 years |
# | Skills | Python, Go |
# | Previous Companies | Flipkart, Razorpay |
# | Target Level | Staff |
# | Remote Preference | Open to remote |
#
# ==================================================
# FORMAT: Bullets
# ==================================================
# - **Role:** Senior Engineer with 6 years of backend experience.
# - **Skills:** Proficient in Python and Go for distributed systems work.
# - **Background:** Previously worked at Flipkart and Razorpay.
# - **Goals:** Seeking staff-level roles, open to fully remote.
