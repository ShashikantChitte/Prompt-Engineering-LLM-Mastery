# Chapter 3 - Part 6: Inference optimisations: Flash Attention, continuous batching

> Chapter 3: What is an LLM? + Transformers and How They Work

**Inference optimization** is the set of model-level and infrastructure-level techniques used to make running trained AI models in production faster, more scalable, and more cost-efficient. These methods lower latency, maximize throughput, and reduce memory consumption without requiring a full model retrain.

## How Inference Bottlenecks Work

Optimizing Large Language Models (LLMs) starts with understanding their two distinct execution phases.

- **Prefill Phase.** The model processes all input prompt tokens simultaneously to compute initial states. This step is heavily parallelized and **compute-bound**, directly impacting Time to First Token (TTFT).
- **Decode Phase.** The model generates output tokens one at a time in an autoregressive loop. Because each token depends on previous ones, this step is **memory-bound**, spending most of its time transferring data from GPU memory.

## Model-Level Optimizations

These techniques modify the model's weights, precision, or architecture to shrink its footprint and speed up math operations.

- **Quantization.** Reduces parameter precision from 32-bit or 16-bit floating-point numbers down to 8-bit or 4-bit integers. This cuts memory usage by up to 75% and accelerates calculations with minimal accuracy loss.
- **Knowledge Distillation.** Trains a smaller, faster "student" model to mimic the behavior and reasoning patterns of a much larger "teacher" model.
- **Pruning and Sparsity.** Removes redundant weights, attention heads, or layers that contribute little to the final output.
- **Architectural Attention Variants.** Replaces standard attention with Multi-Query Attention (MQA) or Grouped-Query Attention (GQA) to share Key-Value heads and shrink memory bandwidth requirements.

## Memory and Attention Optimizations

Because long contexts and large batch sizes quickly exhaust High Bandwidth Memory (HBM) on GPUs, managing the Key-Value (KV) cache is critical.

- **KV Caching and Prefix Caching.** Stores intermediate key and value tensors so the model does not recalculate past tokens. Prefix caching goes further by reusing shared system prompts across different user requests.
- **PagedAttention.** Inspired by virtual memory in operating systems, this technique splits the KV cache into non-contiguous, fixed-size blocks. It eliminates memory fragmentation and can boost serving throughput dramatically.
- **FlashAttention.** Reorders attention calculations to keep operations inside fast on-chip SRAM rather than repeatedly reading and writing to slower GPU main memory.
- **KV Cache Offloading.** Moves inactive or long-context KV cache data to host CPU memory or dedicated context memory tiers to free up GPU space.

## Serving and Runtime Optimizations

Infrastructure-level improvements focus on scheduling requests and utilizing hardware efficiently.

| Technique | Primary Mechanism | Key Benefit |
| --- | --- | --- |
| Continuous Batching | Dynamically injects new requests into a running batch as soon as older sequences finish. | Eliminates GPU idle time caused by varying output lengths and increases throughput. |
| Speculative Decoding | Uses a tiny "draft" model to guess several tokens ahead, which the main model verifies in parallel. | Cuts generation latency by 2x to 3x while mathematically preserving exact output quality. |
| Prefill-Decode Disaggregation | Separates the compute-heavy prefill phase and memory-heavy decode phase onto different GPU pools. | Prevents long prompts from stalling active token generation for other users. |
| Tensor and Pipeline Parallelism | Splits individual layers across multiple GPUs (tensor) or assigns sequential layers to different GPUs (pipeline). | Enables serving massive models that exceed the memory capacity of a single chip. |

## Flash Attention

**FlashAttention** is an IO-aware, exact attention algorithm that speeds up Transformer models and slashes memory usage by restructuring how attention matrices move between slow GPU main memory (HBM) and fast on-chip cache (SRAM). Because it computes the exact same mathematical output as standard attention without approximation, it serves as a drop-in replacement for both training and inference.

### The Bottleneck: GPU Memory Bandwidth

