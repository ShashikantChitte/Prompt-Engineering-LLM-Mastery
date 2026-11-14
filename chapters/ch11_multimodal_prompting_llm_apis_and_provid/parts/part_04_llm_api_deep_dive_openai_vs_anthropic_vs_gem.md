# Chapter 11 - Part 4: LLM API Deep Dive: OpenAI vs Anthropic vs Gemini - design differences, streaming, rate limits, context windows, pricing, function calling

> Chapter 11: Multimodal Prompting + LLM APIs and Provider Ecosystem

An **LLM API Deep Dive** covers the mechanics of how applications communicate programmatically with Large Language Models over HTTP—moving beyond simple chat interfaces to control stateless requests, token economics, decoding parameters, streaming, and reliability.

### 1. Stateless Architecture & Conversation Management

LLM APIs are **stateless**, meaning the server remembers nothing between requests.

- **Full History Replay:** Every API call must send the entire conversation history (messages array) from the beginning so the model has context.
- **Message Roles:** Conversations are structured using distinct roles that control authority and behavior:
  - system (or developer): High-priority instructions setting persona, rules, and output format.
  - user: End-user inputs, questions, or multimodal content (images/PDFs).
  - assistant: Previous model replies (including past tool_calls).
  - tool: Outputs returned by your application after executing a function call.

### 2. Core Inference & Decoding Parameters

API payloads expose mathematical controls over how the model selects the next token:

| Parameter | What It Controls | Practical Guidance |
| --- | --- | --- |
| temperature | Randomness of token selection (typically 0.0 to 2.0). | Use 0.0–0.2 for deterministic tasks (code, extraction, JSON); use 0.7–1.0 for brainstorming or creative writing. |
| top_p (Nucleus Sampling) | Restricts token choices to the smallest pool whose cumulative probability exceeds p. | Usually leave at default (1.0) when adjusting temperature—avoid altering both heavily at once. |
| max_tokens | Hard ceiling on how many output tokens the model can generate. | Prevents runaway billing and infinite loops; if hit, finish_reason returns "length". |
| stop | Custom stop sequences (e.g., ["END", "```"]) that halt generation immediately. | Useful for cutting off conversational chatter after a specific delimiter. |
| seed | Best-effort deterministic sampling seed for reproducible outputs. | Helpful for debugging and regression testing, though slight hardware variance can still occur. |

### 3. Streaming (Server-Sent Events)

Generating long responses can take several seconds, creating a sluggish user experience if you wait for the full payload.

- **How It Works:** Setting stream: true keeps the HTTP connection open using **Server-Sent Events (SSE)**, pushing incremental token chunks (delta) to the client as soon as they are computed.
- **Key Latency Metrics:**
  - **TTFT (Time to First Token):** How fast the user sees the first word appear—critical for perceived responsiveness.
  - **ITL / TPOT (Inter-Token Latency):** The speed at which subsequent tokens stream across the screen.

### 4. Token Economics, Caching & Rate Limits

- **Asymmetric Pricing:** Output tokens (generated one by one) typically cost **3× to 5× more** than input tokens (processed in parallel).
- **Prompt Caching:** When requests share a long static prefix (such as a large system prompt, few-shot examples, or a reference document), providers automatically cache those prefix KV states—cutting input token costs by **50%–90%** and drastically lowering TTFT.
- **Rate Limits (RPM & TPM):** APIs enforce quotas on **Requests Per Minute (RPM)** and **Tokens Per Minute (TPM)**. Production apps handle HTTP 429 (Too Many Requests) errors using **exponential backoff with jitter**.

### 5. Lifecycle of an API Response

Every response includes critical metadata alongside the generated text:

- **usage object:** Exact breakdown of prompt_tokens, completion_tokens, cached_tokens, and reasoning_tokens for cost tracking.
- **finish_reason:** Tells your application *why* generation ended ("stop" for normal completion, "tool_calls" for function execution, "length" for token cutoff, or "content_filter" for safety blocks).

```text
Why the APIs diverged
```

