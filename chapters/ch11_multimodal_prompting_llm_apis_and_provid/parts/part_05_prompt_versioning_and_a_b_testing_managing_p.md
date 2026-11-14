# Chapter 11 - Part 5: Prompt Versioning and A/B Testing: Managing prompts like code, measuring which version works better

> Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

**Prompt Versioning** is the practice of systematically tracking, storing, testing, and managing changes to prompts over time—treating prompts as **first-class software artifacts** rather than hardcoded strings scattered inside application code.

Because small tweaks to a prompt's wording, examples, or temperature can drastically alter model accuracy, latency, or JSON formatting, versioning ensures teams can deploy updates safely and roll back instantly if quality regresses.

### 1. Why Prompt Versioning Matters

- **Non-Deterministic Behavior:** Unlike traditional code where a change breaks at compile time, a minor prompt edit can silently degrade edge-case accuracy across thousands of production requests.
- **Model Coupling:** Prompts are tightly coupled to specific model snapshots (e.g., gpt-4o-2024-08-06 vs. gemini-2.5-flash). Upgrading a model often requires adjusting and versioning the accompanying prompt together.
- **Auditability & Compliance:** In regulated industries (finance, healthcare, legal), teams must know the exact prompt template, system instructions, and model parameters that produced a historical decision.
- **Decoupling Deploys:** Separating prompt versions from application code lets product managers or prompt engineers iterate on wording without waiting for a full backend CI/CD redeployment.

### 2. Core Components of a Prompt Version

A complete prompt version snapshot captures more than just text—it bundles the entire inference configuration:

- **Prompt Template & Variables:** System prompt, user template, and placeholder variables (e.g., {{user_query}}, {{context}}).
- **Few-Shot Examples:** Exact input-output examples embedded in the prompt.
- **Model & Hyperparameters:** Target model ID (model), temperature, top_p, max_tokens, and reasoning settings.
- **Schemas & Tool Definitions:** Attached JSON output schemas or function-calling definitions.
- **Deployment Tags / Aliases:** Labels such as dev, staging, production, or canary-10% that point to immutable version numbers (v1, v2, v3).

### 3. Common Prompt Versioning Workflows

| Approach | How It Works | Best Used For |
| --- | --- | --- |
| Code-as-Prompt (Git) | Prompts live in dedicated .yaml, .json, or .prompt files inside your Git repository alongside application code. | Small-to-medium engineering teams wanting PR reviews, git diff history, and tight CI/CD coupling. |
| Prompt Management Platforms | Dedicated registries (such as **Langfuse**, **LangSmith**, **Braintrust**, or **PromptLayer**) store immutable prompt versions with UI editors, aliases, and SDK caching. | Cross-functional teams where non-engineers edit prompts, or apps needing instant rollback and live A/B testing without code deploys. |

### 4. Production Best Practices

- **Never Mutate Deployed Versions:** Treat every published prompt version (v1.2) as **immutable**. Any edit creates a new version (v1.3) so historical logs remain reproducible.
- **Gate Promotions with Automated Evals:** Before moving a production alias from v2 to v3, run an automated evaluation suite (golden dataset + LLM-as-a-Judge) to verify accuracy hasn't regressed.
- **Log Version IDs in Traces:** Always record prompt_name and prompt_version inside your observability logs so you can compare latency, token cost, and user feedback across versions.
- **Use Gradual Rollouts (Canary / A/B):** Route 5%–10% of live traffic to a new prompt version first to monitor real-world edge cases before shifting 100% of traffic.

## Why prompts need version control

Prompts need version control because they act as the core "source code" of an LLM application, yet they behave unpredictably—meaning even a single-word edit can silently break production logic, alter formatting, or degrade accuracy without throwing a traditional syntax error.

### 1. Silent Regressions & Fragility ("Butterfly Effect")

