# Chapter 11 - Part 3: Code Generation and Review Prompting: Structuring prompts that produce clean, reviewable code

> Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

**Code Generation** with LLMs is the process of prompting models to write, debug, refactor, translate, or explain software code across programming languages. Modern LLMs excel at code generation because source code follows strict syntax rules, predictable patterns, and clear logical structures.

### 1. Core Code Generation Use Cases

- **Scaffolding & Boilerplate:** Generating starter templates, REST APIs, database schemas, and unit test suites from plain-English specifications.
- **Code Translation & Migration:** Converting legacy code between languages or frameworks (e.g., Python 2 to Python 3, SQL dialects, or Class components to React Hooks).
- **Debugging & Refactoring:** Identifying syntax errors, race conditions, or performance bottlenecks from stack traces and rewriting functions for better readability.
- **Multimodal Code Generation (UI-to-Code):** Passing a screenshot, Figma mockup, or hand-drawn wireframe into a Vision-Language Model to generate matching HTML, Tailwind CSS, or React components.

### 2. Prompting Best Practices for Reliable Code

- **Specify the Exact Stack & Versions:** State the programming language, framework versions, and libraries upfront (e.g., *"Use Python 3.12, FastAPI, and Pydantic v2"* instead of *"Write a Python API"*).
- **Define Inputs, Outputs & Edge Cases:** Explicitly list function signatures, expected data types, and how errors or empty inputs should be handled.
- **Provide Existing Context (Repo-Level Grounding):** Include relevant helper functions, database models, or type definitions in your prompt so the model uses your project's actual conventions rather than inventing fake imports.
- **Ask for Plan-First Generation:** For complex features, instruct the model to outline the file structure and logic step-by-step before writing code to prevent architectural bugs.

### 3. Production & Agentic Code Workflows

- **Structured Output for Code:** When building automated coding tools, wrap generated code in a JSON schema ({"filename": "...", "code": "...", "explanation": "..."}) to avoid fragile markdown backtick parsing.
- **Tool-Augmented Execution (Sandboxes):** Connect the LLM to a secure code execution environment (like a Docker container or Python interpreter) so the model can run its own code, inspect compiler errors or failed unit tests, and self-correct in a loop.
- **Human Review & Security Scanning:** Never deploy LLM-generated code directly to production without automated linting, static analysis, and human review—models can still introduce subtle security flaws like SQL injection or outdated dependencies.

## Why code prompting is different

Code prompting is fundamentally different from general text prompting because code is executable, unforgiving of minor errors, and tightly coupled to an external codebase. While a slight phrasing flaw in a creative essay still reads fine, a single wrong symbol or hallucinated library in code breaks the entire program.

### 1. Zero Tolerance for Syntax & Logic Errors

- **Binary Pass/Fail Execution:** Prose can be "mostly right" and still useful. Code is compiled or interpreted by a machine, meaning a missing colon, wrong indentation, or mismatched data type causes an immediate crash.
- **Subtle Edge Cases:** Code that runs without syntax errors can still silently corrupt data or fail on edge cases (like empty lists, null values, or timezone shifts) unless explicitly constrained in the prompt.

### 2. Heavy Dependency on Hidden External Context

- **Repo-Level Coupling:** A standalone paragraph makes sense on its own, whereas a single function relies on unseen database schemas, helper utilities, environment variables, and specific package versions.
- **Hallucinated APIs & Deprecated Versions:** Models are trained on years of older code, so without explicit version constraints (e.g., *Pydantic v2* vs. *v1*, or *Next.js App Router* vs. *Pages Router*), they frequently mix incompatible syntax or invent non-existent library methods.

### 3. Verifiable Feedback Loops (Self-Healing)

- **Automated Ground Truth:** Unlike subjective writing tasks where quality is hard to measure automatically, code can be tested immediately using compilers, linters, type checkers, and unit tests.
- **Iterative Error-Driven Prompting:** Code prompting works best as an interactive loop—feeding exact compiler stack traces or failed test assertions back into the model lets it diagnose and fix its own mistakes deterministically.

### 4. High Security & Production Risk

