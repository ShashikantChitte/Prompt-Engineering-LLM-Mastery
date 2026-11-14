# Chapter 3 - Part 7: Mixture of Experts (MoE): how GPT-4, Mistral, and Gemini avoid paying full compute cost

> Chapter 3: What is an LLM? + Transformers and How They Work

**Mixture of Experts (MoE)** is a sparse neural network architecture that scales a model's total parameter count—and its stored knowledge—without proportionally increasing the compute required for each token. Instead of passing every token through one massive, dense feed-forward network (FFN), an MoE layer splits the network into multiple smaller sub-networks called **experts** and uses a learned **router** to activate only a tiny fraction of them per token.

## How an MoE Layer Works

In a standard Transformer, every token passes through the exact same attention layer and dense FFN layer. An MoE model replaces the dense FFN blocks with sparse MoE layers made of two main parts:

- **Expert Networks.** A collection of independent feed-forward sub-networks (ranging from 8 to 256+ experts per layer), each specializing in different patterns, domains, or syntax structures.
- **Gating Network (Router).** A lightweight linear layer followed by a softmax function that scores every expert for each incoming token. Using **Top-K routing** (commonly Top-1 or Top-2), it selects only the highest-scoring experts to process that token and combines their outputs as a weighted sum.
- **Total vs. Active Parameters.** Because most experts stay dormant for any given token, an MoE model separates model capacity from compute cost. For example, **Mixtral 8x7B** holds **46.7 billion** total parameters in memory, yet activates only **12.9 billion** parameters per token—delivering the speed of a ~13B model with the quality of a much larger model.

## Dense vs. Sparse MoE Transformers

| Dimension | Dense Transformer (e.g., Llama 3 70B) | Sparse MoE Transformer (e.g., DeepSeek-V3, Mixtral) |
| --- | --- | --- |
| Compute per Token (FLOPs) | Uses 100% of model parameters for every single token. | Uses only Top-K active parameters (typically 5% to 25% of total weights). |
| Inference Speed | Slower at large parameter counts due to heavy matrix math. | Much faster generation per token relative to total model size. |
| Training Efficiency | Reaches target quality with fewer total parameters, but requires massive compute. | Converges significantly faster than dense models for the same compute budget. |
| VRAM / Memory Footprint | Proportional to active parameters. | High—**all** expert weights must reside in fast memory (HBM), even inactive ones. |
| Batching Dynamics | Predictable memory reads per batch. | Small batches still read many distinct experts, making single-user decode memory-bound. |

## Inference Challenges & Optimizations for MoE

While MoE reduces floating-point operations (FLOPs), it creates unique bottlenecks during production serving:

- **High Memory Capacity Requirement.** Even though only 2 experts run per token, you cannot predict which experts the next token will need. All experts must stay loaded in GPU VRAM, requiring multi-GPU setups or aggressive **4-bit/FP8 quantization**.
- **Expert Parallelism (EP).** When an MoE model is too large for one GPU, **Expert Parallelism** places different experts on different GPUs. Tokens are routed across fast interconnects (like NVLink) via All-to-All communication kernels to reach their assigned experts.
- **Batch Size Sensitivity.** At batch size 1, each token activates a couple of experts, meaning the GPU loads lots of weights for very little math. At larger batch sizes (enabled by **continuous batching**), multiple tokens share the same experts, turning memory reads into high-throughput matrix multiplications.
- **Shared Experts & Fine-Grained Routing.** Modern architectures (such as **DeepSeek-V3** and **Qwen-MoE**) introduce always-on **shared experts** to capture common knowledge alongside dozens of smaller, fine-grained routed experts to prevent redundant specialization.

## Key Training Concepts

Training sparse networks stably requires preventing the router from collapsing onto just one or two favorite experts:

- **Load Balancing Loss.** An auxiliary loss term penalizes uneven routing during training, encouraging the router to distribute tokens fairly across all available experts.
- **Expert Capacity & Token Dropping.** Each expert is given a fixed buffer limit per batch; if too many tokens route to one popular expert, overflow tokens skip the FFN layer via the residual connection (though modern dropless kernels like MegaBlocks avoid dropping tokens).

