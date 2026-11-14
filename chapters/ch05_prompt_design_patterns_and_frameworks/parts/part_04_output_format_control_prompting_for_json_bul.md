# Chapter 5 - Part 4: Output Format Control: prompting for JSON, bullet lists, code, and tables

> Chapter 5: Prompt Design Patterns and Frameworks

**Output Format Control** is the set of prompting and decoding techniques used to force an LLM to return responses in a predictable, machine-readable, or visually consistent layout—such as strict **JSON**, **XML**, **CSV**, **Markdown tables**, or fixed-length bullet lists—rather than unpredictable conversational prose.

### 1. Why Output Format Control Matters

In production applications, an LLM's output rarely goes straight to a human reader—it usually feeds into downstream code, databases, or UI components:

- **Prevents Parser Crashes.** A single stray conversational sentence (*"Here is your JSON:"*) or unclosed bracket breaks json.loads() and crashes backend pipelines.
- **Reduces Token Costs & Latency.** Enforcing concise schemas or bullet limits prevents models from wasting hundreds of output tokens on polite introductions and summaries.
- **Improves Reasoning Accuracy.** Forcing a model to populate specific fields (like "evidence" before "verdict") acts as a lightweight Chain-of-Thought scaffold that reduces hallucinations.

### 2. Three Levels of Output Format Control

| Control Method | How It Works | Reliability | Best Use Case |
| --- | --- | --- | --- |
| 1. Prompt-Level Formatting | Describing the target layout using explicit rules, negative constraints (*"No markdown fences"*), and **1–3 Few-Shot examples**. | **Moderate (~85–95%)** — occasional formatting drift on edge cases. | Human-readable layouts (Markdown tables, fixed bullet templates, custom plain-text reports). |
| 2. Prefilling (Assistant Turn Start) | Seeding the very first token of the assistant's reply (e.g., prefilling { or <response>) so the model is forced to continue inside that syntax. | **High (~98%+)** | APIs supporting assistant prefill (such as Anthropic Claude or self-hosted vLLM/SGLang). |
| 3. Constrained Decoding (Structured Outputs) | Modifying token probabilities at inference time using a **Finite State Machine (FSM) / Context-Free Grammar** so any token violating your JSON Schema or regex gets masked out (logit = -∞). | **100% Guaranteed** | Production APIs, function/tool calling, database ingestion, and strict Pydantic/JSON Schema extraction. |

### 3. Practical Prompting Patterns for Clean Formats

When you are not using API-level JSON Schema enforcement, combine these four prompt rules to eliminate formatting drift:

- **Show an Exact Skeleton Template.** Models imitate visual templates far better than prose descriptions:

Output strictly using this exact template and nothing else:

Status: [PASS | FAIL]

Confidence: [0-100]%

Reason: <one sentence under 15 words>

- **Use Positive + Negative Framing Together.** State what to output *and* explicitly ban conversational wrappers: *"Return raw JSON only. Do not include markdown code fences (```json), greetings, or explanations."*
- **Order Fields Intentionally.** In JSON extraction, put "reasoning" or "quote" *before* "classification" or "score". Because LLMs generate left-to-right, writing the supporting evidence first improves the accuracy of the final label.
- **Include a Null / Fallback Rule.** Always define what the format should look like when data is missing (e.g., *"Use null for missing fields; never invent values or omit keys"*).

### 4. Production Code Example: 100% Guaranteed Structured Output

Modern APIs (OpenAI, Gemini, Anthropic, and vLLM/Outlines) support passing a **Pydantic model** or **JSON Schema** directly into the request so constrained decoding guarantees valid syntax:

```python
from pydantic import BaseModel, Field
from openai import OpenAI

class InvoiceExtraction(BaseModel):
    vendor_name: str
    total_amount_inr: float
    gst_number: str | None = Field(description="15-character GSTIN if present, else null")
    is_paid: bool

client = OpenAI()

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Extract structured invoice fields accurately."},
        {"role": "user", "content": "Invoice from CloudOps India Pvt Ltd (GSTIN: 27AABCU9603R1ZM) for ₹45,200. Status: Paid."}
    ],
    response_format=InvoiceExtraction,
)

data = response.choices[0].message.parsed
print(data.vendor_name, data.total_amount_inr)
```

## Prompting for JSON

**Prompting for JSON** is the practice of instructing and constraining an LLM to output clean, syntactically valid JSON objects that can be parsed directly by json.loads() without manual cleanup or crash-prone regex hacks. In production systems, reliable JSON output relies on combining **explicit schema definitions**, **strict negative constraints**, and—whenever supported by your API—**native Structured Outputs (constrained decoding)**.

### 1. The 5 Rules of Reliable JSON Prompts

When instructing a model via text alone (or reinforcing an API schema), include these five elements:

- **Define the Exact Schema & Data Types.** Explicitly list every key name, its expected data type (string, number, boolean, array, null), and allowed enum values rather than saying *"Return the result as JSON."*
- **Ban Markdown Code Fences and Chatter.** LLMs love wrapping JSON inside ```json ... ``` blocks or adding *"Here is your JSON:"*—both of which break json.loads(). Explicitly state: *"Return raw, valid JSON only. Do not include markdown fences, backticks, or explanatory text."*
- **Specify null Rules for Missing Data.** Tell the model how to handle absent values (*"If a field is not mentioned in the text, set its value to null. Never omit keys or invent values"*).
- **Put Reasoning Keys Before Answer Keys.** Because LLMs generate tokens sequentially from left to right, placing "reason" or "evidence" *before* "category" or "is_valid" lets the model think briefly before locking in its final label.
- **Include 1 Concrete Example.** Showing a single 4-line example of the exact JSON shape eliminates almost all structural ambiguity.
3. **Copy-Pasteable JSON Prompt Template**

```text
<task>
Extract customer order details from the message below into a single JSON object.
</task>

<schema>
{
  "customer_name": "string or null",
  "items": ["array of strings, empty array if none"],
  "total_amount_inr": "number or null (digits only, no currency symbol)",
  "urgency": "one of: 'low', 'medium', 'high'",
  "notes": "string or null"
}
</schema>

<rules>
- Output strictly raw, valid JSON matching the schema above.
- Do NOT wrap the output in ```json markdown fences or add any text before or after the JSON.
- Escape any double quotes inside string values properly.
</rules>

