# Chapter 7 - Part 1: Chain-of-Thought and Reasoning Techniques

> This block sat inside another chapter in the source document with its own "Class" title, and repeats content that appears elsewhere. It is kept here so nothing is lost; review and merge or delete it.


# The Problem That CoT Solves

## Chain-of-Thought

**Chain-of-Thought (CoT)** is a prompt engineering and model reasoning technique where a large language model generates explicit intermediate reasoning steps before producing a final answer. Introduced by Jason Wei and colleagues at Google Research in 2022, it transforms how models handle multi-step math, logic, coding, and decision-making tasks by breaking a hard problem into a sequence of smaller, easier deductions.

### 1. Why Chain-of-Thought Matters

Without CoT, a transformer model must compress every calculation and logical deduction into a single vertical forward pass before outputting its very first answer token. Generating intermediate steps changes that execution loop in three ways:

- **Extra serial compute.** Every generated token triggers a brand-new forward pass through the model's layers, turning a single fixed-depth guess into a multi-step serial algorithm.
- **External working memory.** Writing intermediate results into the text stream lets the model's attention heads read back its own previous steps as a scratchpad, preventing variable loss.
- **Higher-probability transitions.** Instead of making one risky, low-probability leap straight to a final answer, the model takes a sequence of small, high-confidence steps learned from explanations in its pre-training data.

### 2. Main Flavors of Chain-of-Thought

| Variant | How It Works | Best When To Use |
| --- | --- | --- |
| Zero-Shot CoT | Appends a simple trigger phrase like *"Let's think step by step"* with zero worked examples. | Fast prototyping, ad-hoc reasoning, or when you have no labeled examples. |
| Few-Shot CoT | Provides 3–5 hand-crafted (Question → Step-by-Step Reasoning → Answer) examples in the prompt. | Tasks needing strict output formatting, domain-specific rules, or edge-case handling. |
| Dynamic Few-Shot CoT | Uses vector embeddings (k-NN / MMR) at runtime to fetch the closest worked examples per query. | Large, high-variance domains with dozens of schemas, policies, or edge cases. |
| Compiled CoT (DSPy) | Uses automated optimizers (BootstrapFewShot, MIPROv2) to synthesize and tune CoT traces against a metric. | Production pipelines, multi-hop workflows, or distilling prompts onto smaller models. |
| Native Reasoning Models | Models trained via reinforcement learning (e.g., OpenAI o3, DeepSeek-R1, Gemini Thinking) to generate hidden thinking tokens automatically. | Complex coding, math, and planning where manual *"think step by step"* triggers are no longer needed. |

### 3. When to Use CoT vs. Direct Prompting

- **Use Chain-of-Thought** whenever a task requires **2 or more sequential steps**—such as arithmetic word problems, multi-rule policy classification, code debugging, or multi-hop data extraction.
- **Skip Chain-of-Thought** on simple factual lookups, basic translation, or straightforward sentiment checks where extra reasoning tokens add unnecessary latency and API cost without improving accuracy.

## The Problem That CoT Solves

Chain-of-Thought (CoT) solves the single-pass reasoning bottleneck in large language models, where asking a transformer to jump straight from a complex question to a final answer forces it to compress multi-step logic into a single, error-prone guess.

Standard autoregressive models suffer from three structural limitations when answering complex problems directly:

### 1. Fixed Compute Per Token (The Depth Bottleneck)

- **Constant vertical operations.** A transformer has a fixed number of layers. It executes the exact same amount of mathematical operations to generate one easy word as it does to generate the final answer to a hard puzzle.
- **Single-pass compression.** Without CoT, the model must solve every intermediate step inside **one single forward pass** through its layers before emitting its first answer token. If a problem requires four or five logical hops, the signal degrades and the model guesses.

### 2. Lack of Persistent Working Memory

- **No internal scratchpad.** Standard transformers do not have recurrent memory loops to hold intermediate variables safely from one operation to the next.
- **Volatile activations.** Trying to juggle multiple numbers, rules, or state changes purely inside hidden layer activations leads to dropped constraints and arithmetic errors. Writing steps out as text turns the context window into an external memory tape that attention heads can read back on subsequent passes.

### 3. Reliance on Surface-Level Pattern Matching

- **Statistical shortcuts over deduction.** Because LLMs are trained to predict the most probable next token, a direct question prompt pushes the model to retrieve memorized associations or plausible-sounding guesses rather than computing the answer from scratch.
- **Low-probability leaps.** On multi-step problems, the true final answer often has a very low initial probability compared to common wrong guesses. CoT breaks one risky leap into a chain of small, high-probability transitions.

