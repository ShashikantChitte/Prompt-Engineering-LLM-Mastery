"""
Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem
Demo 2 - Streaming API call: OpenAI with visible chunk delivery

Auto-generated from the course document. Run: python demo_02_streaming_api_call_openai_with_visible_c.py
"""
import openai
import time

client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")

print("Streaming response (watch text arrive in chunks):")
print("-" * 50)

start = time.time()
full_response = ""

# stream=True returns an iterator instead of a complete response
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a concise technical writer."},
        {"role": "user", "content": "Explain what a context window is in exactly 4 sentences."}
    ],
    stream=True,
    max_tokens=200
)

for chunk in stream:
    # Each chunk has a 'choices' list; the delta contains only new tokens
    delta = chunk.choices[0].delta
    if delta.content is not None:
        print(delta.content, end="", flush=True)  # flush=True makes it print immediately
        full_response += delta.content

end = time.time()
print(f"\n" + "-" * 50)
print(f"Time to complete: {end - start:.2f}s")
print(f"Total characters received: {len(full_response)}")
print(f"finish_reason: {chunk.choices[0].finish_reason}")

# ---------------- Expected output ----------------
# Streaming response (watch text arrive in chunks):
# --------------------------------------------------
# A context window is the maximum amount of text, measured in tokens, that a language model can process in a single request. It spans everything the model sees at once: the system prompt, the conversation history, and the user's current message. Because attention scales with sequence length, the window bounds both how much context the model can reason over and the cost and latency of each call. Content beyond the window is either truncated or must be summarized, retrieved, or passed via external memory.
#
# --------------------------------------------------
# Time to complete: 2.31s
# Total characters received: 502
# finish_reason: stop

# Each chunk.choices[0].delta.content contains only the newly generated tokens - not the full
# text so far. The flush=True in print forces immediate display. The final chunk has
# finish_reason set to "stop" (normal completion) or "length" (hit max_tokens). This is how
# every streaming chat interface works under the hood.
