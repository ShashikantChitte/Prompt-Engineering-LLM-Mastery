# Chapter 6 - Part 2: Designing Few-Shot Examples

> Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)

Designing effective **Few-Shot Chain-of-Thought (CoT) examples** means giving the model 3 to 5 clear, diverse, and structurally consistent worked examples that show *how* to solve a problem before asking it to tackle your actual query. Unlike Zero-Shot CoT—which relies on a generic trigger phrase—Few-Shot CoT programs the model's exact reasoning format, granularity, and output style through in-context learning.

### 1. Core Principles for High-Performing Examples

- **Match the target complexity.** Your examples should be at least as hard as the actual problems you want the model to solve. If your examples only show two-step logic, the model may cut corners on a five-step query.
- **Keep step granularity atomic.** Each sentence or line in your reasoning trace should perform just one simple logical or arithmetic operation. Combining multiple deductions into a single dense sentence defeats the purpose of giving the model extra forward passes.
- **Standardize structural delimiters.** Use identical markers across every example—such as Question:, Reasoning:, and Answer:—and end every reasoning chain with a consistent anchor phrase like Therefore, the final answer is:. Consistent formatting makes it effortless to parse the final output programmatically.
- **Include edge cases and negative examples.** If your task involves classification or rule-checking, show at least one example where a condition *fails* or an exception applies so the model learns how to reject false positives.

### 2. Choosing and Ordering Your Examples

- **Prioritize diversity over repetition.** Cover different sub-types of your problem rather than repeating the exact same pattern. For instance, in word problems, include one example with subtraction, one with percentages, and one with a unit conversion.
- **Use semantic similarity for dynamic retrieval.** If you have a large pool of solved examples, selecting the 3 to 5 examples closest in topic or structure to the user's current question significantly boosts accuracy compared to using a static prompt.
- **Place the strongest example last.** Language models exhibit strong recency bias in their context window. Putting your cleanest, most representative example immediately before the target question anchors the model's formatting and tone.

### 3. Anatomy of a Well-Designed Few-Shot CoT Prompt

```text
Question: A bakery makes 48 muffins in the morning. They sell 75% of them by noon, then bake 20 more in the afternoon. How many muffins do they have now?
Reasoning:
1. Start with the morning batch: 48 muffins.
2. Calculate 75% sold by noon: 48 × 0.75 = 36 muffins sold.
3. Subtract sold muffins from the initial batch: 48 - 36 = 12 muffins left.
4. Add the afternoon batch: 12 + 20 = 32 muffins.
Therefore, the final answer is: 32

Question: [Insert your target question here]
Reasoning:
```

### 4. Common Pitfalls to Avoid

- **Skipping "obvious" steps.** Human writers often jump over basic arithmetic or implicit assumptions because they feel trivial. If you skip a step in your examples, the model will learn to skip similar steps and make silent errors.
- **Overloading the context window.** Adding 15 or 20 examples rarely beats 4 to 5 well-crafted ones and increases token costs, latency, and the risk of distracting attention heads.
- **Inconsistent label formats.** Mixing Answer: Yes in one example with Answer: True in another introduces unnecessary noise into the final token prediction.

## Selection criteria: what makes a good example

A good Few-Shot CoT example acts as a clear blueprint that is structurally consistent, properly matched in difficulty, and covers diverse edge cases without skipping intermediate steps. Rather than just showing a correct answer, a strong example teaches the model the exact level of analytical rigor and output formatting required to solve unseen queries reliably.

### 1. Structural & Reasoning Quality

- **Atomic step granularity.** Each line or bullet in the reasoning trace should execute exactly one logical deduction, rule check, or calculation. Merging two operations into one sentence forces the model to compress compute and increases error rates.
- **Zero skipped assumptions.** Good examples explicitly state intermediate values and implicit rules—such as unit conversions or default conditions—rather than jumping ahead the way human experts naturally do.
- **Strict template symmetry.** Every selected example must follow identical delimiters, tone, and conclusion markers (e.g., Input:, Step-by-Step Analysis:, Final Output:). Any formatting drift across examples introduces noise into the model's next-token predictions.

### 2. Difficulty & Complexity Calibration

- **Equal or higher reasoning depth.** Select examples that require at least as many sequential steps as your hardest expected test queries. Research on *Complexity-Based Prompting* shows that prompts with longer, multi-step reasoning chains significantly outperform simple examples on complex tasks.
- **Realistic noise and phrasing.** Include examples that mirror the messy formatting, irrelevant details, or ambiguous wording found in your real-world production data rather than overly sanitized textbook problems.

### 3. Diversity & Boundary Coverage

- **Distinct problem archetypes.** Avoid picking three examples that test the exact same rule or formula. Each example should demonstrate a different branch of logic, calculation method, or decision path within your domain.
- **Balanced positive and negative outcomes.** For classification, extraction, or validation tasks, include examples that trigger both "Yes/Valid" and "No/Invalid" outcomes so the model does not develop a bias toward a single label.
- **Explicit edge-case handling.** At least one example should demonstrate how to handle tricky exceptions, missing data, or tie-breaking rules so the model knows not to guess when conditions are unusual.

### Quick Evaluation Checklist

