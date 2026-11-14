# Chapter 3 - Part 8: Reasoning models: o1/o3/Claude Extended Thinking - compute at inference time

> Chapter 3: What is an LLM? + Transformers and How They Work

**Reasoning models** are a class of AI models trained to solve complex, multi-step problems by generating an internal Chain-of-Thought (CoT)—often called hidden "thinking tokens"—before outputting a final answer. Instead of relying solely on scaling up model parameters during pre-training, models like **OpenAI's o1/o3/GPT-5 reasoning tiers**, **DeepSeek-R1**, **Gemini 2.5/3 Thinking**, and **Claude 3.7/4 Sonnet** use **test-time compute** to plan, verify steps, backtrack from mistakes, and explore multiple paths during inference.

## Pre-Training Scale vs. Test-Time Compute

Traditional LLMs predict the next word immediately using intuition-like pattern matching, which often causes them to stumble on multi-step logic, competitive math, or complex debugging.

- **System 1 vs. System 2 Thinking.** Standard LLMs act like fast, instinctive "System 1" thinkers that blurt out the first plausible continuation. Reasoning models simulate slow, deliberate "System 2" thinking by spending extra inference time breaking problems down and checking their work.
- **Inference-Time Scaling Laws.** Just as adding more data and GPUs during training improves accuracy, allowing a reasoning model to generate more thinking tokens at test time yields predictable, logarithmic accuracy gains on hard benchmarks.

## How Reasoning Models Are Trained

Reasoning capabilities are unlocked primarily through large-scale **Reinforcement Learning (RL)** on tasks with verifiable outcomes, rather than just human preference ratings.

- **Outcome-Based Reinforcement Learning.** Models are given thousands of math, coding, and science problems where answers can be automatically verified (e.g., passing unit tests or matching exact mathematical proofs). They receive rewards for reaching the right answer, naturally discovering human-like habits like self-correction, hypothesis testing, and edge-case checking.
- **Distillation into Smaller Models.** Once a giant reasoning model masters structured thinking, labs use its reasoning traces to fine-tune much smaller dense models (such as Qwen-7B or Llama-8B distilled variants), transferring strong logical abilities to lightweight hardware.

## Inference Challenges & Optimizations

Because a reasoning model might generate **5,000 to 50,000+ hidden thinking tokens** to produce a 200-word reply, they create extreme inference bottlenecks—and require specialized optimizations to stay fast and affordable.

| Bottleneck | Why Reasoning Models Make It Worse | Key Optimization Solutions |
| --- | --- | --- |
| Massive KV Cache Growth | Long chains of thought rapidly fill up GPU High Bandwidth Memory (HBM), capping batch sizes. | **FP8/INT4 KV Cache Quantization**, **Multi-Head Latent Attention (MLA)**, and **PagedAttention**. |
| High End-to-End Latency | Users wait seconds or minutes while the model generates thousands of sequential decode tokens. | **Speculative Decoding** (guessing 3–5 thinking tokens at once) and ultra-fast **MoE** backbones. |
| Overthinking Simple Prompts | Spending 10,000 thinking tokens on "What is the capital of France?" wastes money and time. | **Adaptive Reasoning Budgets** (reasoning_effort controls) and dynamic query routers that bypass thinking on easy prompts. |
| Repetitive Thought Loops | Models can get stuck second-guessing themselves or repeating verification steps endlessly. | **Length penalties** in RL training and early-stopping confidence classifiers that halt thinking once an answer stabilizes. |

## When to Use Reasoning Models vs. Standard LLMs

- **Best for Reasoning Models:** Multi-file software architecture, debugging subtle race conditions, mathematical proofs, financial modeling, scientific research, and strict constraint satisfaction.
- **Best for Standard (Non-Thinking) LLMs:** Creative writing, translation, basic summarization, real-time voice assistants, and straightforward Q&A where low Time-to-First-Token (TTFT) matters more than deep multi-step verification.

## o1/o3/Claude Extended Thinking - compute at inference time

