"""
Chapter 7: Chain-of-Thought and Reasoning Techniques
Demo 0 - Setup

Auto-generated from the course document. Run: python demo_00_setup.py
"""
# # NOTE: We cover the OpenAI SDK, API keys, and Python environments properly in Class 13.

# # This cell is provided as a reference only - do not run it during Class 7.

# # The demos in this notebook are shown as static markdown examples instead.

# Demo setup - install dependencies
# !pip install openai anthropic --quiet

import os
from openai import OpenAI

os.environ['OPENAI_API_KEY'] = 'your-key-here'
client = OpenAI()

def ask(prompt, model='gpt-4o-mini', temperature=0):
     response = client.chat.completions.create(
         model=model,
         messages=[{'role': 'user', 'content': prompt}],
         temperature=temperature
     )
     return response.choices[0].message.content

# ---------------- Expected output ----------------
# no output
