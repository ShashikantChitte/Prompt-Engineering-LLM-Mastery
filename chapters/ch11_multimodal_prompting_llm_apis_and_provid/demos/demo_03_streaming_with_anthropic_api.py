"""
Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem
Demo 3 - Streaming with Anthropic API

Auto-generated from the course document. Run: python demo_03_streaming_with_anthropic_api.py
"""
import anthropic
import time

client = anthropic.Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")

print("Anthropic streaming (note: system is a top-level field, not a message):")
print("-" * 50)

start = time.time()
full_response = ""

# Anthropic uses a context manager for streaming
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    system="You are a concise technical writer.",  # system is separate from messages
    messages=[
        {"role": "user", "content": "Explain what a context window is in exactly 4 sentences."}
    ],
    max_tokens=200  # required in Anthropic API
) as stream:
    for text_chunk in stream.text_stream:
        print(text_chunk, end="", flush=True)
        full_response += text_chunk

end = time.time()
message = stream.get_final_message()  # full response object available after stream

print(f"\n" + "-" * 50)
print(f"Time to complete: {end - start:.2f}s")
print(f"Stop reason: {message.stop_reason}")
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")

# ---------------- Expected output ----------------
# Anthropic streaming (note: system is a top-level field, not a message):
# --------------------------------------------------
# A context window is the maximum amount of text, measured in tokens, that a model can process in a single request. It includes the system prompt, the full conversation history, and the current user message. Because attention and cost scale with sequence length, the window bounds how much context the model can reason over and how expensive each call is. Anything beyond the window must be truncated, summarized, or retrieved from external memory.
#
# --------------------------------------------------
# Time to complete: 2.14s
# Stop reason: end_turn
# Input tokens: 28
# Output tokens: 71

# Compare the Anthropic call structure to the OpenAI one in Demo 2. The system field is at the
# top level (not inside messages). max_tokens is required. Token usage is available in
# stream.get_final_message() after the stream finishes - not per-chunk. The .text_stream
# iterator yields plain strings, slightly simpler than unpacking delta objects.
