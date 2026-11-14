# Chapter 6 - Quick Check

> Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)

> Related part: Decision Framework: Prompt vs Automate

### Q1. A model answers a math word problem incorrectly with zero-shot prompting but correctly with zero-shot CoT. What is the mechanical explanation for why the CoT version produces a better answer?

Zero-Shot Chain-of-Thought (Zero-Shot CoT) produces the correct answer because generating intermediate reasoning tokens gives the transformer additional sequential forward passes and turns its own output text into an external working memory. Without CoT, the model is forced to compress a multi-step calculation into a single forward pass, causing it to rely on surface-level statistical guesses.

Here is the exact mechanical breakdown of what changes inside the model:

#### 1. Expanding Compute Beyond a Fixed-Depth Bottleneck

- **Fixed compute per token.** A transformer has a fixed number of neural layers (depth), meaning it spends the exact same amount of mathematical operations to predict one token regardless of how hard the problem is.
- **Serial iteration over single-pass compression.** In standard zero-shot prompting, the model must compute every intermediate variable and arrive at the final number in **one single vertical pass** through its layers before emitting the first answer token. Appending a trigger like *"Let's think step by step"* triggers **dozens of separate forward passes**—one for each generated token—allowing the model to execute one simple operation per pass instead of solving the entire equation at once.

#### 2. Using the Context Window as an External Scratchpad

- **No internal recurrent memory.** Standard transformers cannot pass hidden intermediate variables directly from one token generation step to the next inside their internal activations without losing precision.
- **Re-attending to written tokens.** Writing out an intermediate result (e.g., *"First, 15 × 4 = 60"*) projects that internal calculation into concrete text inside the context window. On the very next forward pass, the model's self-attention heads look back at those written tokens, using the text stream as an external RAM cache to hold partial answers while computing the next step.

#### 3. Shifting Attention Circuits Away From Shortcuts

- **Bypassing memorized priors.** Mechanistic interpretability research shows that without a reasoning trigger, early and middle layers rely heavily on pre-trained bigram associations and surface-level heuristics to guess an immediate number.
- **Activating structured reasoning pathways.** The *"step by step"* trigger shifts the next-token probability distribution away from predicting an immediate answer and toward predicting an explanatory sequence. Attention heads dynamically shift from scanning the prompt for quick keyword matches to tracking relationships across the model's newly generated steps.

#### 4. Converting One Hard Leap Into Easy Micro-Steps

- **Flattening uncertainty.** Jumping straight from a multi-step word problem to the final number requires selecting a low-probability token that competes against many plausible-sounding wrong guesses.
- **High-probability transitions.** Each individual step in a CoT trace (like simple addition or subtraction) represents a heavily memorized, near-100%-probability transition. Getting Step 1 right mathematically narrows the conditional probability space, keeping the model on a high-confidence trajectory all the way to the final answer.

### Q2. You have a few-shot set for classifying customer support tickets into 5 categories. All 5 examples happen to use formal, polite language. The model starts classifying casual-language tickets incorrectly. What dimension of diversity is missing from your example set?

The missing dimension of diversity is **input phrasing (stylistic and register diversity)**.

### Why This Causes Misclassification

- **Overfitting to surface style.** Because every example in your prompt uses formal, polite language, the model's attention heads treat formal phrasing as a core signal for those categories rather than focusing solely on the underlying customer issue.
- **Distribution mismatch at runtime.** When real-world users submit casual, slang-heavy, abbreviated, or frustrated messages, the input falls outside the narrow linguistic distribution demonstrated in the prompt, causing the model to guess erratically.

### How to Fix the Example Set

- **Vary linguistic register across shots.** Rewrite 2 or 3 of your existing examples so your 5-shot set spans the full spectrum of real customer voices—such as one formal email, one terse/abbreviated chat message, one frustrated complaint with typos, and one casual conversational query.
- **Keep the underlying logic identical.** Ensure that even when the tone changes from polite to casual, the Chain-of-Thought reasoning steps extract the exact same core intent before assigning the category label.