**Test-time compute** (or **inference-time compute**) is the paradigm behind **OpenAI o1/o3** and **Claude Extended Thinking** (introduced in Claude 3.7 Sonnet and evolved in Claude 4), where an AI model dynamically spends extra GPU cycles generating hidden reasoning steps before delivering a final answer. Rather than relying strictly on a massive, fixed parameter count built during pre-training, these models trade **inference latency and tokens for higher accuracy** on complex tasks.

### How Test-Time Compute Works

When you send a prompt to a standard LLM, it runs a single forward pass per output token. Models like o1, o3, and Claude Extended Thinking insert a variable-length **internal scratchpad** between your prompt and the visible reply.

- **Serial Reasoning Chains.** The model generates a step-by-step Chain-of-Thought (CoT) inside hidden reasoning blocks. It breaks problems into sub-goals, tests hypotheses, catches logic errors, and backtracks before writing the final response.
- **Parallel Sampling & Verification (Best-of-N / Search).** At higher compute settings (such as o3-high), systems can also generate multiple candidate reasoning paths in parallel and use a learned **Process Reward Model (PRM)** or verifier to score intermediate steps and select the winning trajectory.
- **Context Discarding Across Turns.** In multi-turn conversations, both OpenAI's API and Claude's API typically strip previous turns' hidden thinking tokens from the active context window once the final answer is produced. This prevents runaway KV cache growth and keeps subsequent turns affordable.

### Comparing OpenAI o1/o3 and Claude Extended Thinking

| Dimension | OpenAI o1 & o3 | Anthropic Claude Extended Thinking |
| --- | --- | --- |
| Architecture Approach | Dedicated reasoning model family trained end-to-end via large-scale Reinforcement Learning (RL) to think before speaking. | Hybrid model design where a single model toggles between instant responses and deep extended thinking. |
| Compute Control Mechanism | Discrete reasoning_effort tiers (low, medium, high, plus xhigh in newer models) that guide how long the model thinks. | Explicit thinking.budget_tokens parameter (e.g., setting a cap from 1,024 up to 64K+ tokens) or adaptive effort controls. |
| Visibility of Thoughts | Hidden by default; APIs and apps display summarized thought headings rather than raw tokens to protect safety and distillation. | Transparent by default in Claude 3.7 (visible thinking blocks), transitioning to summarized thinking in Claude 4 with cryptographic signatures for multi-turn tool use. |
| Tool Use During Thinking | o3 natively interleaves web search, Python execution, and file analysis *inside* its thinking loop to verify facts mid-thought. | Supports **interleaved thinking**, allowing Claude to pause reasoning, call external tools/APIs, inspect results, and continue thinking. |

### The Economics and Systems Trade-Offs

Shifting compute from training to inference fundamentally changes hardware utilization and unit economics:

- **Training Cost vs. Inference Cost.** Pre-training is a massive one-time capital expense, while test-time compute scales linearly with every single user query. A prompt that generates 20,000 hidden thinking tokens consumes **20x to 50x more GPU memory bandwidth** than a standard 400-token reply—and users are billed for those hidden thinking tokens as output tokens.
- **Decode-Bound Bottlenecks.** Because reasoning tokens are generated sequentially, test-time compute pushes inference servers heavily into the **memory-bandwidth-bound decode phase**. Serving these models economically relies on **FP8/INT4 quantization**, **KV cache compression**, and **speculative decoding** to rapidly draft predictable reasoning steps.
- **Diminishing Returns Curve.** Accuracy scales roughly logarithmically with test-time compute. Moving from 1,000 to 10,000 thinking tokens yields huge gains on competitive math and coding, while pushing past 50,000 tokens offers smaller incremental improvements at steep latency costs.

### Practical Rules of Thumb for Developers

- **Match Compute to Task Complexity.** Use low reasoning effort or disable extended thinking for classification, formatting, and retrieval tasks where extra thinking actually hurts speed and can cause over-analysis.
- **Set Hard Token Budgets.** When using Claude Extended Thinking or OpenAI's reasoning tiers in production, cap maximum reasoning tokens so edge-case prompts cannot trigger 60-second stalls or unexpected API spikes.
- **Leverage Interleaved Tool Calls.** For agentic workflows, allow the model to execute code or query databases *during* its thinking phase so it grounds its reasoning in real outputs rather than guessing.
