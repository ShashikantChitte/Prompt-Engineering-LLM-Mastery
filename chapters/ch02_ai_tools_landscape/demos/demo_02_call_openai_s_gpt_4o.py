"""
Chapter 2: AI Tools Landscape
Demo 2 - Call OpenAI's GPT-4o

Auto-generated from the course document. Run: python demo_02_call_openai_s_gpt_4o.py
"""
# This sends one prompt to GPT-4o and prints the response. One concept: making a basic chat
# completion call.

from openai import OpenAI
client = OpenAI()  # reads OPENAI_API_KEY from environment

PROMPT = "Explain what a transformer model is in exactly three sentences. Be precise."

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": PROMPT}
    ],
    max_tokens=200
)

gpt_output = response.choices[0].message.content

print("=== GPT-4o ===")
print(gpt_output)
print()
print(f"Tokens used - input: {response.usage.prompt_tokens}, output: {response.usage.completion_tokens}")

# ---------------- Expected output ----------------
# === GPT-4o ===
# A transformer model is a type of neural network architecture designed to handle sequential data with high parallelization efficiency, primarily for tasks like natural language processing. It utilizes self-attention mechanisms to weigh the importance of different words in a sequence, allowing for the consideration of contextual relationships without regard to their positions. Transformers replace recurrent units with attention mechanisms, enabling greater scalability and improved performance over traditional models like RNNs and LSTMs.
# Tokens used - input: 21, output: 85
