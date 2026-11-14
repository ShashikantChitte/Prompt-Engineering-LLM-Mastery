# Chapter 3 - Quick Check

> Chapter 3: What is an LLM? + Transformers and How They Work

> Related part: Reasoning models: o1/o3/Claude Extended Thinking - compute at inference time

### Q1. An LLM outputs a probability distribution over the vocabulary at each step. What determines which token actually appears in the output? Name two different strategies

A decoding strategy (also called a sampling strategy) determines which token actually appears in the output from the model's probability distribution. While the neural network produces raw scores (logits) converted into probabilities via softmax, the decoding algorithm acts as the selection rule that picks the final token at each step.

Two common strategies are **Greedy Decoding** and **Top-p (Nucleus) Sampling**.

#### 1. Greedy Decoding (Deterministic)

Greedy decoding always selects the single token with the **highest probability** at every generation step.

- **How it works.** The algorithm looks at the probability distribution, picks the top-scoring word (argmax), appends it to the sequence, and moves to the next step.
- **Strengths and trade-offs.** It is fast, predictable, and well-suited for factual extraction, math, or structured formatting where one clear answer exists. However, it often produces repetitive, generic text because it never explores slightly lower-probability words that might lead to a much better overall sentence.

#### 2. Top-p (Nucleus) Sampling (Stochastic)

Top-p sampling randomly chooses the next token from the smallest group of top words whose **cumulative probability reaches or exceeds a threshold** $p$ (such as $p = 0.9$).

- **How it works.** The model sorts all tokens from highest to lowest probability, adds them up until their combined probability hits 90%, discards the remaining long tail of unlikely words, and samples randomly from that dynamic "nucleus" of candidates.
- **Strengths and trade-offs.** Because the candidate pool automatically expands when the model is uncertain and shrinks when the model is confident, top-p sampling balances creativity with coherence. It avoids the robotic loops of greedy decoding while preventing nonsensical, ultra-low-probability words from slipping into the text.

### Quick Comparison

| Strategy | Selection Rule | Output Style | Best Use Case |
| --- | --- | --- | --- |
| Greedy Decoding | Always picks the single highest-probability token. | Deterministic, focused, and occasionally repetitive. | Code syntax, math, translation, and exact Q&A. |
| Top-p (Nucleus) Sampling | Randomly samples from the top tokens summing to probability $p$. | Natural, varied, and context-aware. | Creative writing, conversational chat, and brainstorming. |

### Q2. Why did RNNs struggle with long sequences even after the LSTM's gating mechanism was introduced?

Even with the Long Short-Term Memory (**LSTM**) gating mechanism, Recurrent Neural Networks (**RNNs**) struggled with long sequences primarily because of fixed-size memory bottlenecks, sequential computation limits, and residual gradient degradation over hundreds of steps. While LSTMs solved the worst mathematical instabilities of vanilla RNNs, they could not overcome the structural limits of compressing an entire sequence into a single rolling state vector.

#### 1. The Fixed-Size Bottleneck (Information Compression)

An LSTM passes a single hidden state vector ($h_t$) and cell state vector ($c_t$) of fixed dimensions (for example, 512 or 1,024 numbers) from one word to the next.

- **Squeezing Everything Into One Vector.** Whether a document is 20 words or 5,000 words long, the model must cram every relevant fact, subject-verb relationship, and context clue into that exact same fixed-size array.
- **Memory Overwriting.** Over hundreds of steps, the forget and input gates constantly overwrite older values to make room for new tokens. Crucial details from the beginning of a paragraph inevitably dilute or get erased before the model reaches the end.

#### 2. Sequential Execution Prevents Scaling

RNNs and LSTMs are inherently sequential: calculating step **$t$** requires the hidden state from step **$t-1$**.

- **No Training Parallelization.** Unlike Transformers—which process every token in a prompt simultaneously—an LSTM must step through a 2,000-token sequence one token at a time. This made training on massive datasets painfully slow on modern GPUs and TPUs.
- **Limited Model Capacity.** Because sequential processing was so slow, researchers could not easily scale LSTMs to billions of parameters or train them on trillions of tokens, capping their ability to learn complex long-range patterns.

