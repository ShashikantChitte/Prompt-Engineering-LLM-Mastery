"""
Chapter 3: What is an LLM? + Transformers and How They Work
Demo 2 - Self-Attention from Scratch

Auto-generated from the course document. Run: python demo_02_self_attention_from_scratch.py
"""
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)

# A minimal self-attention implementation.
# 4 tokens, d_model=8, single head.

n_tokens = 4
d_model = 8
d_k = 8

tokens = ["The", "cat", "sat", "mat"]

# Random input embeddings (normally learned during training)
X = np.random.randn(n_tokens, d_model)

# Random projection matrices (normally learned during training)
W_Q = np.random.randn(d_model, d_k) * 0.1
W_K = np.random.randn(d_model, d_k) * 0.1
W_V = np.random.randn(d_model, d_k) * 0.1

# Compute Q, K, V
Q = X @ W_Q  # (4, 8)
K = X @ W_K  # (4, 8)
V = X @ W_V  # (4, 8)

# Attention scores: every token against every other token
scores = Q @ K.T / np.sqrt(d_k)  # (4, 4)

# Softmax over the last dimension
def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)  # numerical stability
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

attn_weights = softmax(scores)  # (4, 4)

# Weighted sum of Values
output = attn_weights @ V  # (4, 8)

print("Input shape:", X.shape)
print("Q, K, V shapes:", Q.shape, K.shape, V.shape)
print("Attention scores (unnormalised):")
print(np.round(scores, 3))
print("\nAttention weights (after softmax, each row sums to 1.0):")
print(np.round(attn_weights, 3))
print("\nRow sums (must be 1.0):", np.round(attn_weights.sum(axis=1), 6))
print("\nOutput shape:", output.shape)

# Visualise attention weights
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(attn_weights, cmap='Blues', vmin=0, vmax=1)
ax.set_xticks(range(n_tokens))
ax.set_yticks(range(n_tokens))
ax.set_xticklabels(tokens)
ax.set_yticklabels(tokens)
ax.set_xlabel("Attended to (Keys)")
ax.set_ylabel("Query token")
ax.set_title("Attention Weights: who attends to whom")
for i in range(n_tokens):
    for j in range(n_tokens):
        ax.text(j, i, f"{attn_weights[i,j]:.2f}", ha='center', va='center',
                color='white' if attn_weights[i,j] > 0.5 else 'black', fontsize=10)
plt.colorbar(im)
plt.tight_layout()
plt.show()

# ---------------- Expected output ----------------
# Input shape: (4, 8)
# Q, K, V shapes: (4, 8) (4, 8) (4, 8)
# Attention scores (unnormalised):
# [[-0.062  0.055 -0.015  0.021]
#  [ 0.039 -0.05  -0.013  0.072]
#  [ 0.063 -0.036  0.008 -0.068]
#  [-0.035  0.031 -0.01   0.   ]]
#
# Attention weights (after softmax, each row sums to 1.0):
# [[0.235 0.264 0.246 0.255]
#  [0.257 0.235 0.244 0.265]
#  [0.268 0.243 0.254 0.235]
#  [0.242 0.259 0.248 0.251]]
#
# Row sums (must be 1.0): [1. 1. 1. 1.]
#
# Output shape: (4, 8)

# Each row is one token's query looking at all other tokens' keys. The values in each row sum
# to 1.0 - they are a probability distribution over which tokens to attend to. The output for
# each token is a weighted average of all Value vectors, where the weights come from this
# matrix. With random weights, the pattern is noisy - trained models learn weights that
# reflect real syntactic and semantic relationships.