- **No Compiler Errors:** In traditional code, a bad edit fails at compile time or crashes a unit test immediately. In prompts, adding one sentence to fix Edge Case A can quietly break Edge Case B while still returning HTTP 200 OK.
- **Instant Rollbacks:** When a prompt update causes hallucinations or drops conversion rates in production, version control lets teams revert to the last known-good version (v2 → v1) in seconds without rewriting code.

### 2. Tight Coupling to Specific Models

- **Model Drift & Upgrades:** Prompts tuned for one model (e.g., gpt-4o) often behave differently when switched to another model (e.g., gemini-2.5-flash or claude-sonnet-4-6).
- **Bundled Configuration:** Version control tracks the prompt text **together with** its exact model snapshot, temperature, max_tokens, and JSON schema so a prompt is never separated from the environment it was tested on.

### 3. Reproducibility & Debugging in Production

- **Tracing Historical Failures:** If a user reports a bad AI response from three days ago, logs are useless unless you know the exact prompt template that generated it.
- **Comparing Metrics Across Versions:** Tagging every API trace with prompt_version lets teams measure whether v3 actually lowered token costs, reduced latency, or improved user satisfaction compared to v2.

### 4. Team Collaboration & Auditability

- **Safe Multi-Person Editing:** Without version control, developers, product managers, and domain experts overwrite each other's changes in scattered strings or spreadsheets.
- **Code Review & Accountability:** Storing prompts in version control enables pull-request diffs, peer reviews, approval gates, and a full audit trail of *who* changed *what* and *why*—essential for regulated industries like finance and healthcare.

### 5. Decoupling Prompt Iteration from App Deploys

- **Faster Experimentation:** Treating prompts as versioned assets (with deployment aliases like dev, staging, and prod) allows teams to run A/B tests and ship prompt improvements independently without redeploying the entire backend service.

## Managing prompts like code

**Managing prompts like code** (often called **PromptOps** or **Prompt-as-Code**) means treating prompts with the exact same software engineering rigor as Python or JavaScript source files—storing them in structured repositories, reviewing changes via pull requests, testing them automatically in CI/CD, and deploying them with semantic versions.

### 1. Core Principles of Prompt-as-Code

- **Extract Prompts Out of Application Logic:**

Never bury long multi-line f-strings inside business logic files. Store prompts in dedicated, human-readable templates (such as .yaml, .json, or .prompt files) so changes are clean and easy to inspect.

- **Bundle Prompts with Model Configs:** A prompt never runs in isolation. Store the text template alongside its required model, temperature, max_tokens, tools, and output schema inside the same versioned file.
- **Strict Variable Contracts:** Define explicit input variables (e.g., {{customer_name}}, {{order_history}}) and validate them at runtime—just like typed function parameters—so missing variables fail loudly before calling the API.
- **Pull Requests & Diff Reviews:** Every prompt edit goes through a Git branch and pull request, allowing teammates to review exact line-by-line diffs (git diff) and leave comments on edge cases before merging.

2. Example: A Structured Prompt-as-Code File (**invoice_extractor.yaml**)

```text
id: invoice_extractor
version: 1.4.0
description: Extracts structured line items and tax totals from vendor invoices.

model_config:
  provider: openai
  model: gpt-4o-2024-08-06
  temperature: 0.0
  max_tokens: 1500

input_variables:
  - currency_code
  - document_text

messages:
  - role: system
    content: |
      You are a precise financial data extractor.
      Extract all invoice fields in {{currency_code}}.
      If a field is missing or illegible, output null. Never guess.
  - role: user
    content: |
      Extract the invoice details from the document below:
      {{document_text}}
```

### 3. The CI/CD Lifecycle for Prompts

| Stage | Traditional Software Code | Prompt-as-Code Equivalent |
| --- | --- | --- |
| Authoring | Writing functions in an IDE | Editing .yaml / .prompt templates with Jinja2 or Mustache placeholders |
| Linting & Static Checks | ruff, eslint, mypy | Checking valid YAML syntax, verifying no unclosed {{variables}}, and ensuring token length stays within budget |
| Automated Testing | Unit & integration tests (pytest) | Running Automated Evals against a golden dataset (checking JSON validity, accuracy scores, and latency) |
| Release & Rollback | Git tags (v1.4.0) & blue/green deploys | Promoting immutable tags (staging → production) with instant rollback on regression |
| Observability | Application logs & APM traces | Logging prompt_id + prompt_version on every LLM request to track cost and quality in production |

