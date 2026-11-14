"""
Chapter 2: AI Tools Landscape
Demo 3 - Call Anthropic's Claude with the same prompt

Auto-generated from the course document. Run: python demo_03_call_anthropic_s_claude_with_the_same_pr.py
"""
# Same prompt, different provider. The API structure differs: Anthropic separates the system
# prompt from the user message at the top level.

import anthropic

client_a = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

# SAME prompt as Demo 2
PROMPT = "Explain what a transformer model is in exactly three sentences. Be precise."

response_a = client_a.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    messages=[
        {"role": "user", "content": PROMPT}
    ]
)

claude_output = response_a.content[0].text

print("=== Claude 3.5 Sonnet ===")
print(claude_output)
print()
print(f"Tokens used - input: {response_a.usage.input_tokens}, output: {response_a.usage.output_tokens}")

# ---------------- Expected output ----------------
# === Claude 3.5 Sonnet ===
# A transformer is a neural network architecture that processes sequences of tokens in parallel using self-attention, allowing each position to weigh the relevance of every other position. Unlike recurrent models, it has no inherent recurrence or convolution, so positional information must be injected explicitly (e.g., via positional encodings). This design enables highly parallel training on large corpora and underlies most modern large language models.
#
# Tokens used - input: 20, output: 68
