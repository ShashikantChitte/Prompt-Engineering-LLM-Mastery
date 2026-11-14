# Chapter 7 - Part 5: Reflection and self-critique

> Chapter 7: Chain-of-Thought and Reasoning Techniques

**Reflection and Self-Critique** (popularized by frameworks like **Self-Refine** by Madaan et al., 2023, and **Reflexion** by Shinn et al., 2023) is an iterative reasoning pattern where an LLM generates an initial output, evaluates its own work against specific criteria or external feedback, and uses that critique to produce an improved revision.

Unlike Tree of Thoughts—which searches *horizontally* across branching alternatives before finishing—Reflection works *vertically* by taking a complete draft and refining it across multiple sequential passes.

### 1. How the Reflection Loop Works

The standard self-critique pipeline repeats a three-step cycle until a stopping condition (such as passing a rubric or hitting a maximum iteration limit) is met:

1. **Generate (Draft):** The model produces an initial solution, piece of code, or reasoning trace y₀ for the task.
2. **Critique (Reflect):** A separate prompt (the **Critic**) inspects y₀ alongside the original instructions, identifying specific logical flaws, missed constraints, edge cases, or formatting errors.
3. **Refine (Revise):** The **Actor** receives the original prompt, its previous draft y₀, and the structured critique, then generates an upgraded version y₁.

### 2. Two Major Flavors of Reflection

- **Intrinsic Self-Refine (No External Tools):** The model relies purely on its own internal knowledge to spot errors (e.g., *"Review your SQL query above for syntax errors, missing JOIN conditions, or edge cases with NULL values"*).
- **Grounded Reflexion (With External Feedback):** The model pairs self-critique with **verifiable environment signals**—such as Python tracebacks, unit test failures, compiler warnings, or search results—and writes a verbal "lesson learned" into memory before trying again.

### 3. Why Self-Critique Works (and Its Critical Catch)

- **Verification Is Easier Than Generation:** In computer science and cognitive tasks, spotting a bug in existing code or a logical leap in a proof requires far less search effort than generating a flawless solution from scratch on the first pass.
- **Decoupled Roles Prevent Confirmation Bias:** Separating the *Generation* prompt from the *Critique* prompt forces the model to switch out of "completion mode" and adopt an adversarial auditing mindset.
- **The "Intrinsic Self-Correction" Caveat:** Research (e.g., Huang et al., 2023) shows that without external ground-truth feedback (like code execution or strict rubrics), LLMs sometimes second-guess *correct* answers and flip them to wrong ones—or hallucinate non-existent flaws. Reflection is dramatically more reliable when anchored by deterministic checks or explicit evaluation rubrics.

## Comparison: ToT vs. Self-Consistency vs. Reflection

| Dimension | Self-Consistency | Tree of Thoughts (ToT) | Reflection / Self-Critique |
| --- | --- | --- | --- |
| Mechanism | Parallel independent attempts + majority vote | Branching search over intermediate steps | Iterative drafting, critiquing, and revising |
| Error Correction | Filters out random mistakes via consensus | Prunes bad branches before reaching the end | Fixes specific bugs found in a completed draft |
| Best Use Cases | Math, classification, discrete answers | Multi-step planning, puzzles, combinatorial search | Code generation, long-form writing, complex instruction following |

## Reflection and self-critique - model reviews its own output

**Reflection and Self-Critique** is an iterative prompting pattern where a model acts as its own reviewer, inspecting a generated output against explicit rules or external feedback to produce a cleaner, more accurate revision.

Instead of expecting a single forward pass to satisfy every constraint simultaneously, this pattern separates **creative/logical generation** from **critical verification**.

### 1. The Three-Stage Review Loop

When a model reviews its own output, the workflow follows a structured loop:

1. **Initial Generation (The Producer):** The model answers the prompt or generates an artifact (code, JSON, essay, or math proof) without worrying about perfection.
2. **Self-Review (The Critic):**

A second prompt passes the original task and the initial draft back to the model, instructing it to audit the work for specific flaws, missed constraints, or logical gaps.

3. **Targeted Revision (The Editor):** The model uses its own critique as an actionable checklist to rewrite and fix the draft, repeating the loop (usually 1–3 times) until no critical issues remain.

### 2. Why Self-Review Catches Errors Missed on the First Pass

- **Asymmetry of Verification vs. Generation:** Checking whether a solution satisfies five constraints is computationally much easier for a transformer than generating a response that obeys all five constraints from scratch.
- **Fresh Attention Context:** During initial generation, the model's attention is stretched across planning the response, maintaining syntax, and recalling facts. In the review pass, the full draft already exists in the context window, allowing attention heads to focus exclusively on spotting contradictions or edge cases.
- **Breaking Autoregressive Momentum:** Left-to-right token generation locks a model into early mistakes. A separate critique pass breaks that momentum and permits localized edits without rewriting the entire thought process blindly.

### 3. Best Practices for Effective Self-Critique

Because LLMs can suffer from **sycophancy** (agreeing with their own flawed output) or **over-correction** (changing a right answer into a wrong one), effective self-review relies on strict prompting guardrails:

- **Use Rubric-Based Audits:** Never ask *"Is this good? Fix any mistakes."* Instead, provide a concrete checklist (e.g., *"Verify: 1) Every claim cites a provided source, 2) Output matches the JSON schema, 3) No division by zero occurs"*).
- **Separate Critique from Revision:** Force the model to output a structured list of flaws *before* writing the revised answer so it commits to diagnosing bugs rather than glossing over them.
- **Anchor with External Tools:** Pair self-critique with deterministic verifiers—such as a Python interpreter, SQL linter, regex validator, or unit test suite—so the model reviews real error messages rather than guessing.
- **Add a "No-Change" Escape Hatch:** Explicitly instruct the model: *"If the original draft passes all rubric criteria without errors, output it unchanged."* This prevents unnecessary edits on already-correct outputs.

## Concrete Example: Code & Logic Self-Review

| Pass | Role | Action |
| --- | --- | --- |
| Pass 1 | **Generator** | Writes a Python function to parse dates, accidentally overlooking leap years. |
| Pass 2 | **Critic** | Audits against edge cases: *"Bug found: February 29 fails validation on leap years like 2024."* |
| Pass 3 | **Reviser** | Updates the date logic using the critique and outputs the corrected function. |