LLM APIs diverged because OpenAI's original Chat Completions API was designed for simple text-in, text-out chatbots, whereas modern AI systems require **stateful agents, native multimodality, reasoning traces, and built-in server tools** that cannot fit cleanly into a flat list of chat messages.

### 1. The Origin: OpenAI's Chat Completions Standard

When OpenAI released /v1/chat/completions, it became the accidental industry standard (messages=[{"role": "user", "content": "..."}]). Nearly every provider (Anthropic, Google, Mistral, Groq, open-source vLLM) initially mimicked this format so developers could switch models by changing a base URL.

However, as capabilities evolved beyond basic text chat, squeezing new features into that rigid schema caused severe friction.

### 2. Four Core Reasons Why APIs Diverged

- **Native Multimodality (Beyond Text Strings):**
  - The original Chat Completions API assumed content was a simple string. Adding images, PDFs, audio streams, and video required complex nested arrays (content: [{"type": "text"}, {"type": "image_url"}]), and providers disagreed on whether to pass raw bytes, base64 strings, or server-side File API URIs (like Gemini's Files API).
- **Reasoning Models & Thinking Traces:**
  - Models that "think" before answering (like OpenAI o-series, Claude Extended Thinking, and Gemini Thinking) produce internal reasoning tokens alongside final answers. APIs had to diverge to separate thinking blocks from visible output, hide encrypted reasoning states, and expose parameters like reasoning_effort or thinking_budget.
- **Stateful Agents & Server-Side Tools:**
  - In Chat Completions, your application had to manually manage the entire conversation loop and execute every tool locally. Modern agentic APIs—such as **OpenAI's Responses API** and **Google's Interactions / Live API**—introduced server-side state (previous_response_id), built-in hosted tools (web search, code execution, file search), and real-time bidirectional WebSockets for voice/video.
- **Strict Structured Outputs & Caching Controls:**
  - Providers implemented constrained decoding and prompt caching differently—for example, Anthropic requires explicit cache_control breakpoints inside message blocks, whereas OpenAI and Gemini use automatic prefix caching or dedicated cached-content objects.

### 3. How Major APIs Split Today

| API Paradigm | Examples | Design Philosophy |
| --- | --- | --- |
| Legacy Stateless Chat | OpenAI /chat/completions, vLLM, OpenRouter | Lowest-common-denominator compatibility; stateless messages array; great for basic text and simple tool loops. |
| Modern Agentic / Unified APIs | OpenAI /responses, Google Gemini SDK (google-genai), Anthropic Messages API | Typed content blocks (text, thinking, tool_use, file); built-in hosted tools; optional server-side state and multimodal streaming. |

## Why This Matters for Developers

Because native APIs no longer share one identical payload format, production teams either use **unified abstraction layers** (like LiteLLM, Vercel AI SDK, or LangChain) when they need multi-provider portability, or call **native provider SDKs** directly when they need bleeding-edge features like prompt caching, reasoning budgets, or real-time audio.

```text
API design differences
```

Major LLM providers—primarily **OpenAI**, **Anthropic**, and **Google Gemini**—differ significantly in how they structure payloads, manage state, handle system instructions, and format multimodal or tool-calling messages.

### 1. Side-by-Side API Design Comparison

| Design Dimension | OpenAI (Responses / Chat Completions) | Anthropic (Messages API) | Google Gemini (google-genai SDK) |
| --- | --- | --- | --- |
| System Instructions | Passed inside the messages array (role: "developer" or "system") or top-level instructions field (Responses API). | Passed as a **top-level parameter** (system="..."), separate from the messages list. | Passed inside a **GenerateContentConfig** object (system_instruction="..."), separate from contents. |
| Conversation Roles | developer / system, user, assistant, tool. | Strictly alternates between **user** and **assistant** (tool results go inside a user message). | Uses **user** and **model** (instead of assistant). |
| Content Representation | String or list of typed blocks (input_text, input_image, output_text). | List of typed content blocks (text, image, thinking, tool_use, tool_result). | List of Part objects (Part.from_text, Part.from_bytes, Part.from_uri) inside Content objects. |
| Tool Calling & Results | Assistant outputs tool_calls array; app appends separate message(s) with role: "tool" and tool_call_id. | Assistant outputs a tool_use content block; app replies with a user message containing a tool_result block. | Model outputs function_call part; app replies with a user message containing a function_response part. |
| State Management | Stateless (Chat Completions) or optional server-side chaining via previous_response_id (Responses API). | Strictly stateless—client must send the full messages array on every turn. | Stateless generate_content or stateful helper chats.create() that manages history client-side. |
| Prompt Caching | **Automatic** prefix caching on prompts ≥1,024 tokens (no code changes needed). | **Explicit breakpoints** via cache_control: {"type": "ephemeral"} on specific blocks. | **Both:** Automatic implicit caching plus explicit CachedContent objects with custom TTLs. |
| Large File Handling | Base64 inline, public URLs, or Files API (file_id). | Base64 inline, URLs, or Files API (file_id). | Dedicated **Files API** (client.files.upload()) supporting large PDFs, audio, and multi-hour videos via URI. |

### 2. Three Key Architectural Philosophies

- **Typed Content Blocks vs. Role-Based Messages:**
  - Earlier APIs separated actions using distinct message roles (role: "tool"). Modern APIs (Anthropic Messages, OpenAI Responses, Gemini Parts) treat every turn as an array of **typed content blocks**, allowing a single assistant turn to seamlessly mix thinking blocks, visible text, and multiple tool_use requests in exact chronological order.
- **Client-Managed State vs. Server-Managed State:**
  - Traditional REST APIs require sending the entire conversation history on every turn (which increases bandwidth as chats grow). Newer endpoints like OpenAI's Responses API allow passing just a previous_response_id so the server stores and retrieves prior context, reasoning traces, and tool outputs.
- **Transport Protocols (REST vs. SSE vs. WebSockets):**
  - Standard text and vision requests use **HTTP POST + Server-Sent Events (SSE)** for one-way token streaming. However, real-time voice and video APIs (such as OpenAI's Realtime API and Gemini's Multimodal Live API) abandon REST completely in favor of **bidirectional WebSockets / WebRTC** to support low-latency interruptions.

```text
Streaming responses
```

**Streaming responses** allow an LLM API to send generated tokens incrementally as they are produced—rather than waiting for the entire answer to finish—dramatically improving perceived speed and user experience.

### 1. Why Streaming Matters

Because LLMs generate text one token at a time (autoregressively), a 500-token response can take 5–15 seconds to complete.

- **Without Streaming (stream=False):**

The user stares at a blank loading spinner until the entire response finishes, then sees a wall of text appear at once.

- **With Streaming (stream=True):** The user sees the first words within **200–500 milliseconds** (measured as **Time to First Token, or TTFT**) and reads along smoothly as the text types out in real time.

### 2. How Streaming Works Under the Hood (Server-Sent Events)

Most LLM APIs implement streaming over standard HTTP using **Server-Sent Events (SSE)**:

1. **Open Connection:** Your client sends a POST request with stream=True, keeping the HTTP connection open.
2. **Incremental Chunks (delta):** Each time the model computes a new token (or small batch of tokens), the server pushes a lightweight JSON event prefixed with data: .
3. **Stream Termination:** When generation finishes, the server sends a final chunk containing the finish_reason (such as "stop"), optional token usage stats, and a terminal data: [DONE] signal before closing the connection.

### 3. Provider Event Formats

While the core concept is universal, providers structure SSE events differently:

| Provider | Stream Format | How Events Are Structured |
| --- | --- | --- |
| OpenAI (Chat Completions) | Generic data: chunks | Every event is a chat.completion.chunk containing choices[0].delta.content (or incremental tool_calls argument fragments). |
| OpenAI (Responses) & Anthropic | Typed semantic events | Uses named SSE events (event: content_block_delta, event: response.output_text.delta) to cleanly separate thinking traces, text chunks, and tool calls. |
| Google Gemini (google-genai) | Typed chunk objects | Iterating over generate_content_stream() yields progressive GenerateContentResponse objects where chunk.text holds the newly generated text. |

### 4. Engineering Challenges & Edge Cases in Streaming

Building production streaming UIs introduces specific edge cases that non-streaming requests avoid:

- **Streaming Tool Calls:** Function arguments arrive piece-by-piece across dozens of chunks (e.g., {"ci, ty": "Mu, mbai"}). Your code must buffer and concatenate these JSON fragments completely before parsing or executing the tool.
- **Mid-Stream Errors & Disconnects:** Because the HTTP 200 OK status was already sent when the stream started, rate limits, content-filter triggers, or network drops happening mid-response arrive inside the stream payload rather than as a standard HTTP error status.
- **Token Usage Tracking:** In many APIs, token counts (prompt_tokens, completion_tokens) are only sent in the very last chunk (and often require setting stream_options={"include_usage": True} in OpenAI).
- **Frontend Buffering & Markdown Rendering:** Proxies (like Nginx) can accidentally buffer SSE chunks unless X-Accel-Buffering: no is set, and frontend UIs must handle incomplete Markdown syntax (like an unclosed code block ```python) gracefully while tokens are still arriving.

## Context windows, rate limits, and pricing

**Context windows, rate limits, and pricing** are the three core operational constraints that determine what an LLM application can process, how fast it can scale, and how much it costs to run in production.

### 1. Context Windows (Memory Capacity)

A **context window** is the maximum number of tokens (input + reasoning + output combined) an LLM can hold in working memory during a single API request.

- **What Counts Toward the Limit:** Everything sent in the request—system instructions, tool schemas, conversation history, uploaded images/PDF tokens—plus the model's internal thinking tokens and final output tokens.
- **Overflow Errors:** Exceeding the context window causes the API to reject the request with an HTTP 400 Bad Request (context_length_exceeded).
- **Effective vs. Advertised Context ("Lost in the Middle"):** Even when a model supports 128K to 1M+ tokens, recall accuracy often degrades for facts buried in the middle of massive prompts, while latency and cost scale linearly or quadratically with input size.
- **Management Strategies:** Production apps manage context using **sliding windows** (keeping only the last N turns), **rolling summarization** of older messages, or **RAG** (retrieving only relevant chunks instead of stuffing whole documents).

### 2. Rate Limits (Throughput Quotas)

API providers enforce rate limits to protect infrastructure stability and ensure fair multi-tenant access. Limits are usually measured across two dimensions simultaneously:

- **RPM (Requests Per Minute):** Maximum number of individual API calls allowed per minute.
- **TPM (Tokens Per Minute):** Maximum total tokens (input + estimated max_tokens output) processed per minute. *(Note: Many providers also enforce* ***RPD / TPD*** *daily limits on lower usage tiers).*
- **Handling HTTP 429 Too Many Requests:**
  - **Exponential Backoff with Jitter:** Wait progressively longer between retries (e.g., 1s, 2s, 4s, 8s) plus a random millisecond delay ("jitter") so multiple failed requests do not retry at the exact same instant.
  - **Set Tight max_tokens:** Providers reserve your requested max_tokens against your TPM quota upfront—setting max_tokens: 500 instead of leaving it at 16,000 prevents premature TPM throttling.
  - **Multi-Region / Multi-Provider Routing:** Production gateways fail over automatically to backup deployments or secondary providers when primary rate limits saturate.

### 3. Pricing & Token Economics

LLM APIs charge on a **pay-per-token** basis (typically quoted per **1 million tokens**), with different rates depending on how the tokens are processed:

| Token Category | Relative Cost | Why It Is Priced This Way |
| --- | --- | --- |
| Cached Input Tokens | **Lowest** (~50%–90% discount) | Reuses precomputed Key-Value (KV) attention states from recent requests with identical prefixes. |
| Standard Input Tokens | **Base Rate** (1×) | Processed in parallel in a single forward pass (prefill phase), making them fast and compute-efficient. |
| Output & Reasoning Tokens | **Highest** (3×–5× input rate) | Generated sequentially one token at a time (decode phase), requiring a full model pass per token and heavy memory bandwidth. |
| Batch API Tokens | **50% Discount** (Input & Output) | Asynchronous jobs processed within 24 hours using spare off-peak GPU capacity—ideal for offline evaluations and bulk extraction. |

## Key Cost Optimization Levers

- **Structure Prompts for Cache Hits:** Put static instructions, tool definitions, and large reference documents at the **very top** of your prompt, and place dynamic user queries at the **very bottom** so prefix caching triggers automatically.
- **Model Routing:** Route simple classification or extraction tasks to small, fast models (like Flash/Mini/Haiku variants) and reserve large frontier models only for complex reasoning.

## Function calling differences

While the core workflow of function calling (tool use) is identical across all providers—**define schemas → model requests call → app executes code → return result**—major LLM APIs differ significantly in how they structure tool definitions, handle parallel calls, format tool results, and enforce strict argument schemas.

### 1. Side-by-Side Comparison Across Providers

| Feature | OpenAI (Chat Completions / Responses) | Anthropic (Messages API) | Google Gemini (google-genai SDK) |
| --- | --- | --- | --- |
| Tool Schema Format | JSON Schema wrapped in {"type": "function", "function": {...}} (or flat in Responses API). | JSON Schema using "input_schema" instead of "parameters". | OpenAPI-compatible Schema object (or auto-generated directly from Python functions/type hints). |
| Model Call Output | Returns a tool_calls array with unique id, function name, and **JSON-encoded string** arguments. | Returns a tool_use content block with unique id, name, and **parsed JSON object** input. | Returns a function_call part with name and **parsed dictionary** args (optional id). |
| Returning Tool Results | Appends separate message(s) with role: "tool" and matching tool_call_id. | Appends a **user** message containing a tool_result block with matching tool_use_id. | Appends a **user** message containing a function_response part with matching function name. |
| Strict Schema Enforcement | Supports "strict": true inside the tool definition for guaranteed constrained decoding. | Supports strict structured tool inputs via constrained decoding. | Enforces types natively via Schema / Pydantic definitions. |
| Tool Choice Controls | "auto", "none", "required", or forcing a specific {"type": "function", "function": {"name": "..."}}. | {"type": "auto"}, {"type": "any"} (forced), or {"type": "tool", "name": "..."}. | FunctionCallingConfig modes: AUTO, NONE, or ANY (with optional allowed_function_names). |

### 2. Four Key Design Differences That Trip Up Developers

- **Stringified JSON vs. Parsed Objects:**
  - OpenAI returns function arguments as a **raw JSON string** ('{"city": "Mumbai"}'), requiring json.loads() before execution—and risking a JSONDecodeError if strict: true is disabled. Anthropic and Gemini return already-parsed dictionaries/objects ({"city": "Mumbai"}).
- **Separate tool Role vs. user Content Blocks:**
  - OpenAI uses a dedicated role: "tool" message for every single tool output. Anthropic and Gemini enforce strict user / model (or assistant) alternation, so tool outputs must be packed inside a **user** message alongside any follow-up text.
- **Parallel Tool Call Matching (id vs. name):**
  - When a model calls the same function twice in parallel (e.g., get_weather("Mumbai") and get_weather("Delhi")), OpenAI and Anthropic link each result back using a unique call ID (tool_call_id / tool_use_id). Gemini traditionally maps responses by function name (or optional id in newer SDK versions), so responses must match the exact order and count of calls.
- **Automatic SDK Execution (Python Functions as Tools):**
  - Google's google-genai SDK allows passing native Python functions directly into tools=[my_func]—automatically extracting the schema from type hints/docstrings and even executing the function loop automatically unless disabled. OpenAI and Anthropic generally require explicit JSON schemas (or helper wrappers like Pydantic's pydantic_function_tool).
