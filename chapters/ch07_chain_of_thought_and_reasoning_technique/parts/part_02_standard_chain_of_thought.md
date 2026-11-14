# Chapter 7 - Part 2: Standard Chain-of-Thought

> Chapter 7: Chain-of-Thought and Reasoning Techniques

**Standard Chain-of-Thought (CoT)**—originally introduced as **Few-Shot CoT** by Wei et al. (2022)—is a prompting technique where you provide a Large Language Model (LLM) with step-by-step reasoning demonstrations inside the prompt before asking your target question.

Unlike Zero-Shot CoT (which relies on a generic trigger phrase like *"Let's think step by step"*), Standard CoT explicitly teaches the model **how** to decompose a problem, what format to use, and what level of granularity to follow.

## How It Works

You construct a prompt containing 2 to 8 manually written examples formatted as:

## [Input Question] -> [Step-by-Step Reasoning Trace] -> [Final Answer]

When the model sees your actual question at the end of the prompt, its in-context learning mechanism mimics both the **logical structure** and the **output format** of your examples.

## Example Comparison

| Approach | Prompt Structure |
| --- | --- |
| Standard Few-Shot | **Q:** Roger has 5 balls. He buys 2 cans of 3 balls each. How many does he have?   **A:** 11.   **Q:** A cafeteria had 23 apples. They used 20 and bought 6 more. How many do they have?   **A:** |
| Standard CoT (Few-Shot CoT) | **Q:** Roger has 5 balls. He buys 2 cans of 3 balls each. How many does he have?   **A:** Roger started with 5 balls. 2 cans of 3 balls each is 6 balls. 5 + 6 = 11. **The answer is 11.**   **Q:** A cafeteria had 23 apples. They used 20 and bought 6 more. How many do they have?   **A:** |

## Key Strengths vs. Limitations

- **Controlled Reasoning Style:** You dictate the exact logic pattern (e.g., checking edge cases, applying specific business rules, or extracting variables first) rather than leaving the reasoning structure up to chance.
- **Consistent Output Parsing:** By ending every demonstration with a standardized anchor phrase (like The answer is X or a JSON block), downstream code can reliably extract the final prediction.
- **Higher Accuracy on Domain Tasks:** Outperforms Zero-Shot CoT on specialized workflows (like legal analysis, medical triage, or custom rule evaluation) where generic reasoning fails.
- **High Authoring Cost:** Requires manually writing clean, accurate reasoning traces for every example, which does not scale easily across dozens of different tasks.
- **Brittle to Distribution Shift:** If your test question requires 6 reasoning steps but all your few-shot demonstrations only show 2 steps, the model may prematurely stop reasoning after 2 steps.

## Standard CoT - step-by-step reasoning and scratchpad patterns

**Standard Chain-of-Thought (CoT)** relies on structured scratchpad patterns inside few-shot demonstrations to guide how a model decomposes problems, tracks intermediate states, and formats its final output.

Rather than letting an LLM generate unstructured prose, well-designed Standard CoT prompts establish repeatable mental templates that prevent skipped steps and state-tracking errors.

### 1. Core Scratchpad Patterns in Standard CoT

Depending on the type of reasoning required, prompt engineers structure the intermediate CoT trace using four distinct patterns:

- **Linear Decomposition (Math & Multi-Step Logic):** Breaks a word problem into sequential equations where the output of step N becomes the input for step N+1.
  - *Pattern:* Identify given variables -> Compute intermediate quantity -> Combine with remaining variable -> State final result.
- **State-Tracking Scratchpads (Symbolic & Rule Simulation):** Explicitly prints the updated state of variables after every action or rule trigger so the model never relies on implicit memory.
  - *Pattern:* Initial state: [A=1, B=0] -> Action 1 modifies A -> Current state: [A=0, B=0] -> Final state check.
- **Evidence-Then-Verdict (Classification & Policy Triage):** Forces the model to quote relevant facts and evaluate criteria *before* committing to a label, preventing premature classification bias.
  - *Pattern:* Extract relevant facts -> Map facts against policy rules -> Weigh exceptions -> Output category.
- **Plan-and-Execute / Sub-Questioning (Complex Retrieval & QA):** Splits a broad question into self-answered sub-questions before synthesizing the final response.
  - *Pattern:* Sub-question 1 -> Answer 1 -> Sub-question 2 -> Answer 2 -> Final synthesis.

### 2. Anatomy of an Effective CoT Demonstration

To make Standard CoT reliable in production, every few-shot example in your prompt should follow strict structural rules:

- **Explicit Variable Binding:** Name intermediate values clearly (e.g., *"Total cost before tax = $40"* rather than just *"20 + 20 = 40"*) so self-attention can easily reference them later.
- **Atomic Steps:** Keep each sentence or bullet limited to a single logical operation. Combining two calculations into one step re-introduces the single-pass bottleneck.
- **Isolated Scratchpad Delimiters:** Wrap the reasoning trace in clear tags (such as <thinking>...</thinking> or Reasoning: ...) so your application parser can strip out the scratchpad and extract only the clean final answer.
- **Deterministic Answer Anchor:** End every demonstration with an identical concluding phrase (e.g., Final Answer: [X]) to stabilize output parsing.

### 3. Pattern Comparison

| Scratchpad Pattern | Best Used For | Key Failure Mode Prevented |
| --- | --- | --- |
| Linear Decomposition | Arithmetic, financial math, unit conversions | Jumping directly to an estimated number |
| State-Tracking | Code execution, games, workflow validation | Losing track of flipped booleans or updated values |
| Evidence-Then-Verdict | Support routing, content moderation, grading | Anchor bias from the first few words of the input |
| Sub-Questioning | Multi-hop QA, comparing multiple documents | Blending facts from two different entities |
