# Chapter 10 - Part 2: How Function Calling Works Mechanically

> Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs

Function calling works mechanically as a multi-turn orchestration loop between your application backend and the LLM API. The LLM never executes code directly; instead, it outputs a structured JSON request asking your server to run a function on its behalf.

## The 5-Step Mechanical Loop

1. **Schema Injection (Request 1):** Your backend sends the user's message along with a tools array containing JSON Schemas (function names, descriptions, and expected parameters). Under the hood, the API provider formats these schemas into special tokens inside the system prompt.
2. **Intent Detection & JSON Generation:** The model evaluates the prompt. Instead of generating normal conversational text, its fine-tuned weights predict special tool-call control tokens (e.g., <|tool_call|>) followed by a JSON object specifying the function name and arguments, such as {"name": "get_order", "arguments": {"id": "123"}}.
3. **Stream Interruption (finish_reason):** The API stops generating tokens and returns the response to your backend with finish_reason: "tool_calls" (instead of "stop"), signaling that the model is paused and waiting for external data.
4. **Local Execution:** Your backend parses the JSON arguments, validates them, and executes the actual Python/Node function or external API call on your own infrastructure.
5. **Context Injection & Final Synthesis (Request 2):** Your backend appends both the assistant's tool-call request and a new role: "tool" message containing the raw execution output to the messages array, then calls the LLM API a second time. The model reads the tool result in its context window and generates the final natural-language answer.

## Payload Evolution Across the Loop

| Turn | Role in messages Array | Content Sent to / Returned by API |
| --- | --- | --- |
| 1. Initial Call | system + tools + user | "Where is order #123?" + schema for get_order(id) |
| 2. Model Pause | assistant (tool_calls) | id: "call_abc", name: "get_order", args: {"id": "123"} |
| 3. Backend Runs | *(Executed on your server)* | Queries database -> returns {"status": "Shipped", "eta": "Friday"} |
| 4. Second Call | tool (tool_call_id: "call_abc") | Appends raw JSON result to history and re-sends entire array |
| 5. Final Output | assistant (content) | "Your order #123 has shipped and will arrive on Friday." |

## Key Mechanical Guarantees

- **Constrained Decoding:** Modern APIs enforce the tool's JSON Schema at the token-logit level during Step 2, guaranteeing the model cannot output malformed JSON or hallucinate missing required keys.
- **Stateless Matching (tool_call_id):** Because an LLM can request multiple tools in parallel in a single turn, every tool call is assigned a unique ID (e.g., call_abc) so your backend can map each execution result back to the exact call that requested it.

## The Model's Role

In the function-calling architecture, the model acts strictly as a semantic router and argument extractor—never as an executor.

It decides *if* a tool is needed, *which* tool to pick, and *what* inputs to pass, while delegating all actual execution to your application backend.

## The Model's 4 Core Responsibilities

- **1. Intent Classification (Routing):** The model reads the user's request alongside the injected tool descriptions and decides whether it can answer from its own parametric memory or needs external help. If external data or action is required, it shifts from normal text generation into tool-calling mode.
- **2. Argument Extraction & Formatting:** The model extracts relevant entities from the messy natural language of the conversation (such as dates, user IDs, or cities) and maps them into the strict types and keys required by the tool's JSON Schema (e.g., converting "next Tuesday" into "2026-11-17").
- **3. Multi-Step Planning & Sequencing:** For complex goals, the model breaks the task down into sequential or parallel tool calls. For example, it knows it must call get_user_id(email) first and wait for the result before it can call get_order_history(user_id).
- **4. Output Synthesis:** Once your backend executes the function and injects the raw data back into the context window, the model translates that structured, machine-readable output (like a dense JSON blob or SQL row) into a natural, human-friendly response.

## What the Model Explicitly Does Not Do

- **No Direct Execution:** The model has zero network access, zero file-system access, and zero ability to run code on its own. It only emits text tokens formatted as a request.
- **No Authentication or Authorization:** The model does not verify whether a user is *allowed* to call a function or access a specific record. Your backend code must enforce permissions and validate inputs before executing any requested tool call.

## The Application's Role

In the function-calling architecture, the application (your backend server) acts as the orchestrator, security gatekeeper, and actual executor.

While the LLM decides *what* needs to happen, your application holds all the credentials, runs the code, enforces permissions, and manages the state of the conversation loop.

## The Application's 5 Core Responsibilities

- **1. Schema Registration & Context Management:** Your backend defines the available tools (as JSON Schemas) and injects them into every stateless API call alongside the running messages history.
- **2. Loop Control & Interception:** Your application inspects the finish_reason returned by the LLM API. When it sees tool_calls, it pauses returning text to the end user, parses the requested function name and arguments, and routes them to the matching local code handler.
- **3. Validation, Auth & Security Gatekeeping:** Because the LLM is untrusted and susceptible to prompt injection, your backend must verify every tool call before running it. It checks user permissions (e.g., ensuring User A cannot call get_order(id="999") belonging to User B), sanitizes inputs against SQL/command injection, and triggers human-in-the-loop approval for high-stakes write actions (like processing refunds or deleting records).
- **4. Real-World Execution:** Your server executes the actual Python/Node function, queries the database, or calls third-party APIs using its own secure API keys and network access—none of which are ever exposed to the LLM.
- **5. State Appending & Error Handling:** After execution, your application wraps the return value—or a clean, descriptive error message if the function failed—into a role: "tool" message matched to the exact tool_call_id, appends it to the conversation history, and triggers the next LLM API call so the model can continue or self-correct.

## Summary: Division of Labor

| Responsibility | The Model (LLM) | The Application (Backend) |
| --- | --- | --- |
| Decision Making | Chooses which tool to call and extracts arguments | Decides which tools are exposed to the model |
| Execution | Emits a structured JSON intent | Runs the actual code, SQL query, or HTTP request |
| Security & Auth | None (relies solely on prompt instructions) | Enforces RBAC, rate limits, and input sanitization |
| State & Memory | Stateless (reads whatever context is sent) | Stores conversation history and manages the while loop |