### Direct Prompting vs. Chain-of-Thought

| Limitation | Standard Direct Prompting | How Chain-of-Thought Solves It |
| --- | --- | --- |
| Compute Budget | 1 forward pass to resolve the entire problem. | Dozens of passes (1 per generated token) acting as serial compute. |
| Variable Tracking | Held precariously inside internal activations. | Written explicitly into the context window as an external scratchpad. |
| Prediction Strategy | Jumps straight to a low-probability final token. | Chains together small, heavily memorized, high-confidence steps. |

## Standard Chain-of-Thought

**Standard Chain-of-Thought (Few-Shot CoT)** is the original prompting technique introduced by Jason Wei and colleagues in 2022, where you **provide a small set of hand-crafted worked examples showing the full step-by-step reasoning path before asking the model to solve a new problem**. Unlike Zero-Shot CoT—which relies on a generic trigger phrase like *"Let's think step by step"*—Standard CoT teaches the model *how* to reason through explicit demonstration.

### 1. How Standard CoT Works

Every prompt in Standard CoT follows a strict three-part structure repeated across **3 to 5 examples** (shots):

- **Input (Question:).** A representative problem matching the domain and difficulty of your target task.
- **Reasoning Trace (Reasoning:).** An explicit, line-by-line breakdown of the intermediate logic, rules, or calculations required to solve the problem.
- **Final Output (Answer:).** A clean, standardized conclusion marker that separates the final answer from the scratchpad text.

```text
Question: A store has 40 apples. It sells 15 in the morning and receives a delivery of 24 in the afternoon. How many apples does it have now?
Reasoning:
1. Start with the initial count: 40 apples.
2. Subtract morning sales: 40 - 15 = 25 apples left.
3. Add the afternoon delivery: 25 + 24 = 49 apples.
Answer: 49

Question: [Your target question goes here]
Reasoning:
```

### 2. Why Standard CoT Outperforms Standard Few-Shot Prompting

In traditional Few-Shot prompting, you only provide (Question → Answer) pairs without showing the intermediate work. Standard CoT adds the middle bridge, which creates three major advantages:

- **Controls step granularity.** Your examples demonstrate the exact level of detail you expect, preventing the model from skipping critical arithmetic or policy checks.
- **Enforces strict output formatting.** By repeating identical delimiters (Reasoning: and Answer:), you make it easy to parse the final result reliably in production code.
- **Handles domain-specific rules.** When a task depends on proprietary business logic rather than general common sense, worked examples teach the model how to apply those specific rules step by step.

### 3. Key Limitations to Keep in Mind

- **Manual authoring effort.** Someone must carefully write, verify, and format every reasoning trace by hand.
- **Static coverage limits.** A fixed set of 3 to 5 examples cannot cover dozens of diverse edge cases, which is why complex production systems eventually upgrade to **Dynamic Few-Shot Retrieval** or **DSPy compilation**.

## Step-by-step reasoning and scratchpad patterns

**Step-by-step reasoning and scratchpad patterns** are structured prompt designs that force a large language model to externalize its working memory into explicit text tokens before committing to a final answer. Because transformers lack persistent internal memory loops between token generations, writing intermediate states into the context window creates a readable "RAM tape" that self-attention heads can reference on every subsequent forward pass.

### 1. Core Scratchpad Patterns

Different tasks benefit from specific scratchpad layouts depending on whether you need math precision, rule verification, or clean JSON parsing:

| Pattern Name | Structure / Delimiters | Best Use Case |
| --- | --- | --- |
| Linear Numbered Steps | Step 1: ... Step 2: ... Final Answer: ... | Sequential math word problems, multi-hop QA, and straightforward logic chains. |
| XML Tag Scratchpad | <scratchpad> ... </scratchpad> followed by <answer> ... </answer> | Production pipelines where backend code needs to strip out reasoning text and parse the final output cleanly. |
| State-Tracking Table / Key-Value | Initial State -> Action 1 -> Updated State -> Action 2 -> Final State | Tracking changing variables over time, such as inventory updates, code execution traces, or game states. |
| Rule-Checklist Verification | Rule 1: [Pass/Fail + Evidence] -> Rule 2: [Pass/Fail + Evidence] -> Decision | Policy compliance, moderation, eligibility checks, and multi-criteria classification. |
| JSON Reasoning Field | {"reasoning": "...", "final_answer": "..."} | Structured API outputs (response_format), ensuring the model generates the reasoning key *before* the final_answer key. |