### Q3. You are building a few-shot prompt for a task and have 20 candidate examples. How would you decide which 5 to include? What would you optimize for, and what tool would you use to measure it?

To select the best **5 examples out of 20**, you should use a cluster-and-validate pipeline: group the 20 candidates by semantic and structural similarity to ensure broad coverage, pick the highest-quality representative from each cluster, and then empirically evaluate candidate permutations against a held-out validation set.

#### 1. How to Decide Which 5 to Include (Selection & Ordering)

- **Step 1: Cluster for maximum coverage (Auto-CoT approach).** Convert all 20 candidate inputs into vector embeddings and group them into **5 clusters** (using k-means clustering). Picking **one representative example from each cluster** guarantees you cover the full breadth of your problem space instead of accidentally picking near-duplicates.
- **Step 2: Filter for structural quality within each cluster.** From each cluster, select the candidate that has **atomic step granularity** (one clear logical operation per line), **zero skipped assumptions**, and **realistic input phrasing** (avoiding overly clean textbook examples if production inputs are noisy).
- **Step 3: Sequence to control positional bias.** Arrange the final 5 examples in **complexity-ascending order** (putting the most thorough, multi-step example last to leverage recency bias) while **alternating final labels** so no two adjacent examples share the exact same outcome.

#### 2. What to Optimize For

When selecting and ordering your 5-shot prompt, balance four core objectives:

- **Rule and edge-case diversity.** Every example should demonstrate a distinct reasoning path, boundary condition, or exception rather than repeating the same formula.
- **Label and outcome balance.** Ensure positive, negative, and edge-case outcomes are evenly represented so the model does not develop majority-label bias.
- **Reasoning depth calibration.** Prioritize examples with complete, multi-step reasoning traces that match or exceed the difficulty of your hardest expected production queries.
- **Template symmetry.** Every example must share identical structural delimiters (e.g., Input:, Reasoning:, Final Answer:) to minimize next-token formatting noise.

#### 3. What Tool to Use to Measure It

- **Automated Prompt Compilers (DSPy).** Instead of guessing manually, pass all 20 candidates into **DSPy** using an optimizer like **BootstrapFewShotWithRandomSearch** or **MIPROv2**. These tools systematically test different 5-example subsets and orderings against the remaining candidates (or a separate validation split) to lock in the combination with the highest score.
- **Embedding & Clustering Utilities (scikit-learn + sentence-transformers).** Use lightweight embedding models paired with **k-means clustering** or **Maximal Marginal Relevance (MMR)** to mathematically measure and maximize diversity across your chosen 5 shots before running LLM evaluations.
- **Programmatic Evaluation Metrics.** Measure prompt quality using an objective validation script—such as **exact match**, **macro F1 score** (for imbalanced classification), **JSON schema pass rate**, or a calibrated **LLM-as-a-judge rubric**—tracked across a held-out evaluation set.

### Q4. You test two orderings of the same 4 few-shot examples and get different model outputs on an ambiguous input. Which position in the sequence has the strongest influence on the output, and why?

The **final position (Position 4, immediately preceding the target input)** has the strongest influence on the model's output due to **recency bias** in transformer self-attention.

### Why Position 4 Dominates

- **Recency bias in causal attention.** During next-token prediction, a transformer's attention heads attend most strongly to the tokens closest to the generation boundary. Because the 4th example sits right before your ambiguous query, its structure, reasoning depth, and final label exert the heaviest gravitational pull on the model's immediate next-token probability distribution.
- **Label and pattern momentum.** On an ambiguous input—where the query itself does not strongly point to one obvious answer—the model breaks the tie by leaning on the most recently seen pattern. If Position 4 demonstrates a specific label or edge-case rule, the model is statistically primed to repeat that exact decision path.
- **Secondary primacy effect (Position 1).** While Position 4 is the strongest driver of the final answer on ambiguous inputs, **Position 1** exerts the second-strongest influence (primacy bias) by setting the initial structural frame for the entire context window—leaving Positions 2 and 3 in the middle with the weakest relative impact.