Standard self-attention is **memory-bound**, meaning GPUs spend more time transferring data than doing actual math.

- **The GPU Memory Hierarchy.**

Modern GPUs have large, relatively slow **High Bandwidth Memory (HBM)** (e.g., 80 GB) and tiny, ultra-fast on-chip **SRAM** (around 20 MB, roughly 10x faster in bandwidth).

- **HBM Round-Trips.** Standard attention computes the N × N attention score matrix (QK<sup>T</sup>), writes it out to slow HBM, reads it back to apply softmax, writes it again, and reads it back to multiply by V.
- **Quadratic Memory Wall.** As sequence length (N) grows, materializing that intermediate N × N matrix consumes quadratic memory (O(N²)), quickly exhausting VRAM on long prompts.

### How FlashAttention Solves It

Introduced by Tri Dao and collaborators, the algorithm keeps intermediate results on-chip using three core techniques:

- **Tiling.** Instead of loading the whole Q, K, and V matrices at once, FlashAttention splits them into small blocks that fit entirely inside fast SRAM. It computes attention block-by-block and never writes the massive intermediate N × N matrix to HBM.
- **Online Softmax.** Standard softmax needs the sum of exponents across an entire row before normalizing. FlashAttention calculates softmax incrementally as each tile arrives by tracking a running maximum and normalization factor, rescaling previous partial outputs on the fly.
- **Kernel Fusion and Recomputation.** All attention steps (matrix multiply, masking, softmax, dropout) are fused into a single GPU kernel. During training, it avoids saving the attention matrix for the backward pass and instead recomputes it rapidly in SRAM on the fly.

### Evolution of FlashAttention Versions

Each major release targets newer GPU architectures and unlocks higher hardware utilization:

| Version | Target Hardware | Key Architectural Upgrades | Impact |
| --- | --- | --- | --- |
| FlashAttention-1 | Ampere (A100, RTX 30-series) | Introduced SRAM tiling, online softmax, and single-kernel fusion. | 2x to 4x faster than standard attention; drops memory scaling from O(N²) to linear O(N). |
| FlashAttention-2 | Ampere, Ada, Hopper | Parallelizes across sequence length in addition to batch/heads, reduces non-matmul FLOPs, and improves warp partitioning. | ~2x faster than FA-1, reaching up to 73% of theoretical peak FLOPs on A100 GPUs. |
| FlashAttention-3 | Hopper (H100, H200) | Uses warp specialization (producer/consumer warps), asynchronous TMA memory transfers, and native FP8 quantization. | 1.5x to 2x faster than FA-2 on H100s, reaching ~75% utilization in FP16 and ~1.2 PFLOPS in FP8. |
| FlashAttention-4 | Blackwell (B200) and Hopper | Adds CuTeDSL kernels, split-KV parallelism for small queries, and arbitrary KV page size optimizations. | Delivers up to 1,613 TFLOPS on B200s and boosts single-token decode throughput. |

### Role in LLM Inference

In production inference, FlashAttention delivers distinct benefits depending on the execution phase:

- **Prefill Acceleration.** Processing long input prompts requires computing full N × N self-attention across all prompt tokens. FlashAttention speeds up prefill by 2x to 8x and drastically lowers Time to First Token (TTFT).
- **Long Context Capacity.** Because memory scales linearly (O(N)) rather than quadratically, a single GPU can process much longer context windows (e.g., 32K to 128K+ tokens) or pack more concurrent user requests into VRAM.
- **Decode Phase Nuances.** During autoregressive decoding, the query length is just 1 token, meaning the bottleneck shifts to reading the stored KV cache rather than computing a massive score matrix. Specialized variants like **FlashDecoding** (and split-KV in FA-3/FA-4) parallelize across the KV cache dimension to speed up this phase as well.

### How to Enable It

Most modern inference stacks use FlashAttention automatically under the hood:

