"""
Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem
Demo 4 - API comparison: same prompt, three providers, side by side

Auto-generated from the course document. Run: python demo_04_api_comparison_same_prompt_three_provide.py
"""
import openai
import anthropic
import google.generativeai as genai
import time

# Initialize clients
oai_client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")
anthropic_client = anthropic.Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")
genai.configure(api_key="YOUR_GEMINI_API_KEY")

PROMPT = "Name three practical use cases for function calling in LLM applications. One sentence each."
SYSTEM = "You are a concise technical writer. Answer directly without preamble."

results = {}

# --- OpenAI ---
start = time.time()
oai_resp = oai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": PROMPT}
    ],
    max_tokens=200
)
results["openai"] = {
    "text": oai_resp.choices[0].message.content,
    "latency": round(time.time() - start, 2),
    "input_tokens": oai_resp.usage.prompt_tokens,
    "output_tokens": oai_resp.usage.completion_tokens
}

# --- Anthropic ---
start = time.time()
ant_resp = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=SYSTEM,
    messages=[{"role": "user", "content": PROMPT}],
    max_tokens=200
)
results["anthropic"] = {
    "text": ant_resp.content[0].text,
    "latency": round(time.time() - start, 2),
    "input_tokens": ant_resp.usage.input_tokens,
    "output_tokens": ant_resp.usage.output_tokens
}

# --- Gemini ---
start = time.time()
gem_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM
)
gem_resp = gem_model.generate_content(PROMPT)
results["gemini"] = {
    "text": gem_resp.text,
    "latency": round(time.time() - start, 2),
    "input_tokens": gem_resp.usage_metadata.prompt_token_count,
    "output_tokens": gem_resp.usage_metadata.candidates_token_count
}

# Print comparison
for provider, data in results.items():
    print(f"\n=== {provider.upper()} ===")
    print(f"Latency: {data['latency']}s | In: {data['input_tokens']} tok | Out: {data['output_tokens']} tok")
    print(data["text"])

# ---------------- Expected output ----------------
# === OPENAI ===
# Latency: 1.84s | In: 31 tok | Out: 78 tok
# 1. Extracting structured data from unstructured text: the model calls a parser tool to turn emails into CRM records.
# 2. Orchestrating multi-step workflows: the model chains a search tool and a calendar tool to book meetings from natural language.
# 3. Enforcing business logic at runtime: the model calls a pricing or inventory tool rather than guessing values.
#
# === ANTHROPIC ===
# Latency: 2.11s | In: 31 tok | Out: 81 tok
# 1. Retrieving live data: the model calls a weather or stock API instead of relying on stale training knowledge.
# 2. Taking actions with side effects: the model triggers a refund, email, or ticket update through a validated tool.
# 3. Composing multi-tool pipelines: the model routes a request through search, then calculation, then a database write.
#
# === GEMINI ===
# Latency: 0.97s | In: 29 tok | Out: 74 tok
# 1. Fetching real-time information: querying weather, prices, or inventory from an external API.
# 2. Automating actions: issuing refunds, sending emails, or updating records via validated tools.
# 3. Building agentic pipelines: chaining tools to complete multi-step tasks like research and booking.

# Look at three things: (1) the latency differences - these vary by load and region, so run
# this several times for a realistic comparison; (2) the token counts for the same prompt -
# tokenizers differ across providers so identical text produces different counts; (3) the
# response extraction path - choices[0].message.content for OpenAI, content[0].text for
# Anthropic, .text for Gemini. These are the structural differences you hit when switching
# providers.