### Practical Takeaway

- **Never end on an edge case.** Always place your cleanest, most representative "gold-standard" example in the final slot right before the user's question, and tuck unusual exceptions or negative boundary cases into Positions 2 or 3.

### Q5. DSPy's BootstrapFewShot optimizer generates few-shot examples automatically. What two things do you need to provide before you can run it? What happens if you do not have them?

To run DSPy's **BootstrapFewShot** optimizer, you must provide two core inputs alongside your uncompiled DSPy program: a training dataset (trainset) and an evaluation metric (metric).

#### 1. The Two Required Inputs

- **A Training Dataset (trainset).** A small collection of representative input-output examples (typically **20 to 100 rows**) formatted as dspy.Example objects with marked input fields. You only need the inputs and expected ground-truth outputs—you do not need to write the step-by-step reasoning chains yourself.
- **An Evaluation Metric (metric).** A Python validation function that takes (example, prediction, trace=None) and returns a boolean (True/False) or numeric score (0.0 to 1.0). This function defines what counts as a successful output.

#### 2. What Happens If You Do Not Have Them?

- **If you do not have a trainset:** The optimizer has no starting questions to run through your teacher model, meaning **compilation cannot run at all**. Without input queries, DSPy cannot generate candidate Chain-of-Thought reasoning traces to populate your few-shot prompt.
- **If you do not have a metric:** BootstrapFewShot loses its **rejection-sampling filter**. During compilation, the optimizer uses a teacher LLM to generate step-by-step reasoning traces for your training questions and relies on your metric to discard wrong answers. Without a metric to verify correctness, bad or hallucinated reasoning traces get saved straight into your compiled prompt—causing the final program to systematically repeat flawed logic at runtime.

### Summary Comparison

| Missing Requirement | Mechanical Consequence in BootstrapFewShot | Fallback Strategy |
| --- | --- | --- |
| No trainset | Optimizer fails immediately; zero candidate traces can be generated. | Start with manual **Zero-Shot CoT** or write **3–5 Static Few-Shot** examples by hand until you log real user inputs. |
| No metric | Cannot filter out wrong teacher outputs; risks injecting hallucinated CoT traces. | Write a basic structural check (e.g., JSON/type validation) or use an **LLM-as-a-judge** rubric before compiling. |

### Q6. You are starting a new feature that requires an LLM to classify text into 3 categories. You have no labeled data yet. Should you use DSPy or write a prompt manually? Walk through the decision using the framework from Part 5.

You should **write a prompt manually** (starting with **Zero-Shot CoT** and quickly stabilizing with **Static Few-Shot CoT**) rather than using DSPy.

Walking through the **Decision Framework from Part 5**, every diagnostic indicator points away from automated compilation and toward manual prompting at this stage:

#### 1. Five-Question Decision Checklist Walkthrough

- **Do you have labeled training data and a clear metric? (No)**
  - **Framework Rule:** DSPy optimizers like BootstrapFewShot and MIPROv2 require **20 to 200+ labeled input-output pairs** and a quantitative validation metric to synthesize and filter reasoning traces. With zero labeled data, a compiler has no ground-truth signal to optimize against.
- **What stage of the Progressive Escalation Ladder are you on? (Level 1 → Level 2)**
  - **Framework Rule:** Start at **Level 1 (Zero-Shot CoT)** when prototyping with zero labeled examples, then move to **Level 2 (Static Few-Shot CoT)** by hand-crafting 3 to 6 balanced examples (covering all 3 categories plus edge cases) once you see how the model behaves. Reaching for **Level 4 (Compiled Pipelines)** on day one is premature optimization.
- **Is your workflow a single prompt or a multi-step chain? (Single step)**
  - **Framework Rule:** Classifying text into 3 categories is a straightforward, single-step task. DSPy's biggest advantage—jointly optimizing cascading multi-hop modules—is unnecessary overhead for a single classification call.