#### 3. Residual Vanishing Gradients & Long Path Lengths

LSTMs introduced the **cell state highway** (an additive path controlled by gates) to help gradients flow backward without shrinking to zero. However, this fix had practical limits on very long sequences.

- **Multi-Step Decay.** Even if a forget gate stays at 0.99 at every step, multiplying 0.99 across 500 tokens reduces the signal to $0.99^{500} \approx 0.0066$. Gradients still fade over very long distances, making it hard to learn dependencies separated by hundreds of words.
- **O(N) Path Length.** Information from token 1 must travel through $N$ sequential recurrent steps to influence token $N$. Every step introduces noise and transformation, whereas self-attention creates a direct **O(1)* shortcut between any two tokens regardless of distance.

### Summary: Why Transformers Replaced LSTMs

| Limitation | How LSTMs Handled It | How Transformers Solved It |
| --- | --- | --- |
| Memory Capacity | Compressed all past context into one fixed-size cell state vector. | Keeps every past token explicitly accessible via Key-Value (KV) states. |
| Distance Between Tokens | Linear *O(N)* path length; distant tokens required hundreds of hops. | Direct *O(1)* path length via self-attention between any pair of tokens. |
| Training Speed | Strictly sequential token-by-token processing. | Fully parallelized across the entire sequence during training. |

### Q3. In self-attention, what are the Queries, Keys, and Values conceptually? If you doubled the number of attention heads without changing d_model, what would you need to adjust?

Conceptually, **Queries $(Q)$, Keys $(K)$, and Values $(V)$** work like a soft, differentiable database lookup system where every token searches the rest of the sequence for relevant context. If you double the number of attention heads **($h$)** while keeping **$d_{model}$** fixed, you must cut the dimension of each individual head **($d_k$ and $d_v$)** in half so the total concatenated output still matches **$d_{model}$**.

#### 1. Conceptual Role of Queries, Keys, and Values

Every input token embedding is multiplied by three learned weight matrices **($W_Q$, $W_K$, $W_V$)** to produce three distinct vectors:

- **Query $(Q)$ — "What am I looking for?"** Represents the current token's active search request. For example, in the sentence *"The dog chased the ball because* **$it$** *was bouncy"*, the word **$"it"$** generates a Query looking for a noun that can bounce.
- **Key $(K)$ — "What do I offer or describe?"** Acts like an index label or metadata tag advertised by every token in the sequence. The word *"ball"* emits a Key signaling *"I am a round, inanimate object"*, while *"dog"* emits a Key signaling *"I am a living animal"*.
- **Value $(V)$ — "What actual information do I pass along?"** Contains the rich semantic content of the token. Once the Query from *"it"* matches strongly with the Key from *"ball"* (via a dot product and softmax), the model pulls in the **Value** vector of *"ball"* to update the representation of *"it"*.

#### 2. What Must Change If You Double Attention Heads?

In Multi-Head Attention, the model splits its total embedding width $d_{model}$ evenly across all parallel attention heads rather than running full-width attention multiple times.

- **Halve the Per-Head Dimension** <b><i>($d_k$ and $d_v$)</i></b>**.** The standard relationship is $d_{model} = h \times d_k$. If $d_{model}$ stays at 512 and you double the heads from 8 to 16, each head's projection size ($d_k$ and $d_v$) must shrink from 64 down to 32.
- **Adjust Projection Matrix Shapes.** The learned projection matrices ($W_Q$, $W_K$, $W_V$) for each head change shape from ($d_{model}$, 64) to ($d_{model}$, 32) so that when all 16 head outputs are concatenated back together (16 × 32 = 512), they fit cleanly into the final output projection matrix $W_O$ of shape ($d_{model}$, $d_{model}$).
- **Update the Scaling Factor $(\sqrt{d_k})$.** Inside scaled dot-product attention, scores are divided by $\sqrt{d_k}$ to keep gradients stable. Because $d_k$ is halved, the scaling denominator adjusts automatically from $\sqrt{64} = 8$ to $\sqrt{32} \approx 5.66$.

