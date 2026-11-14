"""
Chapter 3: What is an LLM? + Transformers and How They Work
Demo 3 - KV Cache Speedup Simulation

Auto-generated from the course document. Run: python demo_03_kv_cache_speedup_simulation.py
"""
import time
import numpy as np
import matplotlib.pyplot as plt

# Simulate the compute cost of generating tokens WITH and WITHOUT KV cache.
# We measure simulated FLOPs as a proxy for time, since actual GPU timing
# requires hardware. The ratio shows why KV cache is essential.

def simulate_no_kv_cache(prompt_len, n_generate):
    """Without KV cache: at step i, recompute attention over all i tokens."""
    total_ops = 0
    for step in range(n_generate):
        context_len = prompt_len + step
        # Attention cost scales as O(n^2)
        total_ops += context_len ** 2
    return total_ops

def simulate_with_kv_cache(prompt_len, n_generate):
    """With KV cache: prefill is O(n^2), then each step is O(n) - just the new token vs all cached."""
    # Prefill: full attention over prompt
    prefill_ops = prompt_len ** 2
    # Decode: each step, new token attends to all cached KVs
    decode_ops = sum(prompt_len + step for step in range(n_generate))
    return prefill_ops + decode_ops

prompt_lengths = [128, 256, 512, 1024, 2048, 4096]
n_generate = 200

results = []
for pl in prompt_lengths:
    ops_no_cache  = simulate_no_kv_cache(pl, n_generate)
    ops_kv_cache  = simulate_with_kv_cache(pl, n_generate)
    speedup       = ops_no_cache / ops_kv_cache
    results.append((pl, ops_no_cache, ops_kv_cache, speedup))

print(f"{'Prompt':>8} {'No Cache (ops)':>18} {'KV Cache (ops)':>18} {'Speedup':>10}")
print("-" * 60)
for pl, nc, kvc, sp in results:
    print(f"{pl:>8,} {nc:>18,.0f} {kvc:>18,.0f} {sp:>10.1f}x")

fig, ax = plt.subplots(figsize=(9, 5))
pls       = [r[0] for r in results]
no_cache  = [r[1] / 1e9 for r in results]
kv_cache  = [r[2] / 1e9 for r in results]
speedups  = [r[3] for r in results]

ax.bar([p - 80 for p in pls], no_cache,  width=120, label='No KV Cache', color='tomato',   alpha=0.8)
ax.bar([p + 80 for p in pls], kv_cache,  width=120, label='With KV Cache', color='seagreen', alpha=0.8)
for pl, sp in zip(pls, speedups):
    ax.text(pl, max(no_cache) * 0.05, f'{sp:.0f}x', ha='center', fontsize=9, color='black', fontweight='bold')
ax.set_xlabel("Prompt Length (tokens)")
ax.set_ylabel("Total Simulated Ops (billions), generating 200 tokens")
ax.set_title("KV Cache: Total Compute for Generating 200 Tokens")
ax.legend()
ax.set_xticks(prompt_lengths)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

# ---------------- Expected output ----------------
#   Prompt     No Cache (ops)     KV Cache (ops)    Speedup
# ------------------------------------------------------------
#      128         11,017,900             61,884      178.0x
#      256         25,942,700            136,636      189.9x
#      512         75,453,100            384,444      196.3x
#    1,024        253,117,100          1,273,276      198.8x
#    2,048        923,017,900          4,623,804      199.6x
#    4,096      3,521,110,700         17,616,316      199.9x

# The speedup grows with prompt length because without KV cache, each new generation step re-
# computes attention over an ever-longer context. With KV cache, each decode step only touches
# the new token's query against the already-stored keys and values. At a 4096-token prompt
# generating 200 tokens, KV cache requires roughly 20x fewer operations.