### 2. Why Key Ordering Matters in Scratchpads

- **Left-to-right causality is strict.** Because autoregressive models generate one token at a time from left to right, the scratchpad **must always appear before the final answer**.
- **Putting reasoning last breaks the mechanism.** If you design a JSON schema with {"answer": "...", "reasoning": "..."}, the model has to guess the answer first without any extra compute, and the subsequent reasoning field becomes post-hoc rationalization rather than genuine problem-solving.

### 3. Example: XML Scratchpad for Production Parsing

```text
Analyze whether the user qualifies for a refund based on our 14-day policy.
Put all intermediate checks inside <scratchpad> tags, then put only YES or NO inside <answer> tags.

Input: "I bought these headphones on 1 October and opened the box, but the left ear stopped working on 10 October."

<scratchpad>
1. Purchase date: 1 October.
2. Issue reported date: 10 October.
3. Days elapsed: 10 - 1 = 9 days (within the 14-day window).
4. Condition check: Item is defective, which is covered even if opened.
5. Conclusion: Meets all refund criteria.
</scratchpad>
<answer>YES</answer>
```

### 4. Best Practices for Designing Scratchpads

- **Keep each step atomic.** Write one deduction or calculation per line so the model never tries to execute two operations in a single forward pass.
- **Restate constraints explicitly.** Instructing the model to copy relevant numbers or rules into the scratchpad first prevents attention heads from losing track of them in long input documents.
- **Strip the scratchpad before showing users.** In user-facing applications, parse out the <scratchpad> block on your backend so users get a fast, clean answer while the model still benefits from the extra reasoning compute.

## Self-consistency

**Self-Consistency** is a decoding and ensembling technique introduced by Xuezhi Wang and colleagues in 2022 that improves Chain-of-Thought (CoT) accuracy by generating multiple independent reasoning paths for the same prompt and selecting the most frequent final answer via majority vote. Instead of relying on a single greedy reasoning trace—which might contain an accidental arithmetic slip or logical detour—Self-Consistency marginalizes over diverse thought processes to find the most reliable conclusion.

### 1. How Self-Consistency Works

The pipeline runs in three straightforward stages:

- **1. Sample diverse reasoning paths.** Rather than setting temperature = 0 (which always picks the single highest-probability token), you set a moderate sampling temperature (typically 0.5 to 0.8) and prompt the LLM to generate **k independent CoT responses** (commonly k = 5 to 20) for the exact same input question.
- **2. Extract the final answer from each trace.** Parse the concluding answer (e.g., 42 or YES) from the end of each generated reasoning chain, stripping away the intermediate scratchpad text.
- **3. Take a majority vote.** Count how often each distinct final answer appears across the k samples and return the answer with the highest vote share.

### 2. Why It Works (The Intuition)

- **Multiple valid paths lead to one truth.** Complex reasoning problems can often be solved in several valid ways (for example, solving an algebra problem with equations vs. working backward from numbers). Correct reasoning paths tend to converge on the **exact same final answer**.
- **Errors are uncoordinated.** When an LLM makes a random arithmetic mistake or misreads a constraint during sampling, those errors tend to scatter across different wrong numbers rather than converging on one identical mistake. Majority voting naturally filters out isolated reasoning glitches.

### 3. Greedy CoT vs. Self-Consistency CoT

| Dimension | Single Greedy CoT (temp = 0) | Self-Consistency CoT (k samples, temp > 0) |
| --- | --- | --- |
| Inference Calls | 1 generation per query | k parallel generations per query (typically 5–10) |
| Accuracy on Math / Logic | Strong baseline | Significantly higher (+5% to +15% on benchmarks like GSM8K) |
| Confidence Signal | None (always outputs 1 answer) | Built-in vote share (e.g., 9/10 agreement vs. a 4/10 split) |
| Token Cost & Latency | 1× cost; single-pass latency | k× output token cost; parallelizable latency |
| Best Use Case | Real-time chat, low-cost bulk processing | High-stakes decisions, offline evaluation, synthetic data creation |

### 4. Practical Engineering Optimizations

- **Use vote consensus as a confidence score.** If 10 out of 10 sampled chains agree on Approved, your system can auto-execute with high confidence. If the vote splits 5 vs. 5, you can automatically flag the item for human review or escalate it to a stronger model.
- **Adaptive sampling (Early Stopping).** You do not always need to run all 10 samples. Start by generating 3 chains; if all 3 produce the exact same final answer, stop immediately and return it—saving up to 70% of your token cost on easy queries while spending full compute only on ambiguous ones.
- **Requires a discrete, canonical answer.** Self-Consistency works best when final answers can be cleanly normalized and compared (such as numbers, multiple-choice letters, boolean flags, or standardized labels), rather than free-form essays.

