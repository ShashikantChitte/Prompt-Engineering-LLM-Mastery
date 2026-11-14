# Chapter 7 - Part 7: Connection back to reasoning models (Class 3: o1/o3/Claude Extended Thinking)

> Chapter 7: Chain-of-Thought and Reasoning Techniques

Modern reasoning models—such as OpenAI's o1/o3 series, Anthropic's Claude Extended Thinking, and DeepSeek-R1—represent the architectural culmination of prompt-engineered reasoning: they take explicit prompting techniques (CoT, Self-Consistency, Tree of Thoughts, and Reflection) and bake them directly into the model's weights via Reinforcement Learning (RL).

Instead of requiring engineers to write elaborate external orchestration loops in Python, these models execute search, verification, and backtracking **natively inside a single continuous stream of hidden "thinking" tokens**.

## 1. From Prompt Scaffolding to Learned Test-Time Compute

Every technique covered earlier solved a specific limitation of standard LLMs through external scaffolding. Modern reasoning models internalize those exact behaviors:

| Prompting Technique | External Scaffolding (2022–2024) | Internalized Behavior in Reasoning Models |
| --- | --- | --- |
| Chain-of-Thought (CoT) | Manually adding *"Let's think step by step"* or few-shot rationales. | **Native Thinking Blocks:** Automatically generates long, private reasoning traces before emitting a user-facing response. |
| Tree of Thoughts (ToT) | External BFS/DFS loops generating branching candidates and pruning dead ends. | **In-Context Backtracking:** Uses phrases like *"Wait, that contradicts constraint X, let me try another approach"* to abandon dead ends mid-stream. |
| Reflection & Self-Critique | Multi-turn Generator → Critic → Reviser API pipelines. | **Continuous Self-Verification:** Audits intermediate equations, edge cases, and assumptions dynamically while thinking. |
| Self-Consistency | Sampling N parallel paths at high temperature and running a majority vote. | **Parallel & Consensus Scaling:** Allocates higher reasoning_effort / thinking token budgets to explore and cross-check multiple hypotheses internally. |

### 2. How Reinforcement Learning Unlocks This

Standard LLMs are trained primarily via Supervised Fine-Tuning (SFT) to imitate human text, which encourages fluent, confident, single-pass answers. Reasoning models shift the training paradigm:

- **Outcome-Based RL (RLVR — Reinforcement Learning with Verifiable Rewards):** Models are trained on thousands of math, coding, and logic problems where the final answer can be objectively verified (e.g., unit tests passing or exact numerical match).
- **Emergent Cognitive Habits:** Because the model is rewarded *only* for reaching the verified answer—regardless of how many thinking tokens it uses—RL naturally teaches it to slow down, decompose problems, double-check arithmetic, and backtrack when stuck.
- **Test-Time Compute Scaling:** Just as larger parameter counts improved pretraining (Train-Time Compute), reasoning models unlock a second scaling axis: **allocating more thinking tokens at inference time** directly increases accuracy on harder problems.

### 3. How Your Prompting Strategy Changes for Reasoning Models

Because reasoning models already know *how* to think, traditional CoT prompt engineering actually becomes counterproductive:

- **Drop Explicit CoT Instructions:** Avoid writing *"Think step by step"* or providing detailed step-by-step few-shot reasoning traces. Over-constraining the model's scratchpad can interfere with its learned RL search patterns and degrade performance.
- **Focus on Goal & Constraints (What, Not How):** Provide crisp problem statements, clear success criteria, edge-case boundaries, and clean context—then let the model decide its own decomposition path.
- **Tune Compute via Effort Budgets:** Instead of building custom ToT or Self-Consistency orchestration code, control cost and latency by adjusting the model's **thinking budget / reasoning effort parameter** (low, medium, high) based on task difficulty.
- **Keep External Loops Only for Grounded Execution:** You only need external Reflection loops when the model requires **real-world environment feedback** it cannot simulate in its head—such as executing code against a live database, running a compiler, or querying live APIs.