| Criterion | Weak Example | Strong Example |
| --- | --- | --- |
| Step Density | *"Since tax is 10% on ₹500, the total is ₹550."* | *"1. Base price = ₹500. 2. Tax (10%) = ₹50. 3. Total = ₹500 + ₹50 = ₹550."* |
| Pool Diversity | 3 examples all testing standard approvals | 1 approval, 1 rejection due to missing data, 1 boundary exception |
| Complexity | 2-step toy problems used for 6-step tasks | 5-to-6-step examples matching real query depth |
| Label Consistency | Mixes Result: True, Answer: Yes, and Valid | Uses Final Answer: YES or Final Answer: NO across all shots |

## Ordering effects: sequence changes output quality

The **sequence of Few-Shot CoT examples significantly impacts output quality** because large language models process tokens sequentially and suffer from strong positional biases—most notably **recency bias** and **primacy bias**. Changing the exact same set of examples from one order to another can swing accuracy by double digits on reasoning and classification tasks.

### 1. Why Order Changes Model Behavior

- **Recency bias (Last-in advantage).** Transformer attention heads attend most strongly to the tokens immediately preceding the target question. The final example in your prompt exerts the heaviest influence on the model's output format, step granularity, and label prediction.
- **Primacy bias (First-in framing).** The very first example sets the initial structural expectation for the rest of the prompt. If the first example is messy or poorly formatted, the model may treat the entire block as noisy context.
- **Label distribution skew.** If your last two or three examples all end with the same label (e.g., Answer: NO), the model builds momentum toward predicting that label again, even when the target question warrants a YES.

### 2. Proven Ordering Strategies

| Strategy | How to Sequence Examples | Best Use Case |
| --- | --- | --- |
| Similarity-Ascending | Place less similar examples first and put the example **most similar** to the target question **last**. | Dynamic retrieval (RAG / k-NN prompting) where examples are picked per query. |
| Complexity-Ascending | Start with a clean, straightforward example and escalate to your **hardest, multi-step example last**. | Multi-step math, coding, or logic tasks where you want deep reasoning without cutting corners. |
| Alternating Labels | Interleave outcomes (e.g., Yes → No → Yes → No) so no two adjacent examples share the same final answer. | Classification, policy enforcement, and eligibility checks to prevent majority-label bias. |
| Edge-Case Buffer | Place tricky exceptions or negative edge cases in the **middle** positions, keeping standard, clean templates at the start and end. | Preventing the model from over-applying rare exception rules to normal inputs. |

### 3. Practical Rules of Thumb

- **Anchor the end with your gold standard.** Never end your few-shot list with an unusual edge case or a short, trivial example. Always reserve the final slot before the user's query for a thorough, well-structured example that matches your ideal output.
- **Avoid repeating answers at the tail.** In a 4-shot classification prompt, ending with [True, False, False, False] heavily biases the model toward False. Balance the sequence so the tail does not create false momentum.
- **Test permutations during evaluation.** Because positional sensitivity varies across model families and prompt lengths, treat example ordering as a tunable hyperparameter and validate 2 to 3 permutations on a small test set before deploying to production.

## Diversity requirements: coverage over repetition

**Example diversity outperforms repetition** in Few-Shot Chain-of-Thought prompting because covering distinct reasoning patterns prevents the model from overfitting to narrow surface templates. When you provide 4 or 5 examples that all follow the exact same logic path, the model copies the superficial phrasing instead of learning how to adapt its reasoning to unseen variations.

### 1. Why Repetition Hurts Reasoning

- **Template overfitting.** If every example uses the exact same formula or phrasing, the model treats that specific text pattern as a rigid rule and breaks down when a user's question requires a slightly different angle.
- **Wasted context bandwidth.** Adding three near-identical examples consumes extra tokens and compute without teaching the model any new problem-solving strategies.
- **False confidence loops.** Repeatedly demonstrating a single outcome or method biases the model's attention heads toward that narrow path, even when the input query contradicts it.

### 2. Four Dimensions of High-Value Diversity

To maximize coverage within a small budget of 3 to 5 shots, vary your examples across four distinct axes:

| Diversity Dimension | Repetitive Pool (Weak) | Diverse Pool (Strong) |
| --- | --- | --- |
| Reasoning Path | 4 examples all using percentage discounts | 1 percentage discount, 1 flat fee deduction, 1 tiered tax, 1 unit conversion |
| Input Phrasing | All examples written as clean, textbook questions | Mix of formal queries, noisy user messages, and inputs with irrelevant decoy numbers |
| Outcome / Label | 4 examples that all end in Approved | 2 Approved (via different rules), 1 Rejected, and 1 Needs Review |
| Step Depth | All examples solved in exactly 3 short steps | Mix of 3-step, 5-step, and 6-step reasoning chains |

### 3. Practical Techniques for Building Diverse Pools

- **Cluster before selecting (Auto-CoT method).** Group your available training questions into distinct semantic clusters (for example, using text embeddings and k-means clustering), then pick **one representative example from each cluster**. This guarantees broad conceptual coverage without manual guesswork.
- **Include "decoy" information.** Make sure at least one example contains extra, irrelevant facts in the prompt and explicitly shows the reasoning step ignoring them (e.g., *"Note: The customer's account age is mentioned, but this rule only depends on transaction amount"*).
- **Map every business rule to a shot.** If your task relies on four core policies or edge cases, assign one dedicated example to each rule rather than doubling up on the most common scenario.
