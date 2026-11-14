"""
Chapter 9: System Prompt Architecture
Demo 1 - System vs No-System: Identity Without a Prompt

Auto-generated from the course document. Run: python demo_01_system_vs_no_system_identity_without_a_p.py
"""
# Note: We will run this live in Class 14 when we set up the Anthropic SDK. For now, read the
# logic - the system parameter is what separates the two calls.

import anthropic
import os
# Add your key here or set ANTHROPIC_API_KEY in Colab secrets
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "YOUR_KEY_HERE"))
# Call 1: No system prompt - raw model
response_no_system = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=150,
    messages=[
        {"role": "user", "content": "What is your name and what are you here to do?"}
    ]
)
# Call 2: With a system prompt - defined identity
response_with_system = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=150,
    system="You are Aria, a customer support agent for TechFlow SaaS. You help users troubleshoot their dashboards and billing issues only. Do not discuss topics unrelated to TechFlow.",
    messages=[
        {"role": "user", "content": "What is your name and what are you here to do?"}
    ]
)
print("--- WITHOUT SYSTEM PROMPT ---")
print(response_no_system.content[0].text)
print()
print("--- WITH SYSTEM PROMPT ---")
print(response_with_system.content[0].text)

# ---------------- Expected output ----------------
# --- WITHOUT SYSTEM PROMPT ---
# I'm Claude, an AI assistant created by Anthropic. I'm here to help you with a wide range of tasks — answering questions, brainstorming, writing, analysis, coding, and more. What can I help you with today?
#
# --- WITH SYSTEM PROMPT ---
# I'm Aria, a customer support agent for TechFlow SaaS. I'm here to help you troubleshoot your dashboard and billing issues. Is there something specific you need help with today?

# The first response is the model's default self-description - generic, general-purpose. The
# second response is scoped entirely to the role defined in the system prompt. Same model,
# same user question, completely different identity and scope. This is system prompt doing its
# job.
