# Chapter 5 - Quick Check

> Chapter 5: Prompt Design Patterns and Frameworks

> Related part: Code Generation Prompting: prompting for code generation and review

### Q1. The 4-part prompt (Role + Task + Context + Format) is not a rigid template - it is a checklist of what information the model needs to produce a useful, consistent output. Each part solves a specific failure mode: role anchors vocabulary and depth, task specifies the operation, context prevents hallucination, format makes output parseable.

Treating the 4-part prompt as a **diagnostic checklist** rather than a rigid fill-in-the-blank form captures exactly how prompt engineering works in practice.

### Why Thinking of It as a Checklist Matters

- **Modular Debugging.** When an LLM gives a poor answer, you can immediately trace *which* missing element caused the failure:
  - Too generic or wrong expertise level? → Add or sharpen **Role**.
  - Wandering or answering the wrong question? → Tighten **Task** verbs.
  - Guessing facts or missing edge cases? → Supply **Context**.
  - Hard to read or breaking downstream code? → Constrain **Format**.
- **Adaptable Order & Weight.** You do not always need all four parts in equal measure. For example, a simple extraction task might rely 80% on **Context** and **Format** with almost no **Role**, whereas a code review relies heavily on **Role** and **Task**.

### Q2. Zero-shot works well for common tasks the model has seen in training. Few-shot is the fix when you need a specific output structure the model cannot infer from a description alone - 2-5 high-quality examples consistently outperform longer zero-shot instructions for format-sensitive tasks.

### Why This Principle Holds Up in Practice

- **Show vs. Tell Efficiency.** Describing subtle formatting edge cases in prose takes dozens of ambiguous sentences that models still misinterpret. Showing **2–5 concrete Input -> Output pairs** activates in-context pattern matching directly inside the attention layers, locking in structure and boundary behavior immediately.
- **Diminishing Returns Beyond 5 Examples.** Two to five diverse examples (including balanced labels and a null/edge case) give the model enough variance to generalize the rule without inflating prefill latency or risking **majority-label bias**.
- **Production Rule of Thumb.** Start **zero-shot** to establish a fast, cheap baseline; the moment you see formatting drift or boundary confusion, promote those exact failure cases into **3-shot demonstrations**.

### Q3. System prompts are the mechanism for persistent persona - they condition every response in the conversation, not just the next turn. They define identity, knowledge scope, behavioural constraints, and tone defaults all at once.

Capturing that a system prompt acts as a **persistent, session-wide behavioral contract**—rather than a one-off instruction—is the key distinction between user turns and system/developer roles.

### Why That Framing Is So Useful

- **Separates Policy from Execution.**

Keeping **identity, knowledge scope, behavioral constraints, and tone defaults** inside the system prompt cleanly isolates static application policy from dynamic user inputs.

- **Protects Priority & Caching.** Because the system prompt sits at token position 0 with higher instruction hierarchy than user messages, it anchors every turn against persona drift while enabling **Prefix Caching** across repeated calls.

### Q4. Tone control is more reliable with specific behavioural rules ("use sentences under 20 words") than with abstract descriptors ("be concise"). Abstract descriptors give the model too much interpretive latitude.

Replacing subjective adjectives with **observable, testable constraints** removes interpretive guesswork and turns tone from a vague suggestion into an enforceable rule.

### Why Concrete Behavioral Rules Beat Abstract Descriptors

- **Eliminates Training-Data Ambiguity.** Words like *"concise"*, *"professional"*, or *"friendly"* mean wildly different things across blogs, academic papers, and support transcripts in the model's training data—leaving the model to guess which version you want.
- **Gives the Model Objective Targets.** Measurable constraints—such as *"keep sentences under 20 words"*, *"lead with the answer in sentence one"*, or *"ban exclamation marks and filler greetings"*—give the token-prediction loop clear boundaries it can satisfy consistently across turns.

### Q5. Format instructions must specify structure type, field/column names, null handling, and whether to include preamble text. Vague format instructions ("give me a table") produce inconsistent structures that break parsing pipelines.

Treating format instructions like a strict **API data contract** rather than a casual request eliminates the exact edge cases that break automated parsers.

### Why Those Four Specifications Prevent Pipeline Crashes

- **Structure Type & Field/Column Names.** Locking in exact JSON keys, types, or Markdown column headers stops the model from inventing synonyms ("user_name" vs. "fullName") across different runs.
- **Explicit null Handling.** Defining a fallback (null, "N/A", or []) prevents the model from silently dropping missing keys or hallucinating placeholder values when source data is incomplete.
- **Preamble & Wrapper Bans.** Explicitly forbidding conversational intros (*"Here is your data:"*) or markdown fences (```json) ensures downstream tools like json.loads() or CSV splitters can ingest the raw output immediately without fragile regex cleanup.

### Q6. Few-shot example quality matters more than quantity. One wrong example actively degrades output. Cover edge cases in your example set - do not pick only easy or "perfect" examples.

Because LLMs treat your demonstrations as the ground-truth pattern to mimic, a single inconsistent or flawed example poisons in-context learning, while curated **edge cases** teach the model exact decision boundaries far better than ten easy examples ever could.

### Why Quality and Edge-Case Coverage Matter So Much

- **Error Amplification.** An LLM assumes every example in your prompt is intentional. One typo in a JSON key, an inconsistent null value, or a mislabeled category teaches the model to reproduce that exact mistake.
- **Boundary Calibration.** Easy examples only confirm what the model already gets right in zero-shot mode. Including **borderline cases, noisy inputs, and empty/null inputs** shows the model precisely where one category ends and another begins.
- **High Signal, Low Token Cost.** Three sharp, diverse examples keep prefill latency low and preserve context window space while delivering peak accuracy.