- **Executable Consequences:** Bad prose is merely unhelpful; bad code can introduce SQL injection vulnerabilities, expose API keys, trigger infinite loops, or delete production records.
- **Strict Constraints Required:** Code prompts must explicitly specify security guardrails, input validation, and error-handling behavior rather than leaving them to the model's defaults.

## Prompting for code generation

**Prompting for code generation** is most effective when you treat the prompt like a technical specification rather than a casual request. Giving the model clear constraints, exact types, and surrounding context eliminates guesswork and prevents hallucinated libraries.

### 1. The Anatomy of a High-Precision Code Prompt

Include these five elements when asking an LLM to write production code:

- **Tech Stack & Exact Versions:** Lock down the language, framework, and library versions so the model does not mix outdated syntax (e.g., *"Python 3.12, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0"*).
- **Exact Function Signature & Types:** Specify function names, parameter types, and return types upfront so the output drops cleanly into your codebase.
- **Surrounding Context:** Paste existing interfaces, database models, or helper functions so the model reuses your project's actual conventions instead of inventing dummy utilities.
- **Edge Cases & Error Handling:** Explicitly state what should happen on invalid inputs, network timeouts, or empty data (e.g., *"Raise a ValueError if the list is empty; retry 3 times on HTTP 429"*).
- **Negative Constraints (What NOT to Do):** Tell the model what to avoid—such as *"Do not use external third-party libraries; use only Python's standard library"* or *"Do not omit implementation details with # TODO comments."*

### 2. Proven Code Prompting Patterns

- **Test-Driven Prompting (TDD):** Provide unit tests first and instruct the model to write code that passes every assertion. This anchors the logic to exact expected inputs and outputs.
- **Plan-Before-Code (Chain-of-Thought):** For multi-file features or tricky algorithms, ask the model to outline the data structures, edge cases, and step-by-step logic before writing a single line of code.
- **Few-Shot Style Matching:** Show 1 example function from your repository so the model matches your exact naming style, docstring format, logging pattern, and error-handling conventions.
- **Structured Output Wrapping:** When generating code inside an automated pipeline, enforce a JSON schema ({"file_path": "...", "code": "...", "dependencies": [...]}) so your parser never breaks on conversational filler text.

### 3. Weak vs. Strong Prompt Example

- **Weak Prompt:**

```text
"Write a Python function to fetch user data from an API and save it."
```

- **Strong Prompt:**

```text
"Write an async Python 3.12 function fetch_and_store_user(user_id: int, db: AsyncSession) -> UserRecord using httpx and SQLAlchemy 2.0.
Call GET https://example.com{user_id} with a 5-second timeout.
Validate the JSON response using the UserSchema Pydantic model shown below.
If the API returns 404, return None. If it times out or returns 5xx, raise ExternalServiceError.
Upsert the validated record into the users table and commit the session.
Return complete, runnable code with type hints and no placeholder comments."
```

## Review Prompting

**Review Prompting** (also called **Self-Review**, **Critic Prompting**, or **LLM-as-a-Judge**) is a prompting pattern where you instruct an LLM to systematically audit, critique, and refine an output—whether generated by an AI or written by a human—against a strict rubric before accepting it as final.

Rather than trusting a model's first pass, review prompting separates **generation** from **verification**, catching hallucinations, logic flaws, and policy violations that single-pass prompts miss.

### 1. Core Patterns of Review Prompting

- **Self-Critique & Refine (Reflexion):** After generating an initial response, the model is prompted to inspect its own answer for flaws, list specific errors, and produce an improved second draft.
- **Rubric-Based Evaluation (LLM-as-a-Judge):** You give the model an explicit scoring checklist (e.g., *Accuracy, Completeness, Tone, Formatting*) with clear pass/fail criteria so it grades outputs consistently rather than giving vague opinions.
- **Multi-Persona / Adversarial Review:** You ask the model to evaluate content from conflicting viewpoints (such as a *Security Auditor*, a *Skeptical End-User*, and a *Compliance Officer*) to uncover blind spots.
- **Grounded Fact-Checking Review:** You pass both a **source document** and a **draft summary**, instructing the model to flag any claim in the draft that is not directly supported by the source text.

### 2. Best Practices for High-Signal Review Prompts

