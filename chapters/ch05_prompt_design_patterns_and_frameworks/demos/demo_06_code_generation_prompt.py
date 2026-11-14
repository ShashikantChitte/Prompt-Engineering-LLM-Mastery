"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 6 - Code Generation Prompt

Auto-generated from the course document. Run: python demo_06_code_generation_prompt.py
"""
# --- prompt / data used below (not Python) ---
# # A well-structured prompt that produces a usable, tested function
#
# import openai
# import os
# client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
#
# code_gen_prompt = """Language: Python 3.11
# Task: Write a function called `parse_email_parts` that extracts the username and domain from an email address.
#
# Function signature:
#     def parse_email_parts(email: str) -> dict:
#
# Input/output contract:
#     Input: a string that may or may not be a valid email
#     Output: {"username": str, "domain": str} if valid, raise ValueError if not
#
# Edge cases to handle:
#     - Missing @ symbol -> ValueError
#     - Multiple @ symbols -> ValueError
#     - Empty string -> ValueError
#     - Valid: "user@example.com" -> {"username": "user", "domain": "example.com"}
#
# Constraints:
#     - Do not use regex
#     - No third-party libraries
#     - Include a docstring
#     - Include 3 example calls in a comment at the bottom"""
#
# response = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[{"role": "user", "content": code_gen_prompt }],
#     max_tokens=400
# )
#
#
# print(response.choices[0].message.content)

# ---------------- Expected output ----------------
# def parse_email_parts(email: str) -> dict:
#     """
#     Extract the username and domain from an email address.
#
#     Args:
#         email: A string that may or may not be a valid email address.
#
#     Returns:
#         A dict with keys "username" and "domain".
#
#     Raises:
#         ValueError: If the email is empty, missing "@", or contains
#                     more than one "@".
#     """
#     if not email:
#         raise ValueError("Email must not be empty")
#
#     if email.count("@") == 0:
#         raise ValueError("Email must contain an '@' symbol")
#
#     if email.count("@") > 1:
#         raise ValueError("Email must contain exactly one '@' symbol")
#
#     username, domain = email.split("@")
#
#     if not username or not domain:
#         raise ValueError("Email must have a non-empty username and domain")
#
#     return {"username": username, "domain": domain}
#
#
# # Example calls:
# # >>> parse_email_parts("user@example.com")
# # {'username': 'user', 'domain': 'example.com'}
# # >>> parse_email_parts("no-at-sign.com")
# # ValueError: Email must contain an '@' symbol
# # >>> parse_email_parts("")
# # ValueError: Email must not be empty