### Summary of the Trade-Off

| Parameter | Before Doubling Heads | After Doubling Heads | Impact on the Model |
| --- | --- | --- | --- |
| **Model Dimension ($d_{model}$)** | 512 | 512 (Unchanged) | Total parameter count and FLOPs stay roughly identical. |
| **Number of Heads ($h$)** | 8 | 16 (Doubled) | Model can track twice as many distinct relationship subspaces (e.g., syntax, coreference, tone) simultaneously. |
| **Head Dimension ($d_k$, $d_v$)** | 64 | 32 (Halved) | Each individual head has less representational capacity to capture complex features on its own. |

### Q4. You have a 4096-token prompt and you want to generate 500 tokens. Without KV cache, roughly how many attention operations does the decode phase require compared to with KV cache? (Order of magnitude is fine.)

Without a *KV* cache, the decode phase requires roughly 4,350× more attention operations—on the order of **$10^{10}$** token-pair interactions compared to **$10^{6}$** with a *KV* cache.

### Step-by-Step Breakdown

Let $P = 4096$ be the prompt length and $G = 500$ be the number of generated tokens. At each decode step $i$ (from 1 to 500), the total sequence length is $L_i = P + i$ (growing from 4,097 up to 4,596).

- **Without *KV* Cache (O(L²) per step):** Because nothing is saved, the model recomputes all Keys, Queries, and Values from scratch for every token in the sequence at every step. This requires computing a full $L_i \times L_i$ attention matrix at each iteration:

$$
\sum_{i=1}^{500} {\left( 4096 + i \right)}^{2} \approx 500 \times {\left( 4346 \right)}^{2} \approx 9.46 \times 10^{9}\text{ operations}
$$

- **With *KV* Cache (O(L) per step):** Past Keys and Values are stored in GPU memory. The model only computes a single Query vector for the newest token and attends it against the $L_i$ cached Keys ($1 \times L_i$):

$$
\sum_{i=1}^{500} \left( 4096 + i \right) \approx 500 \times 4346 \approx 2.17 \times 10^{6}\text{ operations}
$$

### Comparison Summary

| Metric | Without $KV Cache | With KV Cache |
| --- | --- | --- |
| Work at Step $i$ | $(4096 + i)^2$ token-pair scores | $1 \times (4096 + i)$ token-pair scores |
| Total Decode Operations | $\approx 9.46 \times 10^{9} (\sim 10^{10})$ | $\approx 2.17 \times 10^{6} (\sim 10^{6})$ |
| Scaling Complexity | Quadratic per step (O(G . L²)) | Linear per step O(G . L) |
| Relative Overhead | ~ 4,350 X more compute (roughly the average sequence length) | Baseline (1 X) |

### Q5. A Mistral 8x7B MoE model has ~47B total parameters but ~13B active per token. What are the two main downsides of MoE compared to a dense model of the same active-parameter count?

Compared to a dense **~13B** parameter model, the two main downsides of a **Mixtral 8x7B** MoE model are massive **VRAM** (memory) requirements and poor memory-bandwidth efficiency at small batch sizes, alongside increased multi-GPU communication and routing complexity.

#### 1. Full Memory Footprint (VRAM Capacity Bottleneck)

Even though **Mixtral 8x7B** activates only **~13B parameters** per token, the GPU cannot predict which two experts the next token will choose.

- **All Weights Must Stay Loaded.** All **~47B parameters** must reside in fast GPU High Bandwidth Memory (HBM) simultaneously.
- **Hardware Cost Jump.** While a dense **13B** model fits easily on a single consumer or mid-range GPU (**~26 GB in FP16, or ~8 GB in 4-bit**), Mixtral 8x7B requires **~94 GB in FP16**—forcing you onto multi-GPU setups (such as two 80 GB A100s) or aggressive quantization just to load the weights.

#### 2. Low Arithmetic Intensity & Communication Overhead

During generation, an **MoE** model behaves very differently from a dense 13B model when serving traffic or splitting across GPUs.

