"""
Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem
Demo 5 - Prompt versioning and simple A/B test

Auto-generated from the course document. Run: python demo_05_prompt_versioning_and_simple_a_b_test.py
"""
import openai
import json
from datetime import datetime

client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")

# --- Prompt registry: treat prompts as versioned artifacts ---
PROMPT_REGISTRY = {
    "code_review": {
        "v1.0": "Review this code and tell me what is wrong.",
        "v1.1": (
            "Review the following Python code. "
            "List only issues that would cause incorrect behavior or security vulnerabilities. "
            "For each issue: cite the line number, describe the problem in one sentence, "
            "and provide a corrected code snippet. "
            "Rate severity as: critical / warning / suggestion."
        )
    }
}

# --- Test input ---
TEST_CODE = """
def get_user(db, user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result[0]
"""

# --- Run both versions and log results ---
log = []

for version, prompt_text in PROMPT_REGISTRY["code_review"].items():
    full_prompt = f"{prompt_text}\n\n```python{TEST_CODE}```"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=400,
        temperature=0  # deterministic for fair comparison
    )

    output = response.choices[0].message.content
    log.append({
        "prompt_name": "code_review",
        "prompt_version": version,
        "timestamp": datetime.now().isoformat(),
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "output": output
    })

    print(f"\n=== Version {version} ===")
    print(f"Tokens: {response.usage.prompt_tokens} in / {response.usage.completion_tokens} out")
    print(output[:600])
    print("..." if len(output) > 600 else "")

# Log is ready to write to a file or database
print("\n--- Logged entries ---")
for entry in log:
    print(f"{entry['prompt_version']}: {entry['input_tokens']} input tokens, {entry['output_tokens']} output tokens")

# ---------------- Expected output ----------------
# === Version v1.0 ===
# Tokens: 71 in / 89 out
# This code has a SQL injection vulnerability. The `user_id` is inserted directly into the query string using an f-string, which means a malicious user could pass something like `1 OR 1=1` and bypass the WHERE clause entirely.
#
# It should use a parameterized query instead:
#
# ```python
# query = "SELECT * FROM users WHERE id = ?"
# result = db.execute(query, (user_id,))

# v1.0 asks a vague question and the model decides what to surface. v1.1 specifies exactly
# what to find, how to report it, and what format to use. Look at the SQL injection
# vulnerability - v1.1 should flag it explicitly with a severity rating and a fix. The log
# list shows what a prompt evaluation trail looks like: version, token counts, and output
# stored together. In production, write this to a database keyed by (prompt_name, version,
# input_hash) so you can compare versions across many test inputs.
