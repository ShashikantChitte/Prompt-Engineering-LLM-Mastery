# Chapter 7 - Part 3: Self-Consistency

> Chapter 7: Chain-of-Thought and Reasoning Techniques

**Self-Consistency** is a decoding strategy introduced by Wang et al. (2022) that improves Chain-of-Thought (CoT) reasoning by generating multiple diverse reasoning paths for the same prompt and selecting the most frequent final answer via majority vote.

Instead of relying on a single greedy decoding pass—where one early arithmetic slip or logic hallucination ruins the entire output—Self-Consistency treats reasoning like a consensus problem across multiple independent attempts.

### 1. How Self-Consistency Works

The technique replaces standard greedy decoding (temperature = 0) with a three-step pipeline:

1. **Sample Diverse Reasoning Paths:** Query the model N times (typically N = 5 to 40) using the exact same CoT prompt with a non-zero temperature (e.g., temperature = 0.5 to 0.8) so the model explores different ways to solve the problem.
2. **Extract Final Answers:** Strip away the intermediate scratchpad text from each of the N outputs to isolate the final prediction (such as a number, boolean, or category label).
3. **Marginalize via Majority Vote:** Count the frequency of each unique final answer across all N paths and return the answer with the highest vote count.

### 2. Why It Improves Accuracy

- **Corrects Random Reasoning Errors:** Individual CoT traces often fail due to stochastic sampling noise, sign errors, or skipped steps. Because there are many ways to make a mistake on a complex problem—but usually only one or two valid logical paths—wrong answers scatter across different values while correct reasoning paths converge on the same final answer.
- **Approximates Marginalization:** Mathematically, complex problems often have multiple valid reasoning chains leading to the same conclusion. Self-Consistency marginalizes over the latent reasoning variables rather than trusting the single highest-probability token sequence.
- **Built-In Confidence Signal:** The agreement ratio (e.g., 9/10 paths agreeing vs. a 4/3/3 split) serves as a reliable, calibrated confidence score for routing uncertain predictions to human review.

### 3. Trade-Offs and Limitations

| Dimension | Standard CoT (Greedy) | Self-Consistency CoT |
| --- | --- | --- |
| Accuracy on Reasoning | Baseline CoT performance | Significant boost (+5% to +18% on math/logic benchmarks) |
| Token Cost | **1x** inference cost | **Nx** output token cost (scales linearly with sample count) |
| Latency | Sequential generation time | Same wall-clock latency *if* all N samples run in parallel |
| Supported Output Types | Open-ended text, code, or discrete labels | Best suited for **discrete, aggregatable answers** (numbers, MCQs, categories) |

## Practical Optimization: Adaptive Self-Consistency

To avoid paying the full Nx token cost on easy inputs, production systems use **early stopping** (Adaptive Consistency): generate 3 samples first, and if all 3 agree on the exact same answer, return immediately without generating the remaining samples.

## Self-consistency - multiple reasoning paths and majority voting

**Self-Consistency** relies on a two-part mechanism—**sampling diverse reasoning paths and aggregating answers via majority voting**—to turn single-pass Chain-of-Thought (CoT) into a reliable ensemble method.

### 1. Generating Multiple Reasoning Paths (The Exploration Phase)

In standard greedy decoding (temperature = 0), a model commits to a single deterministic token trajectory; if it makes an arithmetic slip or misreads a constraint early on, the rest of the trace builds on that error. Self-Consistency fixes this by introducing controlled randomness:

- **Non-Zero Sampling Parameters:** You sample k independent completions (commonly k = 5 to 40) using temperature sampling (T = 0.5 to 0.8) or nucleus sampling (top_p = 0.9 to 0.95).
- **Diverse Decomposition Strategies:** Because different tokens are sampled at decision points, the model explores distinct ways to break down the problem—for instance, solving an algebra problem via equations in Path 1, working backward from options in Path 2, and estimating step-by-step in Path 3.
- **Prompt & Order Perturbation (Optional):** Advanced implementations also shuffle the order of few-shot examples across the k calls to eliminate positional bias.

### 2. Majority Voting (The Aggregation Phase)

Once all k reasoning paths finish generating, the system discards the intermediate scratchpad text and compares only the final extracted answers:

- **Why Correct Answers Converge:** Complex reasoning problems typically have only one true answer, which can be reached through several valid logical routes. Conversely, hallucinations and calculation mistakes tend to scatter randomly across many different wrong numbers or labels.
- **Answer Normalization:** Before counting votes, outputs must be canonicalized (e.g., converting "$12.00", "12 dollars", and "12" into the unified value 12) so equivalent answers do not split their votes.
- **Weighted Voting Variations:** Instead of treating every path equally, some implementations weight each vote by the token log-probabilities of its reasoning trace or penalize excessively long, rambling chains.

## Concrete Walkthrough Example

Suppose you ask a model a multi-step math question with k = 5 sampled CoT paths:

| Sampled Path | Reasoning Summary | Extracted Final Answer |
| --- | --- | --- |
| Path 1 | Calculates base cost correctly, applies discount properly. | 42 |
| Path 2 | Makes an addition error in step 2 (15 + 18 = 35). | 44 |
| Path 3 | Uses a different grouping order, arrives at the right sum. | 42 |
| Path 4 | Misreads a constraint ("twice as many") as half. | 21 |
| Path 5 | Converts units first, then multiplies cleanly. | 42 |

- Vote Tally: 42 (3 votes), 44 (1 vote), 21 (1 vote).
- Final Output: 42 (60% consensus), filtering out the two independent mistakes.

## Key Design Considerations

- **Diminishing Returns Curve:** Accuracy climbs sharply between k = 1 and k = 10, then flattens out significantly beyond k = 20 to 40.
- **Temperature Calibration:** If temperature is too low (< 0.3), all k paths collapse into the exact same reasoning chain and repeat the same error. If temperature is too high (> 1.0), paths become incoherent and noisy.
