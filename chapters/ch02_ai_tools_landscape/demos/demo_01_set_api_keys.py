"""
Chapter 2: AI Tools Landscape
Demo 1 - Set API keys

Auto-generated from the course document. Run: python demo_01_set_api_keys.py
"""
# Replace the empty strings with your actual keys, or set them as environment variables.
# In a shared notebook, use: import os; os.environ["OPENAI_API_KEY"] = "..."
import os
# Option A: paste keys here (never commit this to git)
os.environ["OPENAI_API_KEY"] =  ""   # paste your OpenAI key
os.environ["ANTHROPIC_API_KEY"] = ""  # paste your Anthropic key

# Option B: if running locally with keys already in your shell environment,
# the os.environ lines above are not needed - the SDKs pick them up automatically.
print("Keys loaded.") if os.environ.get("OPENAI_API_KEY") and os.environ.get("ANTHROPIC_API_KEY") else print("One or both keys are empty - fill them in above.")

# ---------------- Expected output ----------------
# Keys loaded.
