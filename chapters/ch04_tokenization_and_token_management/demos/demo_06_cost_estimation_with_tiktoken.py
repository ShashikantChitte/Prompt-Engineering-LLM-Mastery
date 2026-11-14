"""
Chapter 4: Tokenization and Token Management
Demo 6 - Cost Estimation with tiktoken

Auto-generated from the course document. Run: python demo_06_cost_estimation_with_tiktoken.py
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# Pricing per 1M tokens (as of mid-2025 - check current pricing before use)
PRICING = {
    "gpt-4o":          {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":     {"input": 0.15,  "output": 0.60},
    "gpt-4-turbo":     {"input": 10.00, "output": 30.00},
}

def estimate_cost(prompt: str, expected_output_words: int, model: str) -> None:
    input_tokens = len(enc.encode(prompt))
    # Rough estimate: 1 word ~ 1.3 tokens for output
    output_tokens = int(expected_output_words * 1.3)

    prices = PRICING[model]
    input_cost  = (input_tokens  / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]
    total = input_cost + output_cost

    print(f"Model: {model}")
    print(f"  Input tokens:   {input_tokens:>8,}   cost: ${input_cost:.6f}")
    print(f"  Output tokens:  {output_tokens:>8,}   cost: ${output_cost:.6f}")
    print(f"  Total per call: ${total:.6f}")
    print(f"  Cost per 1000 calls: ${total * 1000:.4f}")
    print()

prompt = """
You are a senior software engineer. Review the following code and identify
bugs, suggest improvements, and explain your reasoning.

" + ("x = x + 1\n" * 200) + "

Provide a detailed code review.
"""

for model in PRICING:
    estimate_cost(prompt, expected_output_words=300, model=model)

# ---------------- Expected output ----------------
# Model: gpt-4o
#   Input tokens:         48   cost: $0.000120
#   Output tokens:       390   cost: $0.003900
#   Total per call: $0.004020
#   Cost per 1000 calls: $4.0200
#
# Model: gpt-4o-mini
#   Input tokens:         48   cost: $0.000007
#   Output tokens:       390   cost: $0.000234
#   Total per call: $0.000241
#   Cost per 1000 calls: $0.2412
#
# Model: gpt-4-turbo
#   Input tokens:         48   cost: $0.000480
#   Output tokens:       390   cost: $0.011700
#   Total per call: $0.012180
#   Cost per 1000 calls: $12.1800

# The cost difference between gpt-4o and gpt-4o-mini is roughly 15-20x on the same prompt. For
# a product making 10,000 calls per day, this is the difference between 15/dayand250/day.
# Always benchmark whether the cheaper model is good enough for your use case before
# committing to the expensive one.