## Multiple reasoning paths and majority voting

**Multiple reasoning paths and majority voting** are the two core mechanisms that power Self-Consistency in Chain-of-Thought prompting, transforming an LLM from a single fragile solver into an **ensemble of independent reasoners** that converge on the most reliable answer.

### 1. Generating Multiple Reasoning Paths (Diverse Sampling)

- **Why greedy decoding fails.** When you run a prompt with temperature = 0, the model deterministically picks the highest-probability next token at every step. If it makes a single early misstep—like misreading a constraint or slipping on arithmetic—the entire chain derails with no second chance.
- **Exploring alternative solution strategies.** By increasing sampling temperature (typically 0.5 to 0.8) and generating **5 to 20 independent completions** in parallel, the model explores genuinely different ways to solve the same problem—such as algebraic substitution in Path A, working backward in Path B, and breaking numbers into parts in Path C.
- **Uncorrelated failure modes.** While valid reasoning approaches naturally converge on the same truth, random hallucinations and arithmetic slips tend to scatter across different wrong numbers rather than repeating the exact same error.

### 2. Majority Voting (Marginalizing Over Thoughts)

- **Answer extraction and normalization.** Once all candidate traces finish generating, a parser extracts only the final answer from each trace and normalizes formatting differences (e.g., treating ₹500, 500, and 500.00 as identical).
- **Tallying the consensus.** The system counts votes across all extracted final answers and selects the winner with the highest frequency—effectively marginalizing out the intermediate reasoning text to find the answer with the highest aggregate probability across all paths.

text

```text
Prompt: "A train travels 120 km in 1.5 hours, then 180 km in 2.5 hours. What is the average speed?"

├── Path 1 (Direct sum): Total dist = 300 km, total time = 4 hrs → 300 / 4 = 75 km/h
├── Path 2 (Weighted avg): (80 × 1.5 + 72 × 2.5) / 4 = (120 + 180) / 4 = 75 km/h
├── Path 3 (Arithmetic slip): Total dist = 300 km, total time = 3 hrs → 300 / 3 = 100 km/h
├── Path 4 (Step-by-step): 120 + 180 = 300; 1.5 + 2.5 = 4.0; 300 ÷ 4 = 75 km/h
└── Path 5 (Unit conversion): 300,000 m / 14,400 s = 20.83 m/s × 3.6 = 75 km/h

Majority Vote Tally:
• 75 km/h → 4 votes (80% consensus) ✅ Winner
• 100 km/h → 1 vote (20% noise)
```

### 3. Engineering Enhancements Beyond Basic Voting

| Technique | How It Improves Basic Majority Voting | Best When To Use |
| --- | --- | --- |
| Adaptive Early Stopping | Samples 3 paths first; if all 3 agree, stops immediately instead of running all 10. | Production APIs looking to cut token costs by 50–70% on easy queries. |
| Confidence-Weighted Voting | Weights each path's vote by the model's average token log-probabilities or reasoning length. | Tie-breaking when small sample sizes (e.g., k = 4) produce a 2 vs. 2 split. |
| Verifier / Reward Scoring (Best-of-N) | Replaces raw frequency counts with a separate reward model or code execution test to pick the best trace. | Code generation, SQL queries, or open-ended answers where exact string matching fails. |
| Consensus Escalation | Routes queries with low vote agreement (e.g., < 60%) to a stronger model or human reviewer. | High-stakes financial, legal, or medical classification workflows. |

## Tree of Thought

**Tree of Thoughts (ToT)** is a deliberate problem-solving framework introduced by Shunyu Yao and colleagues in 2023 that generalizes Chain-of-Thought by allowing a language model to explore multiple branching reasoning paths, evaluate intermediate progress, and backtrack when a path hits a dead end. Instead of generating a single linear sequence of tokens from start to finish, ToT structures reasoning as a search tree over coherent "thoughts."

### 1. Why Linear CoT Hits a Wall

In standard Chain-of-Thought or Self-Consistency, the model generates tokens strictly left-to-right without ever looking back or revising an early decision. If the model chooses a bad strategy at Step 1 of a complex puzzle, planning task, or code architecture problem, it is stuck carrying that flawed premise all the way to the end.

