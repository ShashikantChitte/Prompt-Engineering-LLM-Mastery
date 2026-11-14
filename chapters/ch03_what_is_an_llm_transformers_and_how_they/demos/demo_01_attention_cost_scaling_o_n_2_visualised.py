"""
Chapter 3: What is an LLM? + Transformers and How They Work
Demo 1 - Attention Cost Scaling (O(n^2) visualised)

Auto-generated from the course document. Run: python demo_01_attention_cost_scaling_o_n_2_visualised.py
"""
import numpy as np
import matplotlib.pyplot as plt

# Attention cost grows quadratically with sequence length.
# This demo makes that concrete with real numbers.

sequence_lengths = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072]
d_model = 128  # simplified, real models use 4096-8192

def attention_flops(n, d):
    """FLOPs for single-head attention: QK^T is (n x d)(d x n) = n^2 * d multiply-adds."""
    return 2 * n * n * d  # 2x for multiply + add

def attention_memory_bytes(n, dtype_bytes=2):
    """Bytes to store the n x n attention matrix (float16)."""
    return n * n * dtype_bytes

flops   = [attention_flops(n, d_model) for n in sequence_lengths]
memory  = [attention_memory_bytes(n) / (1024**3) for n in sequence_lengths]  # GB

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

ax1.plot(sequence_lengths, [f / 1e9 for f in flops], 'o-', color='steelblue', linewidth=2)
ax1.set_xlabel("Sequence Length (tokens)")
ax1.set_ylabel("GFLOPs")
ax1.set_title("Attention Compute Cost")
ax1.set_xscale('log', base=2)
ax1.set_yscale('log')
ax1.grid(True, alpha=0.3)
for n, f in zip(sequence_lengths, flops):
    if n in [128, 4096, 131072]:
        ax1.annotate(f'{f/1e9:.1f}G', (n, f/1e9), textcoords="offset points", xytext=(5, 5), fontsize=9)

ax2.plot(sequence_lengths, memory, 'o-', color='darkorange', linewidth=2)
ax2.axhline(y=80, color='red', linestyle='--', linewidth=1.5, label='80GB VRAM (A100)')
ax2.axhline(y=24, color='purple', linestyle='--', linewidth=1.5, label='24GB VRAM (RTX 3090)')
ax2.set_xlabel("Sequence Length (tokens)")
ax2.set_ylabel("Memory for Attention Matrix (GB)")
ax2.set_title("Attention Memory Footprint (float16)")
ax2.set_xscale('log', base=2)
ax2.set_yscale('log')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\nSequence length vs attention matrix size:")
print(f"{'Length':>10} {'Attention Matrix (GB)':>25} {'GFLOPs':>12}")
print("-" * 50)
for n, m, f in zip(sequence_lengths, memory, flops):
    print(f"{n:>10,} {m:>25.4f} {f/1e9:>12.1f}")

# ---------------- Expected output ----------------
# Sequence length vs attention matrix size:
#     Length     Attention Matrix (GB)       GFLOPs
# --------------------------------------------------
#        128                    0.0000          0.0
#        256                    0.0001          0.0
#        512                    0.0005          0.1
#      1,024                    0.0020          0.3
#      2,048                    0.0078          1.1
#      4,096                    0.0312          4.3
#      8,192                    0.1250         17.2
#     16,384                    0.5000         68.7
#     32,768                    2.0000        274.9
#     65,536                    8.0000       1099.5
#    131,072                   32.0000       4398.0

# The left chart shows compute cost doubling for every doubling of sequence length - that is
# the O(n2) curve. The right chart shows why Flash Attention exists: storing the full
# attention matrix for a 65K context requires more VRAM than most GPUs have. Flash Attention
# avoids materialising that matrix.
