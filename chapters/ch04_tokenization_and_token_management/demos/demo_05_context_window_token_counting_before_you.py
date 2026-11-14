"""
Chapter 4: Tokenization and Token Management
Demo 5 - Context Window: Token Counting Before You Send

Auto-generated from the course document. Run: python demo_05_context_window_token_counting_before_you.py
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Model context windows (input + output combined)
MODEL_LIMITS = {
    "gpt-3.5-turbo":  16_385,
    "gpt-4":           8_192,
    "gpt-4-turbo":   128_000,
    "gpt-4o":        128_000,
    "gpt-4o-mini":   128_000,
}

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

def check_fits(prompt: str, model: str, max_output_tokens: int = 1000) -> None:
    prompt_tokens = count_tokens(prompt)
    limit = MODEL_LIMITS.get(model, 0)
    remaining = limit - prompt_tokens - max_output_tokens
    status = "OK" if remaining > 0 else "EXCEEDS LIMIT"
    print(f"Model: {model}")
    print(f"  Prompt tokens:      {prompt_tokens:>8,}")
    print(f"  Reserved for output:{max_output_tokens:>8,}")
    print(f"  Context limit:      {limit:>8,}")
    print(f"  Remaining budget:   {remaining:>8,}  [{status}]")
    print()

short_prompt = "Explain transformers in one paragraph."
long_prompt = "Summarize this document: " + ("This is filler text. " * 5000)

check_fits(short_prompt, "gpt-3.5-turbo")
check_fits(long_prompt, "gpt-3.5-turbo")
check_fits(long_prompt, "gpt-4-turbo")

# ---------------- Expected output ----------------
# Model: gpt-3.5-turbo
#   Prompt tokens:             7
#   Reserved for output:   1,000
#   Context limit:        16,385
#   Remaining budget:     15,378  [OK]
#
# Model: gpt-3.5-turbo
#   Prompt tokens:        25,007
#   Reserved for output:   1,000
#   Context limit:        16,385
#   Remaining budget:     -9,622  [EXCEEDS LIMIT]
#
# Model: gpt-4-turbo
#   Prompt tokens:        25,007
#   Reserved for output:   1,000
#   Context limit:       128,000
#   Remaining budget:    101,993  [OK]

# The long prompt exceeds GPT-3.5's limit but fits in GPT-4-turbo. Counting tokens before
# sending is cheap (runs locally, no API call) and prevents expensive runtime errors. Build
# this check into any code that constructs dynamic prompts.