Tree of Thoughts fixes this by letting the model **look ahead and backtrack** just like a human solving a chess position or a crossword puzzle.

### 2. How Tree of Thoughts Works (The 4 Components)

ToT wraps an LLM inside a classical search algorithm using four modular steps:

- **1. Thought Decomposition.** Break the problem into discrete intermediate steps ("thoughts")—such as one equation in a math puzzle, one paragraph outline in creative writing, or one move in a game—rather than individual tokens.
- **2. Thought Generator.** At the current node in the tree, prompt the LLM to propose **k distinct candidate next steps** (either by sampling multiple completions or prompting the model to list 3 different options).
- **3. State Evaluator.** Prompt the LLM (or use a programmatic rule) to score each candidate branch—for example, rating branches as **sure**, **maybe**, or **impossible**, or assigning a numerical score from 1 to 10 based on how close the state is to a valid solution.
- **4. Search Algorithm.** Use **Breadth-First Search (BFS)** (keeping the top b most promising branches at every depth level) or **Depth-First Search (DFS)** (exploring one promising branch deeply and backtracking immediately if the evaluator marks it impossible).

### CoT vs. Self-Consistency vs. Tree of Thoughts

| Feature | Standard CoT | Self-Consistency CoT | Tree of Thoughts (ToT) |
| --- | --- | --- | --- |
| Reasoning Structure | Single linear chain | Multiple independent full chains | Branching tree with intermediate evaluation |
| Error Recovery | None; commits to early mistakes | Discards bad chains only *after* completion | **Prunes dead ends mid-way and backtracks** |
| Decision Mechanism | Greedy next-token prediction | Majority vote at the very end | Step-by-step lookahead scoring (BFS / DFS) |
| Token Cost & Latency | Lowest (1× pass) | Moderate (k× full passes) | Highest (dozens of generator + evaluator calls) |
| Best Use Cases | Standard math, QA, classification | Arithmetic & logic with clear final answers | Planning, puzzles (Game of 24), constraint satisfaction, complex coding |

### 4. Practical Trade-Offs and When to Use ToT

- **Massive accuracy boost on search problems.** On tasks requiring combinatorial search and backtracking—such as the *Game of 24* puzzle—standard CoT solves roughly **4%** of problems, whereas Tree of Thoughts solves **74%**.
- **High inference cost.** Because every node in the tree requires multiple LLM calls to generate and evaluate branches, ToT can consume **10× to 100× more tokens** than a single CoT prompt.
- **When to reach for it.** Reserve ToT for high-value, offline, or complex planning workflows where **early mistakes ruin the entire output** (such as multi-step code refactoring, formal constraint satisfaction, or strategic planning) and where extra latency is acceptable.

## Branching exploration for planning problems

**Branching exploration for planning problems** is the core superpower of Tree of Thoughts (ToT), allowing an LLM to treat multi-step planning—such as scheduling, logistics routing, code architecture, or game playing—as a deliberate search tree rather than a single irreversible guess.

### 1. Why Linear CoT Fails at Planning

In a planning problem, early choices restrict future options (for example, booking a morning flight determines which afternoon meetings are possible). Standard Chain-of-Thought commits to the very first plausible action it generates and marches forward linearly. If it hits a constraint violation four steps later, it cannot undo Step 1—forcing it to either hallucinate a broken plan or fail.

### 2. How Branching Exploration Solves Planning

Instead of committing to a single timeline, a branching planner wraps the LLM in a **generate → evaluate → search** loop at every decision milestone:

- **1. Action / State Proposal (Branching).** At the current plan state, you prompt the LLM to propose **k distinct next moves** (e.g., *"Give 3 fundamentally different ways to schedule the next 2 tasks without violating resource limits"*).
- **2. Constraint & Progress Evaluation (Lookahead).** Before expanding any further, an evaluator (either a second LLM prompt or a deterministic Python constraint checker) scores each proposed branch on **feasibility** (did it break any hard rules?) and **progress** (how close does this move bring us to the final goal?).
- **3. Pruning & Backtracking (Search Control).**
  - **Breadth-First / Beam Search:** Keep only the top b highest-scoring partial plans at each step (e.g., keeping the best 2 schedules at Hour 1, expanding each into 3 options at Hour 2, and pruning the rest).
  - **Depth-First Search with Backtracking:** Follow the single highest-scoring branch all the way down; the moment a constraint fails (score = 0 or impossible), discard that branch, step back up one node, and try the next best sibling option.

### 3. Concrete Example: Multi-Constraint Event Scheduling