- **Require Evidence Before Judgment:** Force the model to quote exact lines or cite specific errors before assigning a score or declaring something "approved."
- **Suppress Fluff & Nitpicks:** Explicitly instruct the reviewer to skip minor stylistic preferences and focus only on factual errors, missing requirements, or high-impact defects.
- **Use Structured Output Schemas:** Enforce a JSON or Pydantic output ({"passed": bool, "severity": str, "issues": [...], "revised_output": str}) so your application can programmatically decide whether to accept the output or trigger an automatic retry loop.
- **Allow a "No Issues Found" Exit:** Explicitly tell the model that if the work meets all criteria, it should output "PASS" rather than inventing fake problems just to look helpful.

### 3. Universal Review Prompt Template

```text
Act as an objective quality auditor. Evaluate the [Draft Output] against the [Original Requirements / Source Context] using the rubric below.

Rubric:
1. Factual Grounding: Every claim must be supported by the source context.
2. Completeness: All requested constraints and edge cases must be addressed.
3. Clarity & Format: Must follow the exact output structure specified.

Instructions:
- List only objective, high-impact defects. Do not suggest minor stylistic rewrites.
- For each defect, quote the exact problematic text and explain why it fails the rubric.
- If zero defects exist, return "STATUS: PASS". Otherwise, return "STATUS: FAIL" followed by a corrected version.

Original Requirements:
[Insert requirements or source text]

Draft Output:
[Insert draft to review]
```

## Prompting for code review

**Prompting for code review** works best when you narrow the LLM's focus with a specific review persona, explicit evaluation criteria, and a structured output format. Generic prompts like *"Review this code"* produce superficial praise and nitpicks, whereas targeted prompts catch real bugs, security holes, and performance bottlenecks.

### 1. Core Principles of Effective Code Review Prompts

- **Give a Focused Review Lens (Persona + Scope):** Instead of asking the model to check everything at once, focus it on high-impact dimensions such as security, concurrency, edge cases, or database performance.
- **Provide System Context:** Explain how the code is used in production (e.g., *"This endpoint handles 5,000 requests per second on a public API"*). Context helps the model prioritize real risks over theoretical ones.
- **Suppress Noise & Style Nitpicks:** Explicitly instruct the model to ignore formatting, variable naming, or linter rules unless they cause bugs, keeping feedback actionable.
- **Require Evidence + Concrete Fixes:** Demand that every issue reported includes the exact line or snippet, an explanation of *why* it fails under specific inputs, and a corrected code block.

### 2. High-Signal Code Review Dimensions

| Review Focus | What to Instruct the Model to Check |
| --- | --- |
| Bugs & Edge Cases | Off-by-one errors, null/None handling, empty collections, integer overflows, and unhandled exceptions. |
| Security Vulnerabilities | SQL/NoSQL injection, hardcoded secrets, broken authentication/authorization checks, path traversal, and unsafe deserialization. |
| Performance & Scalability | N+1 database queries, blocking I/O inside async functions, unnecessary memory copies, and O(n²) loops on large inputs. |
| Concurrency & State | Race conditions, deadlocks, missing locks on shared state, and non-idempotent retries. |

### 3. Ready-to-Use Code Review Prompt Template

```text
Act as a Senior Staff Engineer performing a rigorous pull-request review.

Context: [Describe what the code does, expected traffic, and tech stack].

Review the code below strictly for:
1. Logic bugs and unhandled edge cases (empty inputs, nulls, timeouts).
2. Security vulnerabilities (injection, auth bypass, data leaks).
3. Performance bottlenecks (N+1 queries, blocking calls, memory leaks).

Rules:
- Do NOT comment on code formatting, docstrings, or minor naming preferences.
- Only flag issues with high confidence. If the code is solid, say so.
- For each issue found, output:
  - **Severity:** [Critical / High / Medium]
  - **Location:** Exact function or line reference
  - **Failure Scenario:** Exact input or condition that breaks it
  - **Fix:** Minimal corrected code snippet

Code to review:
[Paste code or git diff here]
```

### 4. Pro Tip: Review Git Diffs Instead of Whole Files

When reviewing pull requests, pass the **git diff** alongside the surrounding file context. Instruct the model to only critique the changed lines (+ / -) while using the rest of the file purely to verify types, imports, and side effects.
