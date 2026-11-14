"""
Chapter 2: AI Tools Landscape
Demo 4 - Side-by-Side Comparison

Note: this demo reuses names defined in earlier demos of this chapter: PROMPT, claude_output, gpt_output.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_04_side_by_side_comparison.py
"""
# Print both outputs together for direct comparison. Also shows the structural difference
# between the two API response objects.

# Side-by-side output
# Requires Demo 2 and Demo 3 to have run first.

print("PROMPT")
print("-" * 60)
print(PROMPT)
print()

print("GPT-4o")
print("-" * 60)
print(gpt_output)
print()

print("Claude 3.5 Sonnet")
print("-" * 60)
print(claude_output)
print()

# API structure difference
print("API STRUCTURE NOTE")
print("-" * 60)
print("OpenAI:    response.choices[0].message.content")
print("Anthropic: response.content[0].text")
print()
print("OpenAI token field:    response.usage.prompt_tokens / completion_tokens")
print("Anthropic token field: response.usage.input_tokens / output_tokens")

# ---------------- Expected output ----------------
# PROMPT
# ------------------------------------------------------------
# Explain what a transformer model is in exactly three sentences. Be precise.
#
# GPT-4o
# ------------------------------------------------------------
# A transformer is a neural network architecture that uses self-attention to model relationships between all positions in an input sequence simultaneously. It replaces recurrence with stacked attention and feed-forward layers, with positional encodings supplying order information. This parallelism makes transformers highly efficient to train at scale and is the basis for modern large language models.
#
# Claude 3.5 Sonnet
# ------------------------------------------------------------
# A transformer is a neural network architecture that processes sequences of tokens in parallel using self-attention, allowing each position to weigh the relevance of every other position. Unlike recurrent models, it has no inherent recurrence or convolution, so positional information must be injected explicitly through positional encodings. This design enables highly parallel training on large corpora and underlies most modern large language models.
#
# API STRUCTURE NOTE
# ------------------------------------------------------------
# OpenAI:    response.choices[0].message.content
# Anthropic: response.content[0].text
#
# OpenAI token field:    response.usage.prompt_tokens / completion_tokens
# Anthropic token field: response.usage.input_tokens / output_tokens