Suppose you need to schedule 3 workshops (A, B, C) across 3 time slots (9 AM, 11 AM, 2 PM) with strict constraints (e.g., *"Workshop A cannot be at 9 AM"* and *"Workshop B must happen before C"*):

## Reflection and self-critique

**Reflection and self-critique** (often called **Self-Refine** or **Reflexion**) is an iterative prompting pattern where a language model generates an initial draft, explicitly critiques its own output for errors or missing constraints, and then uses that critique to produce an improved revision. Unlike standard Chain-of-Thought—which reasons *before* producing an answer—reflection adds a feedback loop *after* generation so the model can catch mistakes that only become visible once a full solution is written down.

### 1. Why Models Spot Errors Better Than They Avoid Them

- **Generation vs. verification asymmetry.** For an LLM, verifying whether a written answer violates a rule or contains a bug is significantly easier than generating a flawless answer on the first pass.
- **Shifting attention to the finished output.** During initial generation, attention heads focus on forward completion. During a dedicated critique pass, the complete draft sits inside the context window, allowing the model to audit the full text against constraints line by line.

### 2. The Three-Stage Reflection Loop

Most reflection architectures follow a clean **Draft → Critique → Revise** cycle (typically run for 1 to 3 iterations):

- **1. Generate (Initial Draft).** The model solves the problem using standard or Chain-of-Thought prompting to produce Output v1.
- **2. Critique (Self-Evaluation).** A second prompt feeds both the original requirements and Output v1 back into the model, instructing it to act as a strict reviewer and list specific factual errors, edge-case failures, or formatting violations.
- **3. Refine (Targeted Revision).** A third prompt provides the original query, Output v1, and the structured critique, asking the model to rewrite the solution while fixing every identified flaw to produce Output v2.

### 3. Key Variants in Practice

| Pattern | How It Works | Best When To Use |
| --- | --- | --- |
| Single-Pass Self-Check | Prompts the model inside one response: *"Write your answer, then verify every constraint and provide a corrected final version."* | Low-latency chat apps where a lightweight sanity check is enough. |
| Self-Refine (Iterative Loop) | Separates generation, critique, and revision into distinct API calls across 2–3 rounds. | Complex writing, policy compliance, SQL queries, and multi-constraint planning. |
| Reflexion (Environment-Grounded) | Feeds real external signals—such as **Python unit test tracebacks, compiler errors, or linter outputs**—into the critique step instead of relying purely on LLM self-judgment. | Code generation, math verification, and tool-using agents. |

### 4. Critical Pitfalls to Avoid

- **Sycophantic "hallucinated" critiques.** If you ask an LLM *"What is wrong with your answer?"* when the answer is actually right, it may invent fake flaws and ruin a correct response. Always give the critique step an explicit exit option (e.g., *"If all constraints are met, output NO_ISSUES"*).
- **Blind leading the blind.** Without external grounding (like code execution, search, or a strict rule checklist), a weak model often fails to catch its own subtle factual hallucinations. Pairing reflection with **deterministic checks** or a **stronger critic model** yields far higher gains than pure self-critique alone.

When a model **reviews its own output**, it decouples the cognitive load of creation from the task of verification. Because autoregressive models generate text one token at a time, they often commit to a flawed direction early on; allowing the model to pause and inspect the completed draft lets its attention heads evaluate the entire output against constraints as a whole.

### 1. Why Self-Review Works Mechanically

- **Verification is easier than generation.** Checking whether a finished SQL query has a syntax error or whether a summary misses a required date requires simple pattern matching across existing context, whereas generating a flawless response from scratch requires predicting every dependency sequentially.
- **Full-draft visibility.** During initial generation, the model cannot "see" future tokens it hasn't written yet. During a review pass, the entire completed response sits inside the context window, allowing attention heads to cross-reference the ending against the opening prompt.

### 2. Three Ways to Structure a Model Self-Review

| Pattern | How It Executes | Best When To Use |
| --- | --- | --- |
| In-Context Self-Check (Single Call) | Instructs the model inside one prompt to write a draft, audit it against a checklist, and output a final corrected version. | Low-latency applications where a fast sanity check is enough without extra API round-trips. |
| Multi-Turn Critic Loop (Self-Refine) | Runs a separate API call where the model acts strictly as a hostile auditor, outputting structured critique notes that feed into a third revision call. | Complex writing, policy compliance, structured extraction, and multi-constraint planning. |
| Tool-Grounded Review (Reflexion) | Executes the model's output against a deterministic environment (such as a Python interpreter, SQL engine, or JSON schema validator) and feeds the real error traceback back to the model for self-correction. | Code generation, math calculation, and API tool-calling workflows. |