- **PyTorch.** Calling torch.nn.functional.scaled_dot_product_attention automatically dispatches to FlashAttention kernels on supported NVIDIA Ampere or newer GPUs.
- **Hugging Face Transformers.** Pass attn_implementation="flash_attention_2" (or "flash_attention_3") when loading a model via from_pretrained().
- **Inference Engines.** Serving frameworks like **vLLM**, **SGLang**, and **TensorRT-LLM** integrate custom FlashAttention kernels natively alongside PagedAttention.

## Continuous Batching

**Continuous batching** (also known as **iteration-level scheduling**) is an LLM inference serving technique that dynamically inserts new incoming requests into a running batch and evicts completed sequences after every single token generation step, rather than waiting for an entire batch of requests to finish. First popularized by the Orca paper and widely deployed in engines like vLLM, it routinely increases GPU serving throughput by **2x to 4x** (and up to 10x+ on workloads with high variance in output length) without changing model outputs.

### The Problem with Static Batching

Traditional deep learning models (like image classifiers) process inputs of uniform size and run a fixed number of operations. LLMs behave very differently because text generation is autoregressive and unpredictable.

- **Straggler Bottleneck.** In static batching, the server groups a fixed number of prompts (e.g., 8 requests) and runs them together until the *longest* response finishes. If Request A finishes in 10 tokens while Request B takes 500 tokens, Request A's GPU slot sits completely idle for 490 iterations.
- **Padding Overhead.** Static batches pad all input prompts to the length of the longest prompt in the batch. The GPU wastes compute and memory bandwidth processing meaningless padding tokens.
- **Queueing Delays.** Newly arriving requests must wait in a queue until the entire active batch clears out, causing spikes in latency and poor hardware utilization.

### How Continuous Batching Works

Continuous batching shifts scheduling granularity from the **request level** down to the **iteration (single-token) level**.

- **Step-by-Step Scheduling.** After the model generates one token for every active sequence in the batch, the scheduler immediately checks if any sequence emitted an End-of-Sequence (<EOS>) token or hit its maximum token limit.
- **Immediate Slot Reclamation.** As soon as a sequence finishes, it exits the batch and returns its output to the user. Its freed memory and compute slot are filled on the very next forward pass by a waiting request from the queue.
- **Ragged Tensor Execution.** Instead of padding sequences to a uniform rectangle, modern inference kernels pack active tokens from different requests into flattened, contiguous arrays alongside metadata pointers, eliminating wasted math on pad tokens.

### Static vs. Continuous Batching

| Feature | Static Batching | Continuous Batching |
| --- | --- | --- |
| Scheduling Granularity | Request-level (entire batch starts and ends together). | Iteration-level (updated after every generated token). |
| Handling Finished Requests | Early finishers sit idle and output dummy tokens until the slowest request completes. | Finished requests exit immediately; new requests enter on the next step. |
| Memory Management | Pre-allocates worst-case contiguous memory per slot, causing high fragmentation. | Pairs with **PagedAttention** to allocate KV cache dynamically in small blocks. |
| GPU Utilization | Low to moderate (drops sharply when response lengths vary). | Consistently high (keeps batch size saturated near hardware limits). |
| Latency Profile | High queueing wait times for new arrivals during long generations. | Lower average wait times and predictable per-token generation speed. |

### Key Implementation Challenges & Modern Variants

Combining prefill and decode requests inside the same iteration introduces specific scheduling trade-offs that modern engines solve in clever ways:

- **Prefill vs. Decode Interference.** Inserting a brand-new request requires running its compute-heavy **prefill** phase (processing the full input prompt), which can temporarily stall the memory-bound **decode** step for other users already mid-generation.
- **Chunked Prefill.** Engines like vLLM and Sarathi-Serve split long input prompts into smaller chunks (e.g., 512 tokens at a time) and piggyback one chunk onto a batch of single-token decode steps. This keeps batch execution times smooth and avoids latency spikes.
- **KV Cache Paging.** Because requests enter and leave at unpredictable times, continuous batching relies heavily on **PagedAttention** (or RadixAttention in SGLang) to manage non-contiguous KV cache blocks without running out of memory.