### 4. Balancing Git vs. Dynamic Prompt Registries

- Pure Git Approach: Best when engineering owns all prompts and wants zero external dependencies—every prompt change triggers a standard CI/CD pipeline.
- Hybrid Registry Approach (e.g., Langfuse, PromptLayer, Braintrust): Best when product managers or domain experts need to tweak wording and run A/B tests quickly without waiting for full backend deployments, while syncing snapshots back to Git for auditability.

## A/B testing prompts

**A/B testing prompts** is the practice of splitting live production traffic between two or more prompt versions (such as v1 Control vs. v2 Variant) to measure which version performs better against real-world user behavior, accuracy metrics, latency, and token cost.

While offline evaluations (evals) catch obvious bugs before deployment, A/B testing reveals how prompts handle messy, unpredictable live inputs at scale.

### 1. How Prompt A/B Testing Works in Production

1. **Traffic Splitting (Routing):** When a request arrives, your application or prompt gateway deterministically assigns it to a variant (e.g., 90% to prompt_v1 and 10% to prompt_v2) using a hash of user_id or session_id so the same user experiences consistent behavior across turns.
2. **Trace & Version Logging:** Every response is tagged in your observability logs with the exact prompt_version, model, latency_ms, and token_cost.
3. **Outcome Collection:** Your system records downstream signals—both automated checks and real user reactions—mapped back to each prompt version.
4. **Statistical Comparison & Promotion:** Once enough samples are collected to reach statistical significance, the winning prompt is promoted to 100% of traffic (or rolled back if metrics degrade).

### 2. Key Metrics to Track in Prompt Experiments

| Metric Category | What to Measure | Why It Matters |
| --- | --- | --- |
| User Outcome Signals | Thumbs up/down, task completion rate, copy/accept rate (for code/drafts), or human escalation rate. | Measures true end-user value rather than synthetic benchmark scores. |
| Automated Quality Scores | Schema validation pass rate, hallucination rate (via async LLM-as-a-Judge), and tool-call success rate. | Catches silent formatting breaks or factual drift on live traffic. |
| Operational & Cost Metrics | Input/output token counts, **TTFT** (Time to First Token), total latency, and cost per request. | A prompt that is 2% more accurate but 3× more expensive or slower may lose overall. |

### 3. Best Practices for Reliable Prompt A/B Tests

- **Change One Variable at a Time:** Avoid changing the prompt wording, the few-shot examples, and the underlying model (gpt-4o → gemini-2.5-flash) simultaneously, or you will not know which change caused the metric shift.
- **Start with Canary Rollouts (5%–10%):** Never split traffic 50/50 on an untested prompt. Route 5%–10% first to catch severe edge-case failures with minimal blast radius.
- **Use Sticky Assignment for Multi-Turn Chats:** Route by conversation_id or user_id rather than random per-request coin flips so a multi-turn conversation does not switch personalities or formatting rules mid-chat.
- **Consider Shadow Testing for Zero-Risk Checks:** For background extraction or classification pipelines, run prompt_v2 asynchronously alongside prompt_v1 on the same live inputs without showing v2 to users—letting you compare outputs head-to-head with zero user impact.

## Quick Demo

1. **A 1024x1024 image sent with detail: high costs more input tokens than the same image sent with detail: low. Why - what is the model actually doing differently in each mode?**

A 1024×1024 image sent with detail: high costs significantly more input tokens than detail: low because detail: low shrinks the entire image into a single low-resolution thumbnail, whereas **detail: high slices the image into a grid of separate high-resolution tiles** and encodes every tile individually.

## What the Model Does in Each Mode