### 3. Essential Guardrails for Reliable Self-Review

- **Give an explicit "Pass" exit condition.** If you force a model to critique a draft that is already 100% correct, it will often hallucinate fake flaws just to satisfy your instruction. Always include a rule like: *"If every requirement is satisfied, respond only with PASS and do not alter the output."*
- **Use a concrete rubric instead of vague instructions.** Asking *"Is this good?"* produces generic, unhelpful feedback. Instead, provide a numbered verification checklist (e.g., *"1. Check that all dates are in DD-MM-YYYY format. 2. Verify no external assumptions were added."*).
- **Separate the persona or model.** In multi-turn setups, clearing the initial generation conversation and passing only (Original Constraints + Draft Output) into a fresh critic prompt prevents the model from feeling biased to defend its own previous phrasing.

### 4. Example: Rubric-Based Self-Review Prompt

```text
Review the draft response below against the user's original constraints.
Constraints:
1. Must be under 100 words.
2. Must explicitly mention the 14-day return window.
3. Must maintain a polite, neutral tone.

Draft Output:
[Insert Model Draft Here]

Instructions:
Audit each constraint line by line. If all 3 constraints pass, output "STATUS: PASS".
If any constraint fails, list the exact failure and write a corrected version.
```

## Choosing the right technique for a given problem

Choosing the right reasoning technique depends on matching how a problem fails to the specific mechanism that fixes it, while respecting your latency and token budgets. Rather than defaulting to the most complex pattern, pick the simplest method that solves your core failure mode.

### 1. Problem-to-Technique Mapping Matrix

| Problem Type & Failure Mode | Recommended Technique | Why It Fits | Compute & Latency Cost |
| --- | --- | --- | --- |
| Simple factual lookup or basic translation (No multi-step logic) | **Direct Zero-Shot Prompting** | Extra reasoning tokens add latency without improving accuracy. | **1×** (Lowest) |
| Multi-step arithmetic, logic, or ad-hoc reasoning (Single-pass compression errors) | **Zero-Shot CoT** (*"Let's think step by step"*) | Buys extra sequential forward passes and an external scratchpad with zero setup effort. | **Low** (1 call, more output tokens) |
| Strict output formatting or proprietary business rules (Model skips steps or uses wrong labels) | **Static Few-Shot CoT** (3–5 worked examples) | Programs exact step granularity, edge-case handling, and consistent delimiters while keeping 100% prefix caching. | **Low** (1 call, fixed prompt prefix) |
| High-variance domains with 50+ schemas or policies (Static examples miss relevant rules) | **Dynamic Few-Shot Retrieval** (k-NN / MMR) | Fetches only the 3–5 closest worked examples per query at runtime without bloating context length. | **Low–Moderate** (Vector search + 1 LLM call) |
| High-stakes math/logic with occasional random slips (Single greedy path makes unforced errors) | **Self-Consistency** (Multiple paths + majority vote) | Samples k independent chains and uses consensus voting to filter out isolated calculation mistakes. | **Moderate–High** (k× output tokens) |
| Combinatorial planning, puzzles, or early dead-ends (One bad early choice ruins the entire plan) | **Tree of Thoughts (ToT)** (Branching + lookahead + backtracking) | Evaluates intermediate states and prunes dead ends mid-way instead of committing linearly. | **High** (10×–100× LLM calls) |
| Complex writing, code generation, or strict constraint compliance (Easier to spot flaws than prevent them) | **Reflection / Reflexion** (Draft → Critique → Revise) | Separates creation from verification, especially when grounded by deterministic tools like unit tests or linters. | **Moderate** (2–3 sequential calls) |
| Multi-hop production pipelines or distilling to smaller models (Manual tuning hits a ceiling) | **Compiled Pipelines (DSPy)** (BootstrapFewShot / MIPROv2) | Replaces fragile manual strings with programmatic optimization against a quantitative validation metric. | **High offline build; Low runtime** |

### 2. Four-Step Selection Rule of Thumb