## How GPT-4, Mistral, and Gemini avoid paying full compute cost

Frontier models like **GPT-4, Mistral, and Gemini** avoid paying full compute cost per token primarily by using Mixture of Experts (MoE) architectures—activating only a small fraction of their total parameters for any single token—combined with adaptive routing, compressed attention, and low-precision serving. Rather than forcing every word through a massive dense neural network, these systems decouple stored knowledge from active compute.

### 1. Sparse Mixture of Experts (MoE)

Instead of one giant dense feed-forward network (FFN) per layer, these models split their parameters across many specialized sub-networks (experts) and route each token to only the top 1 or 2 relevant experts.

| Model Family | Architectural Strategy | Total vs. Active Parameters | Compute Savings Mechanism |
| --- | --- | --- | --- |
| Mistral (Mixtral 8x7B / 8x22B, Large variants) | **Sparse MoE with Top-2 Routing.** Each layer has 8 experts, and a learned router picks 2 per token. | Mixtral 8x7B holds **46.7B** total parameters, activating only **12.9B** per token (~28%). | Cuts FLOPs per token by roughly **3.5x** while matching or beating dense 70B models. |
| GPT-4 (Architecture reports & o-series lineage) | **Multi-Expert MoE + Model Routing.** Widely reported to use a 16-expert MoE (~1.8T total parameters, ~280B active) alongside dynamic model routing. | Activates roughly **15% to 20%** of total weights per forward pass. | Combines sparse expert activation with automatic routing between fast lightweight models and heavy reasoning models. |
| Gemini (1.5 Pro, 2.0, & Flash series) | **Sparse MoE + Efficient Long-Context Attention.** Built natively on sparse MoE architectures paired with specialized fast variants (Flash). | Exact counts are proprietary, with Flash models tuned for ultra-low active parameter footprints. | Uses sparse routing plus hardware-aware TPU kernels to process million-token contexts at a fraction of dense compute. |

### 2. Dynamic Query & Reasoning Routing

Beyond routing individual tokens inside a model, modern APIs route entire user requests based on task difficulty so simple queries never touch expensive compute.

- **Lightweight vs. Heavy Model Routing.** Modern chat platforms (such as OpenAI's unified routing and Gemini's Flash/Pro tiers) use a fast classifier to send simple prompts like greetings or basic summaries to tiny, cheap models while reserving massive models for complex coding or math.
- **Adaptive Thinking Budgets.** Reasoning models dynamically adjust how many hidden "thinking tokens" they generate before answering—spending near-zero reasoning compute on factual lookups and scaling up only when multi-step verification is needed.

### 3. Shrinking the Memory & Attention Bottleneck

Because storing and reading conversation history (the KV cache) dominates serving costs on long prompts, these model families use architectural tricks to compress memory traffic:

- **Grouped-Query Attention (GQA).** Used heavily by Mistral and modern frontier architectures, GQA shares Key and Value heads across multiple Query heads, slashing KV cache memory bandwidth by **4x to 8x** with virtually no quality drop.
- **Context & Prefix Caching.** OpenAI, Google, and Mistral all cache recurring prompt prefixes (such as long system instructions, codebases, or documents) in fast memory. Subsequent turns reuse pre-computed KV states instead of reprocessing input tokens, cutting prompt compute costs by **50% to 90%**.

### 4. Hardware-Level Precision & Speculative Execution

At the serving layer, labs compress the math itself so GPUs and TPUs execute far more operations per second:

- **FP8 and INT4 Quantization.** Models are served in 8-bit floating-point (FP8) or 4-bit integer formats on NVIDIA Hopper/Blackwell GPUs and Google TPUs, roughly doubling matrix-multiplication throughput and halving memory capacity needs.
- **Speculative Decoding & Multi-Token Prediction.** A tiny draft model (or built-in prediction heads) guesses multiple upcoming tokens at once, allowing the main MoE model to verify them in a single parallel pass rather than running separate memory-bound steps for every word.