- **Memory-Bandwidth Bottleneck at Small Batches.** In a dense **13B** model, every token in a small batch reuses the exact same **13B** weights. In **Mixtral 8x7B**, a batch of just 4 to 8 tokens can trigger *all 8 experts* across a layer, forcing the GPU to read almost the entire **47B parameter pool** from HBM while doing only **13B** worth of math per token.
- **All-to-All Communication Overhead.** When the model is split across multiple GPUs using **Expert Parallelism**, tokens must be shuffled over GPU interconnects (All-to-All collectives) to reach the specific GPU holding their assigned experts, adding synchronization latency that a single-GPU dense **13B** model avoids completely.

### Quick Comparison: Mixtral 8x7B vs. Dense 13B

| Metric | Dense 13B Model | Mixtral 8x7B (MoE) |
| --- | --- | --- |
| **Active Compute per Token** | **~13B parameters** | **~13B parameters** |
| **Total Parameters in VRAM** | **~13B (~26 GB in FP16)** | **~47B (~94 GB in FP16)** |
| **Single-User Decode Speed** | Fast (reads only 13B weights per step) | Slower (unpredictable expert jumps strain memory bandwidth) |
| **Multi-GPU Scaling** | Simple (fits on 1 GPU) | Complex (requires Expert/Tensor Parallelism and All-to-All syncs) |

### Q6. Flash Attention produces the same mathematical output as standard attention. What exactly does it change, and why does that matter for long-context inference?

**FlashAttention** changes how and where the attention math is scheduled across the GPU's memory hierarchy—specifically by tiling inputs into fast on-chip **SRAM** and fusing operations so the massive intermediate attention matrix is never written to slow GPU main memory (**HBM**). For long-context inference, this eliminates the **quadratic *O(N²)* memory bottleneck** and drastically cuts slow HBM read/write traffic, preventing Out-of-Memory (OOM) crashes and slashing Time-to-First-Token (TTFT).

### What FlashAttention Actually Changes

Instead of changing the equation:

$$
\text{Softmax}\left( \frac{QK^{T}}{\sqrt{d_{k}}} \right)V
$$

FlashAttention changes the **memory access pattern (IO-awareness)** using three execution tricks:

- **SRAM Tiling Instead of Full Matrix Materialization.** Standard attention computes the entire *N × N* attention score matrix $QK^T$, writes it out to slow HBM (VRAM), reads it back to compute softmax, writes it out again, and reads it back a third time to multiply by V. FlashAttention splits Q, K, and V into small blocks (tiles) that fit inside ultra-fast on-chip SRAM (~20 MB), computing attention block-by-block without ever writing the *N × N* matrix to HBM.
- **Online Softmax (Incremental Rescaling).** Because softmax normally needs the sum of all scores across an entire row before normalizing, standard attention must materialize the whole row first. FlashAttention tracks a running maximum and normalization factor as each tile passes through SRAM, rescaling partial outputs on the fly so it only ever stores the compact final output vector.
- **Kernel Fusion.** Standard frameworks launch separate GPU kernels for matrix multiplication, causal masking, softmax, and dropout—each requiring a round-trip to HBM. FlashAttention fuses all of these steps into a single CUDA kernel so intermediate values stay inside GPU registers and SRAM.

### Why This Matters for Long-Context Inference

During the **prefill phase** (when the model reads your prompt before generating the first token), self-attention must process all *N* input tokens simultaneously. As *N* scales to 32K, 128K, or 1M+ tokens, standard attention breaks down:

- **Eliminates the *O(N²)* Memory Wall.** At a context length of *N* = 100,000 tokens (with 32 attention heads in FP16), materializing the intermediate *N × N* attention matrix alone requires **~640 GB of VRAM**—instantly crashing any single GPU. FlashAttention drops memory usage from quadratic *O(N²)* down to **linear O(N)**, needing only a few megabytes of extra workspace memory regardless of prompt length.
- **Slashes Time-to-First-Token (TTFT).** On long prompts, standard attention spends the vast majority of its runtime waiting on slow HBM data transfers rather than doing math. By keeping operations inside fast SRAM (which has roughly 10x higher bandwidth than HBM), FlashAttention speeds up long-context prefill by **2x to 8x**, turning multi-second prompt processing stalls into sub-second responses.
- **Frees VRAM for Larger KV Caches and Batches.** Because attention calculations no longer spike VRAM usage during prefill, serving engines like vLLM and SGLang can dedicate almost all remaining GPU memory to holding longer **KV caches** or serving more concurrent users simultaneously.

