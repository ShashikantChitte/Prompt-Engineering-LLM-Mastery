# Chapter 10 - Part 1: Why Tools Exist: three fundamental LLM problems

> Chapter 10: Tool-Using LLMs: Function Calling and Structured Outputs

Tools (also called function calling) exist to bridge the gap between a passive text generator and an active system that can interact with the real world.

On its own, an LLM is a frozen mathematical model trapped in a box. It can only read text and predict the next token. Tools give the model "hands and eyes" so it can access live information, perform exact computations, and take real-world actions.

## Core Reasons Why Tools Exist

- **1. Overcoming Knowledge Cutoffs (Accessing Live Data):** An LLM only knows what was in its training data up to a specific date. Tools allow the model to query live databases, search the web, or check real-time APIs (such as current stock prices, weather, or a customer's order status).
- **2. Eliminating Hallucinations via Grounding:** Instead of guessing answers from compressed memory, the model can use a retrieval tool (like RAG or SQL search) to pull verified facts from private company documents or knowledge bases before answering.
- **3. Performing Deterministic Computation:** LLMs are probabilistic word predictors, making them unreliable at complex math, sorting large datasets, or running code. Tools let the model hand off calculations to a Python interpreter or calculator, ensuring 100% deterministic accuracy.
- **4. Taking Real-World Actions (Agency):** Text alone cannot change state in external software. Tools allow an AI agent to send an email, create a Jira ticket, update a CRM record, or process a refund via structured API calls.
- **5. Enforcing Structured Interfaces:** Instead of trying to parse messy natural language from the LLM's output, tools force the model to output a strict JSON object matching a predefined schema, which your backend code can safely execute.

## How It Works Under the Hood (Crucial Distinction)

The LLM **never executes the tool itself**. Instead, the process works as a loop between the model and your backend code:

1. **Declaration:** Your API call sends a list of available tool schemas (names, descriptions, and required parameters) inside the system prompt.
2. **Intent & Formatting:** When the user asks a question requiring external data, the LLM pauses text generation and outputs a structured JSON request (e.g., get_weather(city="Mumbai")).
3. **Execution:** Your application server intercepts that JSON, runs the actual code or API call, and gets the result ("31°C, Humid").
4. **Synthesis:** Your server sends that result back into the LLM's context window as a tool message, and the LLM uses it to write the final human-readable answer.

## Three fundamental problems in LLM

Tools exist specifically to solve the **three fundamental problems** of standalone Large Language Models:

### 1. Static Knowledge (The Cutoff Problem)

- **The Problem:** An LLM’s weights are frozen after training finishes. It has zero knowledge of real-time events, current prices, live weather, or private company data created after its training cutoff.
- **How Tools Fix It:** Tools connect the model to live APIs, web search, and internal databases so it can fetch up-to-the-second facts on demand.

### 2. Probabilistic Guessing (Hallucinations & Bad Math)

- **The Problem:** LLMs generate text by predicting the statistically most likely next token, not by verifying facts or executing logic. Because of this, they confidently invent false information (hallucinations) and fail at exact arithmetic, sorting, or code execution.
- **How Tools Fix It:** Tools offload deterministic tasks to specialized engines—such as a Python interpreter for exact math or a RAG retrieval tool for verified source documents—grounding the output in truth.

### 3. Lack of Agency (Inability to Act)

- **The Problem:** A standalone LLM is purely a text-in, text-out processor trapped in a sandbox. It cannot modify external state, interact with software systems, or perform tasks in the real world.
- **How Tools Fix It:** Tools act as structured API bridges (function calling) that let the model trigger real actions—like sending an email, querying a SQL database, or updating a customer record—through your application backend.