<input>
Hi, this is Rohan Sharma. Please deliver 2 wireless routers and 1 LAN cable urgently today. Budget is around ₹8,500.
</input>
```

### 3. Three Levels of Enforcement in Code

| Method | How to Use It | Reliability | Trade-Offs |
| --- | --- | --- | --- |
| Prompt-Only JSON | Use the template above with temperature=0. | **~90–95%** | Works on any model/API, but long strings with unescaped quotes (") can still occasionally break parsing. |
| JSON Mode (response_format={"type": "json_object"}) | Built-in API flag in OpenAI, Gemini, Mistral, and vLLM. | **~99% valid syntax** | Guarantees valid JSON syntax, **but does not enforce your exact key names or data types** unless paired with a schema. |
| Structured Outputs / JSON Schema (Pydantic) | Pass a Pydantic class or JSON Schema (response_format / response_schema). | **100% guaranteed** | Uses constrained decoding (masking invalid tokens at inference) to guarantee both valid JSON *and* exact keys/types. |

### 4. Common JSON Failure Traps & Fixes

- **Unescaped Quotes Inside Long Text.** If your JSON requires a field containing multi-paragraph prose or code snippets, models frequently forget to escape inner double quotes (\"), corrupting the JSON. **Fix:** If you are extracting long text or code, use **XML tags** (<code_snippet>...</code_snippet>) instead of JSON—XML doesn't require escaping quotes or newlines.
- **Truncated JSON on Max Tokens.** If the model hits max_tokens mid-generation, you get an unclosed { that fails to parse. **Fix:** Set a generous max_tokens ceiling and keep array sizes bounded (*"Extract up to 5 key points"*).

Controlling an LLM's output format relies on **explicit structural templates**, **strict negative constraints** (banning conversational filler), and **format-specific guardrails**. Each output format—**JSON, bullet lists, code, and tables**—has distinct failure modes and requires tailored prompting patterns to stay clean and parseable.

### Comparison of Output Format Controls

| Format | Primary Risk / Failure Mode | Key Prompting Control | Best Enforcement Method |
| --- | --- | --- | --- |
| JSON | Wrapping in ```json fences, unescaped quotes ("), or hallucinated keys. | Define exact keys/types + ban markdown fences and chatter. | **Structured Outputs / JSON Schema** (Constrained Decoding). |
| Bullet Lists | Endless rambling, inconsistent nesting, or introductory/closing fluff. | Cap item count + set word limits per bullet + show a 1-item template. | Explicit skeleton pattern + negative constraints. |
| Code | Incomplete snippets (// ... rest of code), outdated libraries, or surrounding prose. | Specify language/version + ban placeholders + demand full runnable code. | XML tags (<code>...</code>) or fenced block rules. |
| Tables | Broken pipe (` | `) alignment, overly wide cells, or missing columns. | Declare exact column headers upfront + cap cell word count. |

### 1. Prompting for JSON (Machine-Readable Data)

When extracting data for backend APIs or databases, specify exact data types and forbid conversational wrappers.

- **Key Rules:** Define every key name, type, and null fallback; put reasoning keys *before* answer keys; ban ```json backticks if passing directly to json.loads().
- **Copy-Paste Template:**

```text
Extract the details into strictly valid, raw JSON matching this schema:
{"reason": "string", "category": "Bug | Billing | Other", "priority": 1-5, "customer_email": "string or null"}
Rules: Output raw JSON only. Do not include markdown fences, backticks, or any text before or after the JSON object.
```

### 2. Prompting for Bullet Lists (Scannable Summaries)

Without strict bounds, models write bloated paragraphs disguised as bullets and pad responses with intros and conclusions.

- **Key Rules:** Cap the exact number of bullets, limit sentence length, enforce bold lead-ins, and explicitly ban intro/outro lines.
- **Copy-Paste Template:**

```text
Summarize the incident report into 4 to 5 bullet points.
Format each bullet strictly as: * **[Key Term]:** [One clear sentence under 20 words].
Rules: Start immediately with the first bullet. Do not include an introductory sentence, sub-bullets, or a concluding summary.
```

### 3. Prompting for Code (Runnable Implementation)

LLMs often save tokens by inserting lazy placeholders like # TODO: add error handling here or wrapping code in lengthy tutorials.

- **Key Rules:** Lock in the exact language, framework version, and dependencies; forbid truncation placeholders; isolate code from explanation.
- **Copy-Paste Template:**

```text
Write a complete, production-ready Python 3.12 function using httpx and pydantic v2 to fetch and validate user profiles.
Rules:
- Output only the executable code inside a single ```python block.
- Include all imports, type hints, and try/except timeout handling.
- Never use placeholders like # ... or pass. Do not add explanations before or after the code block.
```

### 4. Prompting for Tables (Side-by-Side Comparisons)

Markdown tables break easily when models invent extra columns or write multi-paragraph cells.

- **Key Rules:** Provide the exact Markdown header row and separator row (| :--- |) directly in your prompt so the model simply fills in the rows.
- **Copy-Paste Template:**

```text
Compare Redis, Memcached, and DragonflyDB across latency, persistence, and multi-threading.
Output strictly as a Markdown table using these exact headers:
| Engine | Latency Profile | Persistence Support | Multi-Threading | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
Rules: Keep every cell under 12 words. Do not add text above or below the table.
```