- **Are you optimizing for rapid iteration and prefix caching? (Yes)**
  - **Framework Rule:** Hand-crafting a static prompt lets you ship in minutes, iterate immediately on phrasing, and benefit from **100% API prefix caching** across incoming requests.

#### 2. Recommended Action Plan (The Hybrid Path)

1. **Launch with Level 1 (Zero-Shot CoT):** Write a clean, explicit manual prompt defining the 3 categories, clear boundary rules for each, and a step-by-step reasoning instruction before outputting the final label.
2. **Upgrade to Level 2 (Static Few-Shot CoT):** Hand-write **3 to 6 diverse examples** (at least 1–2 per category, varying casual vs. formal tone, and alternating label order) to lock in formatting and boundary accuracy.
3. **Collect data for Level 4 (DSPy Graduation):** Log real production inputs and human corrections. Once you accumulate **50+ verified examples** and hit an accuracy plateau—or decide to distill the classifier onto a smaller, cheaper model—plug that dataset into **DSPy** to compile an automated version.

### Q7. A teammate says: "Dynamic few-shot retrieval is overkill - just use the same 5 examples every time." Under what conditions would they be right? Under what conditions would they be wrong?

Your teammate is **right when your domain is narrow, structurally uniform, and sensitive to API prefix caching or latency**, and **wrong when your domain spans dozens of distinct rules, schemas, or edge cases that cannot fit inside a single 5-example window**.

#### 1. When Your Teammate Is Right (Static 5-Shot Wins)

- **Narrow, predictable problem space.** If every incoming query follows the same 2 or 3 logic paths (such as basic sentiment analysis, simple entity extraction, or a 3-category classifier), 5 well-chosen static examples easily cover the entire task distribution.
- **Strict unit economics and API prefix caching.** Modern LLM providers discount cached input tokens by 50% to 90% and cut time-to-first-token when the prompt prefix stays identical across calls. Using the exact same 5 examples gives you a **100% cache hit rate**, whereas dynamic retrieval changes the prompt on every request and invalidates the cache.
- **Tight latency SLAs and low engineering overhead.** Static prompting avoids the extra 10–50 ms overhead of embedding every query and querying a vector database, while sparing your team from maintaining an embedding pipeline and vector index.
- **Small example bank.** If you only have 10 to 15 total labeled examples, setting up a vector retriever adds infrastructure complexity without providing meaningful selection diversity.

#### 2. When Your Teammate Is Wrong (Dynamic Retrieval Wins)

- **High-variance domains with dozens of rules or schemas.** In tasks like text-to-SQL across 100 database tables, multi-tier tax/policy compliance, or complex customer support routing, 5 static examples leave 90% of your rules completely unrepresented—causing the model to guess or hallucinate on unseen branches.
- **Context-length vs. coverage trade-off.** Trying to fix edge-case blindness by cramming 30 static examples into one prompt drives up token costs on every call and triggers **"lost-in-the-middle" attention degradation**, where the model ignores examples buried in the center.
- **Rapidly evolving catalogs or policies.** When product rules or edge cases change weekly, updating a static prompt means risky manual text edits that often break existing behaviors. With dynamic retrieval, you simply add or update a row in your vector database without touching prompt logic.
- **Severe surface-phrasing mismatch.** When incoming queries vary wildly in format, jargon, or structure, dynamically fetching the 3 to 5 closest worked examples (k-NN / MMR) anchors the model's recency bias on the exact reasoning pattern needed for that specific query.

### Summary Decision Matrix

| Condition | Teammate Is Right (Use Static 5-Shot) | Teammate Is Wrong (Use Dynamic Retrieval) |
| --- | --- | --- |
| Rule / Schema Breadth | 3–5 core rules cover 95%+ of queries | 20–500+ distinct schemas, policies, or edge cases |
| Caching & Cost Priority | Relies heavily on static prefix cache discounts | Accuracy gains outweigh higher uncached input token cost |
| Maintenance Frequency | Stable task requirements | Frequent new edge cases added weekly |
| Infrastructure Budget | Minimal; single prompt template | Vector store and embedding pipeline already available |
