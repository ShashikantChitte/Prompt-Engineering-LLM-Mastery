"""
Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem
Demo 1 - Vision API: Analyse an image with GPT-4o

Auto-generated from the course document. Run: python demo_01_vision_api_analyse_an_image_with_gpt_4o.py
"""
import openai
import base64
import requests
from io import BytesIO
from PIL import Image

# Replace with your actual key
client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Fetch a sample architecture diagram (public domain)
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Transformer_architecture.png/800px-Transformer_architecture.png"

# Option A: Pass image by URL (works for public images)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "high"  # 'low' for speed/cost, 'high' for legibility
                    }
                },
                {
                    "type": "text",
                    "text": "List every labeled component in this diagram. For each component, write one sentence describing its role."
                }
            ]
        }
    ],
    max_tokens=500
)

print(response.choices[0].message.content)
print(f"\n--- Token usage ---")
print(f"Input tokens: {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")

# ---------------- Expected output ----------------
# The diagram shows the Transformer architecture with these labeled components:
#
# - Input Embedding: Converts input tokens into dense vectors.
# - Positional Encoding: Adds sequence-order information to the embeddings.
# - Encoder (stack of N layers): Processes the input sequence; each layer has:
#   - Multi-Head Attention: Lets each position attend to all positions.
#   - Feed Forward: A position-wise MLP applied independently to each token.
#   - Add & Norm: Residual connection followed by layer normalization.
# - Decoder (stack of N layers): Generates the output sequence; each layer has:
#   - Masked Multi-Head Attention: Prevents attending to future positions.
#   - Multi-Head Attention: Attends over the encoder output.
#   - Feed Forward, Add & Norm: As in the encoder.
# - Linear: Projects decoder output to vocabulary size.
# - Softmax: Produces output token probabilities.
#
# --- Token usage ---
# Input tokens: ~800-1100   (depends on image detail="high" tiling)
# Output tokens: ~150-250

# Notice the image token count in the usage output - detail: high tiles the image and charges
# per tile. Switch to detail: low and re-run to see the input token count drop significantly.
# The content array mixes an image block and a text block - this is the standard pattern for
# all multimodal calls.