- **Step 1: Check if you are using a native reasoning model.** If you are calling a dedicated thinking model (such as OpenAI o3, DeepSeek-R1, or Gemini Thinking), skip manual Zero-Shot CoT triggers—internal reinforcement-learned reasoning is already built in. Focus instead on clear constraints, schemas, and tool grounding.
- **Step 2: Start linear before branching.** Always test **Zero-Shot CoT** or **Static Few-Shot CoT** first. Only escalate to **Self-Consistency** or **Tree of Thoughts** when evaluation logs prove that single linear chains fail on your task.
- **Step 3: Add deterministic verification wherever possible.** For code, SQL, math, or strict JSON, pairing a lightweight **Reflection loop** with a Python interpreter or schema validator beats pure LLM self-critique every time.
- **Step 4: Automate once you have 50+ labeled examples.** When hand-tuning turns into prompt whack-a-mole across a multi-step pipeline, move to **DSPy** to compile and maintain your prompts systematically.

## Connection back to reasoning models (Class 3: o1/o3/Claude Extended Thinking)

**Native reasoning models** (such as OpenAI **o1/o3**, **Claude Extended Thinking**, **DeepSeek-R1**, and **Gemini Thinking**) represent the architectural evolution of everything we have covered: they take external prompt-engineering patterns—Chain-of-Thought, Tree-of-Thoughts backtracking, and Reflection—and bake them directly into the model's weights via Reinforcement Learning (RL).

Instead of relying on a human to write *"Let's think step by step"* or orchestrate external Python search loops, these models learn to generate hidden **thinking tokens** autonomously before emitting a final response.

### 1. How Reasoning Models Internalize Prompting Techniques

| External Prompting Technique (Class 1 & 2 Models) | How Class 3 Reasoning Models Do It Natively |
| --- | --- |
| Zero-Shot / Few-Shot CoT (*"Think step by step"*) | **Built-in <think> block.** Trained via RL to always allocate test-time compute to an internal scratchpad before answering. |
| Tree of Thoughts (ToT) (External BFS/DFS search) | **In-context branching.** The model naturally writes *"Wait, let's test another approach..."* inside its thinking trace, exploring multiple branches in one continuous pass. |
| Reflection & Self-Critique (Multi-turn Draft → Critique loops) | **Continuous self-verification.** Models learn emergent habits like *"Hold on, let me double-check that constraint"* mid-thought without needing a separate critic API call. |
| Self-Consistency (Sampling k paths externally) | **Adaptive thinking budgets.** Instead of manually running 10 calls, you adjust a single reasoning_effort or thinking_budget parameter to let the model think longer on hard problems. |

### 2. Why Reinforcement Learning Replaces Manual Triggers

- **Outcome-based RL over imitation.** Standard LLMs learn CoT by imitating human-written explanations in their pre-training data. Reasoning models are trained with large-scale reinforcement learning (such as GRPO) on verifiable math, coding, and logic tasks—rewarding the model solely for getting the **right final answer**, regardless of how messy its internal scratchpad looks.
- **Emergent cognitive behaviors.** Because longer, self-correcting thought chains earn higher rewards on hard problems, the model spontaneously develops human-like problem-solving habits: breaking down sub-goals, spotting dead ends, backtracking, and verifying edge cases entirely on its own.

### 3. How Your Prompting Strategy Must Change for Class 3 Models

When working with o3, Claude Extended Thinking, or DeepSeek-R1, classic prompt-engineering rules actually invert:

- **Stop writing** ***"Let's think step by step."*** **Adding manual CoT triggers or rigid step-by-step templates is redundant and can actually degrade performance** by forcing the model into a cramped, unnatural reasoning groove instead of letting its RL-trained search policy work freely.
- **Drop verbose Few-Shot CoT reasoning traces.** You rarely need to hand-write long step-by-step demonstrations anymore. If you provide examples, keep them minimal—showing only the desired **input-output format** rather than dictating *how* to think.
- **Shift focus to crisp specifications and constraints.** Because the model handles the *how*, your prompt should focus 100% on the *what*: clear problem boundaries, unambiguous success criteria, edge-case definitions, and strict output schemas.
- **Keep DSPy for multi-step systems and verification.** Even with Class 3 models, frameworks like **DSPy** remain valuable—not for injecting *"think step by step"* triggers, but for **orchestrating multi-hop tool pipelines**, managing dynamic retrieval (KNNFewShot), and optimizing system-level prompts against business metrics.

### Summary: The Evolution of Test-Time Compute

1. **Standard Prompting:** 1 pass, zero scratchpad (relies purely on memorized weights).
2. **Prompted CoT / ToT / Reflection:** Humans externally scaffold step-by-step compute using text triggers and Python loops.
3. **Class 3 Reasoning Models:** The model natively scales **test-time compute** inside an internal RL-trained thinking loop—turning prompt engineering from *"teaching the model how to think"* into *"clearly specifying what problem to solve."*
