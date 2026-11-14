# Chapter 5 - Part 5: Code Generation Prompting: prompting for code generation and review

> Chapter 5: Prompt Design Patterns and Frameworks

**Code Generation Prompting** is the practice of writing structured, unambiguous specifications so an LLM produces complete, runnable, secure, and idiomatic code on the first pass—rather than buggy snippets filled with placeholder comments. Because code has zero tolerance for syntax errors or hallucinated APIs, effective code prompts act like a **technical design spec** rather than a casual request.

### 1. The 5 Essential Elements of a Code Prompt

| Element | What to Specify | Why It Prevents Bugs | Example |
| --- | --- | --- | --- |
| 1. Tech Stack & Exact Versions | Language, runtime version, framework, and allowed libraries. | Stops the model from mixing deprecated syntax (e.g., Pydantic v1 vs. v2, Next.js Pages vs. App Router). | *"Use Python 3.12, FastAPI 0.115+, SQLAlchemy 2.0 async syntax, and httpx."* |
| 2. Function Signature & Data Contracts | Exact function names, input parameter types, return types, and sample payloads. | Ensures the generated code plugs cleanly into your existing codebase without glue-code rewrites. | *"Signature: async def sync_invoices(batch_id: str, limit: int = 50) -> SyncResult:"* |
| 3. Edge Cases & Error Handling | Timeouts, empty inputs, rate limits, retries, and specific exceptions to catch. | Prevents "happy-path-only" code that crashes in production on network blips or None values. | *"Handle HTTP 429 with exponential backoff (max 3 retries) and raise SyncTimeoutError after 10s."* |
| 4. Existing Context (Interfaces / Schemas) | Paste relevant database models, TypeScript interfaces, or helper signatures. | Prevents the model from hallucinating column names, imports, or helper functions that do not exist. | *"Here is our existing User SQLAlchemy model: <code>...</code>."* |
| 5. Anti-Laziness & Output Rules | Ban placeholders (// TODO, # ...) and control whether prose explanations are included. | Forces complete, copy-pasteable implementation instead of half-finished skeletons. | *"Output complete, runnable code in a single block. Never use ... or TODO placeholders."* |

### 2. Code Generation Prompt Template

```xml
<role>
You are a senior backend engineer writing clean, production-grade code.
</role>

<stack>
- Language: Python 3.12
- Libraries: FastAPI, Pydantic v2, httpx (async), pytest
</stack>

<context>
Existing Pydantic schema in our codebase:
class WebhookEvent(BaseModel):
    event_id: str
    payload: dict
    timestamp: int
</context>

<task>
Implement a FastAPI POST endpoint `/webhooks/payments` and a helper function `verify_signature(raw_body: bytes, signature: str, secret: str) -> bool` using HMAC-SHA256.
</task>

<requirements>
- Verify the `X-Webhook-Signature` header using constant-time comparison (`hmac.compare_digest`).
- Return HTTP 401 if the signature is missing or invalid.
- Return HTTP 200 `{"status": "accepted", "event_id": event.event_id}` on success.
- Include 2 concise `pytest` unit tests covering a valid signature and a tampered payload.
</requirements>

<output_rules>
- Provide complete, runnable code with all imports and type hints.
- Do not use placeholders like `# ...` or `pass`.
- Keep explanations under 3 bullet points after the code block.
</output_rules>
```

### 3. High-Leverage Techniques for Complex Coding Tasks

- **Test-Driven Prompting (TDD).** Paste your failing unit tests first and instruct the model: *"Write the implementation that makes all of these tests pass."* Concrete assertions eliminate 90% of specification ambiguity.
- **Plan Before Coding (Two-Step Workflow).** For multi-file features or tricky algorithms, ask the model to outline the architecture, data flow, and edge cases first—or use a **reasoning model**

(like o3 or Claude Extended Thinking) to trace logic before emitting code.

- **Diff / Patch Output for Edits.** When modifying an existing 500-line file, instruct the model to output only the changed functions or a unified diff rather than rewriting the whole file (which wastes tokens and risks accidental deletions).
- **Self-Review Pass.** On security-critical code (auth, SQL queries, payments), add a second prompt: *"Review the code above specifically for SQL injection, race conditions, and unhandled exceptions, then output the hardened version."*

### 4. Common Pitfalls to Avoid

- **Vague "Make It Better" Prompts.** Asking *"Optimize this function"* without stating *what* to optimize (memory footprint, CPU time, SQL query count, or readability) leads to arbitrary rewrites.
- **Outdated Library Hallucinations.** LLMs trained before a major framework release often invent outdated method names. Always paste a 5-line snippet of the current library's syntax if you are using a fast-moving SDK.

## Prompting for code generation and review

Effective prompting for **code generation and review** treats the LLM like a senior engineer working from a strict technical specification rather than a casual chat partner. Because software has zero tolerance for hallucinated APIs or subtle edge-case bugs, pairing **precise context contracts** for generation with **adversarial, checklist-driven criteria** for review produces reliable, production-ready code.

### 1. Code Generation vs. Code Review: Core Prompting Differences

| Dimension | Code Generation Prompting | Code Review Prompting |
| --- | --- | --- |
| Primary Goal | Produce complete, runnable, idiomatic code that fits existing interfaces. | Uncover hidden bugs, security flaws, race conditions, and performance traps. |
| Essential Input Context | Tech stack versions, exact function signatures, schemas, and edge cases. | The target code/diff, runtime environment, scale expectations, and surrounding types. |
| Best Persona Framing | *"Senior [Language] engineer writing production-grade, maintainable code."* | *"Skeptical principal security & reliability auditor looking for ways this breaks in prod."* |
| Key Guardrail | Ban lazy placeholders (// TODO, # ...) and enforce complete error handling. | Ban minor style nitpicks unless requested; require concrete proof/triggers for every bug flagged. |

### 2. High-Signal Code Generation Prompting

To prevent the model from guessing library versions or emitting half-finished skeletons, structure generation prompts around five anchors:

- **Lock Versions & Contracts.** State exact runtime and SDK versions (e.g., Python 3.12, FastAPI 0.115, Pydantic v2) alongside exact input/output types.
- **Provide Neighboring Code.** Paste existing database models, interfaces, or helper signatures so the model wires into real symbols instead of inventing new ones.
- **Define Failure Modes.** Explicitly specify timeouts, empty-input behavior, retry policies, and exceptions to raise.
- **Use Test-Driven Prompting.** Whenever possible, paste 2–3 unit tests first and instruct the model to write the implementation that passes them.
- **Enforce Anti-Laziness Rules.** Explicitly forbid # ... rest of implementation or pass stubs.

```xml
<role>
You are a senior backend engineer writing clean, production-grade TypeScript.
</role>

<stack>
Node.js 22, TypeScript 5.6 (strict mode), Prisma ORM, Zod.
</stack>

<context>
Existing Zod schema:
const TransferSchema = z.object({
  fromAccountId: z.string().uuid(),
  toAccountId: z.string().uuid(),
  amountPaise: z.number().int().positive(),
});
</context>

<task>
Implement `async function executeTransfer(rawInput: unknown): Promise<{ transferId: string }>` using a Prisma interactive transaction.
</task>

<requirements>
- Validate `rawInput` with `TransferSchema`; throw `ValidationError` on failure.
- Reject self-transfers (`fromAccountId === toAccountId`).
- Check sufficient balance inside the transaction and decrement/increment atomically.
- Catch Prisma serialization/deadlock errors and retry up to 2 times.
</requirements>

<output_rules>
- Output complete, runnable code with all imports and types.
- Do not use `// TODO` or `...` placeholders.
- Keep explanations under 3 short bullets after the code block.
</output_rules>
```

### 3. Adversarial Code Review Prompting

Default LLM personas are polite and agreeable, which often causes them to rubber-stamp buggy code or obsess over variable naming while missing SQL injection or N+1 queries. Fix this by giving the model a **prioritized defect rubric** and requiring **evidence before suggestions**.

- **Assign an Adversarial Auditor Persona.**

Explicitly instruct the model to try to *break* the code under high concurrency, malformed inputs, or network failures.

- **Constrain Review Categories.** Focus the model on high-impact dimensions: **Correctness & Edge Cases**, **Security & Auth**, **Concurrency & State**, and **Performance / Memory**.
- **Require Severity + Reproduction Trigger.** Force the model to explain *how* an attacker or edge case triggers each issue so it does not hallucinate false positives.
- **Demand Minimal Diffs.** Ask for targeted patches rather than rewriting untouched functions.

```xml
<role>
You are a principal software architect and application security auditor conducting a strict pull-request review.
</role>

<context>
This Python service handles webhook payouts in production (~500 requests/sec) behind a load balancer.
</context>

<review_rubric>
Audit the code strictly for:
1. Security flaws (injection, auth bypass, secret leakage, SSRF)
2. Concurrency & idempotency bugs (race conditions, duplicate processing)
3. Resource & performance traps (N+1 queries, unbounded memory, missing timeouts)
4. Silent error handling or edge-case crashes (`None`, empty lists, integer overflow)
</review_rubric>

<rules>
- Ignore formatting, docstrings, and minor naming preferences.
- Only report issues with high confidence; if no real defects exist, output "LGTM — no critical issues found."
- For every issue found, specify: Severity (Critical/High/Medium), Exact Line/Block, How It Fails, and the Minimal Fixed Code.
</rules>

<code>
[PASTE CODE OR GIT DIFF HERE]
</code>
```

### 4. Pro Workflow: The Generate → Review → Harden Loop

For critical modules (payments, authentication, data migrations), chain two prompts—or pair a fast model with a reasoning model:

1. **Pass 1 (Generate):** Generate the implementation and unit tests from your specification.
2. **Pass 2 (Adversarial Review):** Feed that generated code into a fresh session using the **Code Review Template** above (ideally using a reasoning model like **o3** or **Claude Extended Thinking** to trace edge cases).
3. **Pass 3 (Patch):** Apply only the verified Critical/High fixes without altering working logic.