### Standard Attention vs. FlashAttention at Long Contexts

| Dimension | Standard Self-Attention | FlashAttention |
| --- | --- | --- |
| Intermediate *N × N* Matrix | Written and read multiple times in slow HBM. | Never materialized in HBM; computed block-by-block in SRAM. |
| Memory Scaling with Context (N) | **Quadratic *O(N²)*** — quickly causes OOM errors on long prompts. | **Linear *O(N)*** — scales effortlessly to 128K–1M+ tokens. |
| Primary Bottleneck | **Memory-bandwidth bound** (stalled by HBM reads/writes). | **Compute-bound** (keeps Tensor Cores running near peak FLOPs). |
| Long-Context Prefill (TTFT) | Slow due to heavy memory I/O overhead. | **2x to 8x faster** while producing bit-for-bit equivalent math. |

### Q7. A user asks you to use a reasoning model (like o1) for generating marketing copy. Is this a good use case? What types of tasks do reasoning models actually improve on over standard models?

No, generating standard marketing copy is generally a poor use case for a reasoning model. Standard LLMs (like GPT-4o, Claude 3.5/4 Sonnet, or Gemini Flash) are faster, far cheaper, and often produce more natural, punchy copy than reasoning models.

### Why Marketing Copy Doesn't Need a Reasoning Model

- **No Verifiable Multi-Step Logic.** Creative copywriting relies on tone, rhythm, emotional resonance, and style rather than deductive logic or step-by-step proofs. Generating 5,000 hidden "thinking tokens" to debate adjective choices adds latency and cost without making a tagline catchier.
- **Risk of Over-Engineering.** Reasoning models are trained via Reinforcement Learning to check edge cases and satisfy strict logical rules. When asked for creative prose, they frequently over-analyze the prompt, resulting in stiff, overly literal, or formulaic text.
- **Poor Cost and Latency Trade-Off.** Users expect fast turnaround when iterating on copy. Waiting 15–30 seconds and paying 5x–10x more per output token makes rapid creative brainstorming sluggish and expensive. *(The only exception is highly constrained copy—such as ad copy that must simultaneously obey strict legal compliance rules, exact character limits, and complex A/B personalization matrices.)*

### What Tasks Reasoning Models Actually Improve On

Reasoning models shine on problems with **verifiable outcomes**, **hidden traps**, and **multi-step dependencies** where an initial intuitive guess is likely to fail:

| Task Category | Why Reasoning Models Excel | Concrete Examples |
| --- | --- | --- |
| Complex Software Engineering | Can trace execution paths, simulate edge cases, and backtrack when a proposed fix breaks another module. | Debugging race conditions, refactoring across multiple files, or writing complex SQL/regex queries. |
| Mathematics & Quantitative Logic | Breaks equations into sequential steps and double-checks arithmetic before committing to an answer. | Competitive math proofs, financial modeling, probability puzzles, and statistical analysis. |
| Multi-Step Planning & Strategy | Evaluates trade-offs, checks dependencies, and resolves conflicting constraints systematically. | Designing distributed system architectures, supply-chain routing, or multi-stage project schedules. |
| Dense Document & Legal Synthesis | Cross-references clauses across long contexts to spot subtle contradictions or compliance gaps. | Auditing contracts for conflicting terms, analyzing scientific papers, or synthesizing regulatory rules. |
| Strict Constraint Satisfaction | Tracks multiple simultaneous rules and revises drafts internally until every constraint passes. | Generating valid complex JSON/XML schemas, crossword construction, or heavily regulated medical/financial disclosures. |
