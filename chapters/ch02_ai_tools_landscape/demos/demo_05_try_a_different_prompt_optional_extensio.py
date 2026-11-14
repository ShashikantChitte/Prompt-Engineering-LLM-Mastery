"""
Chapter 2: AI Tools Landscape
Demo 5 - Try a Different Prompt (Optional Extension)

Note: this demo reuses names defined in earlier demos of this chapter: client, client_a.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_05_try_a_different_prompt_optional_extensio.py
"""
# Change CUSTOM_PROMPT below and re-run. Try a task where you expect the models to differ - a
# creative task, a logic puzzle, or a prompt that requires following unusual constraints.

# Change this prompt and observe how both models handle it differently
CUSTOM_PROMPT = "List three practical uses of LLMs in a software company. One sentence each. No intro, no outro."

# OpenAI
custom_gpt = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": CUSTOM_PROMPT}],
    max_tokens=200
).choices[0].message.content

# Anthropic
custom_claude = client_a.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    messages=[{"role": "user", "content": CUSTOM_PROMPT}]
).content[0].text

print("GPT-4o")
print(custom_gpt)
print()
print("Claude 3.5 Sonnet")
print(custom_claude)

# ---------------- Expected output ----------------
# GPT-4o
# 1. AI pair programmers generate boilerplate code, suggest completions, and write unit tests, speeding up development.
# 2. Automated code review tools flag potential bugs and security issues before human reviewers see the pull request.
# 3. Support copilots summarize customer tickets and draft responses, reducing response time and improving consistency.
#
# Claude Sonnet 4.5
# 1. Accelerating development with AI pair-programmers that suggest code, write tests, and explain unfamiliar codebases.
# 2. Automating code review and bug triage by flagging risky diffs and summarizing issues for engineers.
# 3. Powering internal knowledge assistants that answer questions over documentation, tickets, and design docs.
