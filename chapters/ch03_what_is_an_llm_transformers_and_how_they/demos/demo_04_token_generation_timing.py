"""
Chapter 3: What is an LLM? + Transformers and How They Work
Demo 4 - Token Generation Timing

Auto-generated from the course document. Run: python demo_04_token_generation_timing.py
"""
# We will run this demo live in Class 14 once you have your API key set up. The simulated
# output below shows typical gpt-4o-mini numbers. The pedagogical point is the same: TTFT
# (time to first token) scales with prompt length because it is dominated by the prefill
# phase, while decode speed stays roughly constant because KV cache eliminates per-step
# recomputation.

# Simulated output - typical gpt-4o-mini numbers.
# We will run the live version in Class 14 after setting up the OpenAI SDK and API key.

print("Simulated results (typical gpt-4o-mini numbers):")
print()
print("  Short prompt (~10 tokens):")
print("    TTFT: ~0.3s | Total: ~1.1s | Decode: ~60 tok/s")
print()
print("  Long prompt (~1400 tokens):")
print("    TTFT: ~1.8s | Total: ~2.7s | Decode: ~58 tok/s")
print()
print("  TTFT ratio: ~6x - prefill cost is proportional to prompt length.")
print("  Decode speed: nearly identical - KV cache makes per-step cost independent of prompt length.")

# ---------------- Expected output ----------------
# Simulated results (typical gpt-4o-mini numbers):
#
#   Short prompt (~10 tokens):
#     TTFT: ~0.3s | Total: ~1.1s | Decode: ~60 tok/s
#
#   Long prompt (~1400 tokens):
#     TTFT: ~1.8s | Total: ~2.7s | Decode: ~58 tok/s
#   TTFT ratio: ~6x - prefill cost is proportional to prompt length.
#   Decode speed: nearly identical - KV cache makes per-step cost independent of prompt length.

# Time to first token (TTFT) scales with prompt length - that is the prefill phase. Once
# generation begins, the per-token speed stays roughly constant regardless of prompt length -
# that is the KV cache eliminating recomputation. This is why long-context APIs report latency
# separately as TTFT and throughput (tokens/second).
