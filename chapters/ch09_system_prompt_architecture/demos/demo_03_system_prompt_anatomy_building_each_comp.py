"""
Chapter 9: System Prompt Architecture
Demo 3 - System Prompt Anatomy: Building Each Component

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_03_system_prompt_anatomy_building_each_comp.py
"""
# Build a system prompt component by component and test the cumulative effect
# Component 1: Instructions only
INSTRUCTIONS_ONLY = "You are a code reviewer. Review the code the user provides."
# Component 2: Instructions + Constraints
WITH_CONSTRAINTS = """
You are a code reviewer. Review the code the user provides.
Constraints:
- Focus only on Python code.
- Do not rewrite the code for the user. Point out issues only.
- Keep feedback to 5 items maximum.
"""
# Component 3: Instructions + Constraints + Output Format
WITH_FORMAT = """
You are a code reviewer. Review the code the user provides.
Constraints:
- Focus only on Python code.
- Do not rewrite the code for the user. Point out issues only.
- Keep feedback to 5 items maximum.
Output format:
Return ONLY a JSON array where each item has:
- "severity": "high", "medium", or "low"
- "line": line number (integer or null if general)
- "issue": one sentence describing the problem
- "fix": one sentence describing what to change
"""
sample_code = """
def get_user(id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    result = cursor.fetchone()
    return result
"""
print("--- INSTRUCTIONS ONLY ---")
r1 = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=200,
    system=INSTRUCTIONS_ONLY,
    messages=[{"role": "user", "content": f"Review this:\n{sample_code}"}]
)
print(r1.content[0].text[:300])
print("\n--- WITH FORMAT (JSON output) ---")
r3 = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=400,
    system=WITH_FORMAT,
    messages=[{"role": "user", "content": f"Review this:\n{sample_code}"}]
)
print(r3.content[0].text)

# ---------------- Expected output ----------------
# --- INSTRUCTIONS ONLY ---
# Here's my review of your code:
#
# 1. **SQL Injection vulnerability (line 7)**: The f-string used to build the SQL query is a serious security risk. Using `f"SELECT * FROM users WHERE id = {id}"` allows an attacker to inject arbitrary SQL. This should use a parameterized query instead.
#
# 2. **Import inside function (line 2)**: `import sqlite3` inside the function is inefficient if called repeatedly...
#
# 3. **No error handling**: The function doesn't handle cases where the connection fails or the query returns nothing.
#
# 4. **Resource leak**: The database connection is never closed...
#
# 5. **No type hints**: The function lacks type annotations...
#
# --- WITH FORMAT (JSON output) ---
# [
#   {
#     "severity": "high",
#     "line": 7,
#     "issue": "SQL injection vulnerability from interpolating id directly into the query.",
#     "fix": "Use a parameterized query with placeholders instead of an f-string."
#   },
#   {
#     "severity": "medium",
#     "line": 2,
#     "issue": "Importing sqlite3 inside the function on every call is inefficient.",
#     "fix": "Move the import to the top of the module."
#   },
#   {
#     "severity": "medium",
#     "line": null,
#     "issue": "The database connection and cursor are never closed, leaking resources.",
#     "fix": "Use a context manager or call conn.close() in a finally block."
#   },
#   {
#     "severity": "low",
#     "line": 8,
#     "issue": "fetchone() result is returned without indicating whether no row was found.",
#     "fix": "Document or handle the None return when the user does not exist."
#   },
#   {
#     "severity": "low",
#     "line": 1,
#     "issue": "Function lacks type hints for the id parameter and return value.",
#     "fix": "Add annotations, e.g. def get_user(id: int) -> tuple | None."
#   }
# ]