- **detail: low (Single Global Overview):**
  - **Resizing:** The API immediately downsamples the 1024×1024 image into a single fixed 512×512 thumbnail.
  - **Tokenization:** Only that one 512×512 square is passed through the vision encoder, generating a flat, fixed token budget (typically **85 tokens** in OpenAI's vision pricing).
  - **Trade-off:** Fine details like small text, serial numbers, or dense chart labels become blurry and unreadable, though broad shapes, colors, and overall scene context remain clear.
- **detail: high (Global Thumbnail + High-Res Tile Grid):**
  - **Step 1 — Global Context Thumbnail:** First, the model still creates the same downsampled 512×512 overview image (**85 tokens**) so it understands the big picture and how everything connects spatially.
  - **Step 2 — High-Res Tiling:** Next, the API takes the full 1024×1024 image and slices it into a **2×2 grid of four 512×512 square tiles** (four quadrants: top-left, top-right, bottom-left, bottom-right).
  - **Step 3 — Per-Tile Encoding:** Each of those four 512×512 tiles is encoded at full crisp resolution (costing **170 tokens per tile** × 4 tiles = **680 tokens**).
  - **Total Token Cost:** 85 (overview) + 680 (4 tiles) = 765 input tokens—exactly **9× more tokens** than detail: low for the exact same 1024×1024 image.

## Summary Comparison (1024×1024 Image)

| Setting | Image Processing Steps | Visual Detail Preserved | Typical Input Token Cost |
| --- | --- | --- | --- |
| detail: low | Downsampled to one 512×512 image | Broad scene, objects, and colors only; fine text is lost | **85 tokens** (flat cost) |
| detail: high | One 512×512 overview + four 512×512 high-res crops | Full native sharpness across every quadrant for OCR, tables, and charts | **765 tokens** (85 + 4 × 170) |

2. **You are building a tool that reads scanned receipts to extract the total amount. During testing, the model sometimes returns 87.50 when the receipt shows 87.60. What is the likely cause and how would you work around it?**

Misreading 87.60 as 87.50 happens because **small, low-contrast, or crumpled receipt characters get compressed during vision patch encoding**, making visually similar digits (6 vs 5, or 8 vs 0) blur together so the model falls back on statistical guessing.

### 1. Likely Causes

- **Insufficient Image Resolution / Patch Compression:** Vision encoders slice images into small pixel patches (e.g., 14×14 pixels). On thermal paper receipts, faded ink, low DPI scans, or detail: low settings blur the tiny gap in a 6, making it look identical to a 5.
- **Visual Noise & Skew:** Receipt creases, shadows, background clutter, or tilted angles distort character shapes across patch boundaries.
- **Lack of Cross-Verification:** Extracting only the final total field in isolation prevents the model from checking whether the numbers actually add up mathematically.

### 2. How to Work Around It (Engineering & Prompting Fixes)

- **Image Preprocessing & Resolution Controls:**
  - **Force detail: high (High Resolution):** Ensure the API runs in high-detail tile mode rather than downsampling the receipt into a blurry thumbnail.
  - **Crop & Deskew Before Sending:** Automatically crop out empty background space around the receipt and straighten tilted scans so maximum pixel resolution is dedicated to the text.
  - **Enhance Contrast:** Convert faded thermal scans to high-contrast grayscale or apply adaptive thresholding so faint ink strokes stand out sharply.
- **Prompting & Schema Workarounds (Math Self-Verification):**
  - **Extract Line Items + Subtotal + Tax First:** Design your Pydantic/JSON schema to extract all line_items, subtotal, and tax *before* the total_amount field. Because LLMs generate tokens left-to-right, extracting the components first anchors the model's reasoning to the true sum (87.60).
  - **Add a Verification Field:** Include a math_check_notes or calculated_sum field in your schema instructing the model to sum the extracted line items and compare them against the printed total.
- **Deterministic Code Validation (Post-Processing):**
  - **Programmatic Arithmetic Check:** In your Python code, sum the extracted line_items + tax and compare it against total_amount. If calculated_total != extracted_total (e.g., 87.60 != 87.50), flag the receipt for a high-resolution re-crop retry or human-in-the-loop review.
3. **Write the key structural differences between an OpenAI chat.completions.create call and an Anthropic messages.create call. Name at least three fields that differ.**

The core structural difference between OpenAI's chat.completions.create and Anthropic's messages.create is how they handle system instructions, required token limits, and content block formatting. OpenAI places system instructions inside the messages list and treats max_tokens as optional, whereas Anthropic separates system instructions into a top-level parameter, mandates max_tokens, and enforces strict user/assistant message alternation.

Key Structural Differences (Side-by-Side)

| Request / Response Field | OpenAI (client.chat.completions.create) | Anthropic (client.messages.create) |
| --- | --- | --- |
| 1. system Instructions | Passed inside the messages array as the first item with {"role": "system", "content": "..."} (or role: "developer"). | Passed as a top-level parameter (system="...") completely outside the messages array. |
| 2. max_tokens | Optional. If omitted, the model generates up to its default maximum output limit. | Strictly Required. Omitting max_tokens raises an immediate 400 Bad Request validation error. |
| 3. Tool Definitions & Results | Tools use parameters inside a nested function object. Tool outputs are sent back as a separate message with role: "tool" and tool_call_id. | Tools use input_schema at the top level of the tool dict. Tool outputs are sent back inside a role: "user" message containing a tool_result content block (tool_use_id). |
| 4. Response Text Location | Nested inside a choices list: response.choices[0].message.content (a plain string). | Nested inside a typed content block array: response.content[0].text (alongside thinking or tool_use blocks). |
| 5. Message Role Alternation | Flexible; allows consecutive user messages or starting with system. | Strictly requires user and assistant roles to alternate (and the first message must be role: "user"). |

## Side-by-Side Code Comparison

## OpenAI (chat.completions.create):

response = openai_client.chat.completions.create(

model="gpt-4o",

messages=[

{"role": "system", "content": "Be concise."},

{"role": "user", "content": "Hello!"}

]

)

print(response.choices[0].message.content)

## Anthropic (messages.create):

response = anthropic_client.messages.create(

model="claude-sonnet-4-6",

max_tokens=1024,  # Required field

system="Be concise.",  # Top-level parameter

messages=[

{"role": "user", "content": "Hello!"}

]

)

print(response.content[0].text)

4. **In the streaming demo, each chunk contains delta.content with only the new tokens. Why does the API send deltas rather than the full accumulated text in each chunk?**

The API sends only delta.content (the newly generated tokens) rather than the full accumulated text to avoid quadratic bandwidth growth, reduce network latency, and minimize client/server memory overhead.

### 1. Preventing Quadratic Bandwidth Growth (O(N²))

- **The Math of Resending Everything:** If a model generates a 1,000-token response and sends the entire text on every single step, Chunk 1 sends 1 token, Chunk 2 sends 2 tokens, Chunk 3 sends 3 tokens, and Chunk 1,000 sends 1,000 tokens. That transmits roughly **500,500 tokens over the network** instead of **1,000 tokens**.
- **Linear Scaling with Deltas (O(N)):** Sending only the new delta keeps every Server-Sent Event (SSE) packet tiny (just a few bytes) regardless of whether the response is 50 tokens or 10,000 tokens long.

### 2. Lower Latency & Faster Inter-Token Delivery

- **Smaller Payloads Travel Faster:** Tiny JSON packets serialize, transmit over TCP/TLS, and parse in the browser almost instantaneously, keeping **Inter-Token Latency (ITL)** smooth and preventing network congestion on mobile or slow connections.

### 3. Simpler Client-Side Appending & Memory Efficiency

- **Direct UI Appending:** Frontend interfaces simply append each incoming delta string to the existing text buffer (full_text += chunk.delta.content) without needing to diff strings or re-render the entire message state from scratch on every token.
- **Stateless Server Streaming:** The inference engine pushes each newly decoded token out of the socket immediately and frees it from the outgoing network buffer rather than holding and re-serializing an ever-growing string on every step.
5. **You have a code review prompt that gets good results on security issues but consistently misses performance problems. You write v1.1 with more specific instructions. How do you measure whether v1.1 is actually better, not just longer?**

To measure whether v1.1 is genuinely better rather than just longer or noisier, you run a **controlled offline evaluation (eval) against a labeled golden dataset**—comparing v1.0 and v1.1 side-by-side across **performance recall, security regression, false-positive rate, and token cost**.

### 1. Build a Labeled Golden Dataset (Ground Truth)

Create a fixed test suite of 20–50 representative code snippets (PR diffs) divided into three clear buckets:

- **Known Performance Bugs:** Snippets containing planted bottlenecks (such as N+1 database queries, blocking I/O inside async loops, or O(n²) scans) with exact expected findings.
- **Known Security Bugs (Regression Suite):** Snippets with SQL injection, auth bypasses, or hardcoded secrets to ensure adding performance instructions didn't degrade v1.0's existing security accuracy.
- **Clean / Production-Ready Code (Negative Controls):** Well-written snippets with zero bugs to test whether v1.1 hallucinates fake performance issues just to obey the longer prompt.

### 2. Run Both Prompts Under Identical Conditions

- Run v1.0 and v1.1 against the exact same golden dataset using temperature = 0 (and the same model snapshot) so any score difference comes strictly from your prompt changes.
- Enforce a **Structured Output Schema** (e.g., [{"category": "security" | "performance", "line": int, "issue": str}]) so results can be graded objectively.

### 3. Measure Four Key Metrics (Beyond Output Length)

| Metric | What It Measures | Target for v1.1 |
| --- | --- | --- |
| Performance Recall | % of planted performance bugs caught (True Positives / Total Performance Bugs) | **Increases significantly** over v1.0 |
| Security Recall (Non-Regression) | % of planted security bugs still caught | **Stays flat or improves** (no regression) |
| Precision / False-Positive Rate | % of flagged issues that are real bugs (tested heavily on the clean code bucket) | **Remains high** (proves v1.1 isn't crying wolf) |
| Token Cost & Latency Delta | Average input + output tokens and response time per review | Stays within acceptable budget relative to the accuracy gain |

### 4. Grade Outputs Automatedly + Validate in Production

- **Deterministic + LLM-as-a-Judge Grading:** Match reported bug categories and line numbers programmatically where possible, and use a separate judge prompt (or human spot-check) to verify whether the model's explanation matches the ground-truth root cause.
- **Shadow or Canary Test:** Once v1.1 beats v1.0 on the offline golden set, run v1.1 in **shadow mode** on live pull requests—comparing developer acceptance/dismissal rates on real code before promoting v1.1 to 100% of traffic.
6. **You need to analyse a 40-page PDF report for tables and charts. What is the recommended approach, and when would you choose pdfplumber text extraction over sending page images?**

For a 40-page PDF report containing both **tables and charts**, the recommended approach is a hybrid triage-and-vision pipeline (render pages as images and use a Vision-Language Model for visual elements, while using lightweight text extraction to locate relevant pages first), rather than blindly sending all 40 pages at high resolution.

### 1. Recommended Approach for a 40-Page Report (Tables + Charts)

Sending 40 pages at detail: high in a single request wastes tokens, increases latency, and risks "lost in the middle" recall drops. Instead, follow a three-step pipeline:

1. **Page Triage (Filter Before Vision):**
  - Run a fast local scan using PyMuPDF (fitz) or pdfplumber—or inspect the Table of Contents—to identify which specific pages contain tables, charts, or embedded images.
  - For pages with pure narrative prose, extract text directly; reserve vision tokens strictly for pages containing charts, complex tables, or scanned graphics.
2. **Targeted Page-to-Image Rendering:**
  - Convert the identified visual pages to PNG/JPEG at **150–200 DPI** (or **300 DPI** for dense financial tables with tiny footnotes) and send them to a multimodal LLM with detail: high.
  - If a table splits across consecutive pages (e.g., Pages 14 and 15), send both page images together in the same prompt so the model merges the headers and rows accurately.
3. **Structured Output Extraction:**
  - Pair the page images with a strict Pydantic / JSON schema (including a page_number citation field) so extracted table rows and chart trends map directly into clean data structures.

### 2. When to Choose pdfplumber vs. Page Images (Vision)

| Factor | Choose pdfplumber (Text Extraction) | Choose Page Images (Multimodal Vision) |
| --- | --- | --- |
| Charts, Graphs & Diagrams | **Never.** pdfplumber cannot read bar heights, line trends, pie slices, or rasterized chart images. | **Always.** Vision models read plotted data, legends, axis labels, and visual callouts directly. |
| PDF Source Type | **Digitally generated PDFs** with embedded, selectable text streams and simple gridlines. | **Scanned PDFs**, photocopies, or flattened documents where text is stored as pixels rather than character objects. |
| Table Layout Complexity | Simple, clean, single-level tables with explicit cell borders and consistent column alignment. | Complex nested tables, borderless layouts, merged headers, rotated text, or tables mixed with visual icons/checkboxes. |
| Scale, Speed & Cost | Processing hundreds or thousands of standardized reports where near-zero latency and zero token cost are critical. | Analyzing nuanced reports where layout context matters more than paying a few cents per document in vision tokens. |

7. **Your Gemini API call works but you want to switch to Claude 3.5 Sonnet for a cost comparison. Your Gemini tool definition uses function_declarations. What needs to change in the tool schema for the Anthropic API?**

To switch your tool definition from Google Gemini (function_declarations) to Anthropic Claude (tools), you need to unwrap the outer function_declarations list, rename parameters to input_schema, and convert uppercase OpenAPI schema types (like OBJECT and STRING) to lowercase JSON Schema types (object and string).

## Key Schema Changes Required

| Schema Component | Google Gemini Format | Anthropic Claude Format |
| --- | --- | --- |
| Top-Level Wrapper | Wrapped inside a {"function_declarations": [ ... ]} object inside the tools list. | Passed as a flat list of tool objects directly inside tools=[ ... ] (no function_declarations key). |
| Parameter Field Name | Uses "parameters" to define tool arguments. | Uses "input_schema" instead of "parameters". |
| Data Type Casing | Often uses uppercase OpenAPI enums ("OBJECT", "STRING", "INTEGER", "NUMBER", "BOOLEAN", "ARRAY"). | Strictly requires lowercase JSON Schema types ("object", "string", "integer", "number", "boolean", "array"). |

## Side-by-Side Schema Comparison

### 1. Before: Gemini Tool Definition

```text
gemini_tools = [
    {
        "function_declarations": [
            {
                "name": "get_exchange_rate",
                "description": "Get the current exchange rate between two currencies.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "base_currency": {
                            "type": "STRING",
                            "description": "Three-letter currency code, e.g. USD"
                        },
                        "target_currency": {
                            "type": "STRING",
                            "description": "Three-letter currency code, e.g. INR"
                        }
                    },
                    "required": ["base_currency", "target_currency"]
                }
            }
        ]
    }
]
```

### 2. After: Anthropic Claude Tool Definition

```yaml
anthropic_tools = [
    {
        "name": "get_exchange_rate",
        "description": "Get the current exchange rate between two currencies.",
        "input_schema": {  # 1. Renamed from 'parameters'
            "type": "object",  # 2. Lowercase JSON Schema type
            "properties": {
                "base_currency": {
                    "type": "string",  # 2. Lowercase type
                    "description": "Three-letter currency code, e.g. USD"
                },
                "target_currency": {
                    "type": "string",  # 2. Lowercase type
                    "description": "Three-letter currency code, e.g. INR"
                }
            },
            "required": ["base_currency", "target_currency"]
        }
    }
]
```
