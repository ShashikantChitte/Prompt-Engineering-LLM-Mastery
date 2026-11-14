# Chapter 7 - Part 6: Choosing the right technique for a given problem

> Chapter 7: Chain-of-Thought and Reasoning Techniques

Choosing the right reasoning technique depends on balancing task complexity, error tolerance, latency, and token budget. Every step up in reasoning sophistication trades extra inference compute for higher reliability.

### 1. Decision Matrix by Problem Type

| Problem Profile | Recommended Technique | Why It Fits | Compute Cost |
| --- | --- | --- | --- |
| Simple recall, translation, or basic formatting | **Direct Zero-Shot / Few-Shot** | Single-pass knowledge retrieval needs no extra tokens; CoT only adds latency. | **1x** (Lowest) |
| Multi-step math, logic, or rule classification | **Standard / Zero-Shot CoT** | Unlocks step-by-step compute and externalizes working memory in a single linear pass. | **1.5x – 3x** |
| High-stakes discrete answers (math, MCQs, routing) | **Self-Consistency (CoT + Voting)** | Eliminates random arithmetic or logic slips by aggregating N independent paths. | **5x – 20x** |
| Combinatorial search, puzzles, or multi-step planning | **Tree of Thoughts (ToT)** | Enables lookahead evaluation and backtracking when early choices lead to dead ends. | **10x – 100x** |
| Code generation, long-form writing, or strict schemas | **Reflection / Self-Critique** | Separates generation from rubric-based auditing, ideally anchored by unit tests or linters. | **2x – 4x** |

### 2. Three Questions to Pick Your Strategy

Walk through these three filters in order before adding complexity:

- **Filter 1: Can the answer be solved in a single intuitive leap?**
  - *Yes:* Stick to **Standard Zero-Shot or Few-Shot**. Do not force CoT on simple summarization, extraction, or trivia.
  - *No (requires tracking state or combining multiple facts):* Start with **Chain-of-Thought (CoT)**.
- **Filter 2: What happens if the model makes one mistake mid-way?**
  - *Answers are discrete and easy to vote on (numbers, categories):* Wrap CoT in **Self-Consistency** to filter out stochastic errors.
  - *Output is an artifact (code, SQL, structured report) that can be tested or audited:* Add a **Reflection / Self-Critique** loop paired with a deterministic validator (compiler, linter, or schema check).
- **Filter 3: Do early decisions lock out valid solutions later?**
  - *Yes (planning, scheduling, complex debugging, constraint puzzles):* Upgrade to **Tree of Thoughts (ToT)** so the system can branch, score intermediate states, and backtrack.

### 3. Production Rule of Thumb: Escalate Gradually

Never start with Tree of Thoughts or heavy multi-agent loops on day one. Follow an incremental escalation ladder:

1. **Baseline:** Start with **Standard CoT** (with XML <thinking> tags) to establish a fast, cheap benchmark.
2. **Verify:** Add **Tool-Grounded Reflection** (e.g., code execution or schema validation) if outputs fail syntactic or rule checks.
3. **Scale Compute:** Layer on **Self-Consistency** (or switch to a dedicated RL reasoning model) only on the hardest, highest-value edge cases where accuracy outweighs latency and cost.
