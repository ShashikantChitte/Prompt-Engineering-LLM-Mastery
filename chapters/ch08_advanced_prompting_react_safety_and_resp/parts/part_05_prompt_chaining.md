# Chapter 8 - Part 5: Prompt Chaining

> Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI

**Prompt Chaining** is a software architecture pattern for Large Language Models (LLMs) where a complex task is decomposed into a sequence of smaller, focused sub-tasks, with the output of one prompt passed programmatically as the input to the next.

Instead of cramming every instruction, constraint, and reasoning step into one massive "mega-prompt," prompt chaining treats LLM calls like modular functions in a data pipeline.

### 1. Why Mega-Prompts Fail (and Chaining Works)

Asking a single prompt to perform five distinct cognitive operations at once—such as extracting facts, translating terms, checking policy compliance, formatting JSON, and writing a summary—leads to predictable degradation:

- **Attention Dilution:** As prompt length grows, instructions buried in the middle lose influence, causing the model to skip edge cases or drop formatting rules.
- **Error Compounding:** If the model misinterprets a fact early in a single long generation, every downstream paragraph builds on that mistake without a validation checkpoint.
- **Rigid Model Selection:** A single prompt forces you to pay frontier-model pricing for the entire workflow, even if 80% of the steps are simple extraction or formatting.

### 2. Core Prompt Chaining Patterns

Production systems typically combine three structural chaining topologies:

- **Sequential Pipeline (A -> B -> C):** Linear step-by-step transformation.
  - *Example:* **Prompt 1** extracts raw entities from a messy PDF → **Prompt 2** normalizes currencies and dates into JSON → **Prompt 3** generates an executive summary from the clean JSON.
- **Conditional Routing / Branching (A -> If X then B else C):** A lightweight classifier prompt inspects the user query first and routes it to a specialized downstream prompt.
  - *Example:* **Prompt 1** classifies a customer ticket as Billing, Technical Bug, or Refund → routes to a tailored prompt with category-specific rules and tools.
- **Map-Reduce / Parallel Fan-Out (Split -> [A1, A2, A3] -> Merge):** Splits a large document into chunks, processes each chunk concurrently with identical prompts, and merges the results in a final synthesis prompt.
  - *Example:* Analyzing a 100-page legal contract by running clause-extraction prompts across 10 sections in parallel, then feeding all flagged risks into a final risk-assessment prompt.

### 3. Production Benefits & Trade-Offs

| Dimension | Single Mega-Prompt | Prompt Chaining |
| --- | --- | --- |
| Instruction Adherence | Drops as constraints accumulate | **High** (each prompt focuses on 1 clear job) |
| Debuggability & Testing | Hard to isolate where a failure occurred | **Easy** (inspect, log, and unit-test each step independently) |
| Deterministic Guardrails | Can only validate at the very end | Insert **Python/regex/schema checks** between steps before continuing |
| Cost Optimization | Single model tier for everything | Route simple steps to **small/cheap models**, hard steps to **large models** |
| Latency & Overhead | Single network round-trip | Higher end-to-end latency due to sequential API calls |

## Rule of Thumb: When to Split a Prompt

Split a single prompt into a chain whenever you notice **more than two distinct transformations** (e.g., *extract → verify → rewrite*), when you need **deterministic code validation** mid-workflow, or when adding a new instruction consistently breaks an existing rule.

## Prompt Chaining - multi-step pipelines, passing outputs as inputs, when to chain vs use one big prompt

Prompt Chaining breaks a complex workflow into a multi-step pipeline of focused LLM calls, where the structured output of Step N is validated and passed programmatically as the input to Step N+1.

While a single "mega-prompt" tries to solve everything in one monolithic generation, prompt chaining treats each LLM call like a modular function—improving accuracy, debuggability, and cost efficiency on multi-stage tasks.

### 1. How Multi-Step Pipelines Work (Passing Outputs as Inputs)

In a well-engineered chain, intermediate outputs are rarely raw, unstructured prose. Instead, each stage transforms data into a clean contract for the next stage:

1. **Step 1 — Extract & Structure:** Takes raw, noisy input (e.g., a 10-page support transcript) and outputs a clean JSON object of facts and timestamps.
2. **Validation Gate (Code Layer):** A deterministic script (like Pydantic or regex) checks that the JSON is valid and required fields are non-empty before spending tokens on Step 2.
3. **Step 2 — Reason & Analyze:** Receives *only* the verified JSON from Step 1 (stripping away conversational noise) and evaluates policy rules or calculates root causes.
4. **Step 3 — Format & Localize:** Takes the analytical verdict from Step 2 and drafts a polite, user-facing response in the target tone or language.

### 2. Core Pipeline Topologies

- **Linear Chain (Step 1 -> Step 2 -> Step 3):** Best for sequential data transformations (e.g., *Transcribe → Summarize → Translate*).
- **Router / Branching Chain (Classifier -> Specialized Prompt):** Step 1 categorizes the intent (e.g., Refund, Technical Bug, Account Access), and application code routes the request to a dedicated, compact prompt tailored exclusively to that category.
- **Parallel Fan-Out / Map-Reduce (Split -> [Parallel Calls] -> Synthesizer):** Splits large inputs into independent chunks, processes them concurrently, and passes all extracted summaries into a final aggregation prompt.

### 3. When to Chain vs. Use One Big Prompt

Deciding between a single mega-prompt and a multi-step chain comes down to **task coupling, latency budgets, and error tolerance**:

| Criteria | Use One Big Prompt | Use Prompt Chaining |
| --- | --- | --- |
| Number of Distinct Tasks | **1–2 closely coupled tasks** (e.g., summarize and extract 3 tags). | **3+ distinct transformations** (e.g., extract, verify against rules, calculate, rewrite). |
| Context & Attention Load | Short inputs where every instruction stays clearly in focus. | Long inputs or heavy rulebooks where instructions in the middle get forgotten. |
| Need for Deterministic Checks | No mid-process code execution, API lookups, or schema gates needed. | Need **Python/SQL/regex validation** or external tool calls between reasoning stages. |
| Latency Sensitivity | **Strict real-time UI** (single network round-trip, fast time-to-first-token). | **Offline batch jobs** or workflows where accuracy outweighs extra round-trip latency. |
| Model & Cost Optimization | Entire task requires the same intelligence tier. | Mix models—use a **cheap, fast model** for extraction/formatting and a **frontier model** only for the hard reasoning step. |
| Debugging & Iteration | Acceptable to tune the prompt holistically. | Need to isolate, log, and unit-test individual failure points without breaking other steps. |

## Practical Rule of Thumb

Start with **one well-structured prompt** (using XML sections and Chain-of-Thought). Split it into a **Prompt Chain** the moment you hit any of three triggers:

1. Adding a new instruction causes the model to forget an existing rule.
2. You need deterministic code to verify or transform intermediate data before the model continues.
3. A single step in the workflow requires a stronger (or cheaper) model than the rest.
