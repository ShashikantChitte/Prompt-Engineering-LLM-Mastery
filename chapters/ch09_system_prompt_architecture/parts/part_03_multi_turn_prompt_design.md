# Chapter 9 - Part 3: Multi-Turn Prompt Design

> Chapter 9: System Prompt Architecture

**Multi-turn prompt design** is the practice of structuring prompts so an AI maintains context, follows complex workflows, and refines outputs across a back-and-forth conversation rather than a single query. Instead of cramming every requirement into one massive initial prompt, you guide the model step by step.

## Core Principles

- **Set the Foundation Early:** Use the first turn (or system prompt) to establish the AI's role, tone, formatting rules, and overall goal.
- **Decompose Complex Tasks:** Break large projects into sequential stages so the model focuses on one subtask at a time.
- **Use Explicit Anchors:** Refer directly to previous outputs (e.g., "Using the outline from step 2...") to prevent the model from drifting or forgetting constraints.
- **Iterate and Refine:** Treat each subsequent turn as a targeted feedback loop to adjust tone, fix edge cases, or expand specific sections.

## Common Multi-Turn Patterns

| Pattern | How It Works | Best Used For |
| --- | --- | --- |
| Prompt Chaining | The output of Turn 1 becomes the input and foundation for Turn 2, moving linearly toward a final deliverable. | Writing long articles, building software architectures, or multi-step data analysis. |
| Critique & Revise | You ask the model to generate a draft, evaluate its own work against criteria in Turn 2, and rewrite it in Turn 3. | Polishing copy, debugging code, and improving factual or logical accuracy. |
| Clarification-First | You instruct the AI to ask you targeted questions before attempting to solve the problem. | Ambiguous requests, personalized planning, and complex system design. |
| State & Summary Reset | Periodically asking the AI to summarize agreed-upon decisions so far before starting a new phase. | Long conversations where early instructions risk falling out of the active context window. |

## Practical Example: Building a Python Playwright Scraper

Instead of asking for a complete production script at once, you split it into turns:

- **Turn 1 (Architecture):** *"Act as a senior Python automation engineer. Outline a plan to scrape product prices from a paginated site using Playwright's Sync API, handling rate limits and missing elements."*
- **Turn 2 (Core Code):** *"Write the Python code for Step 1 and Step 2 of your outline, using clean functions and type hints."*
- **Turn 3 (Edge Cases):** *"Update the code to retry failed page loads up to three times and export the final results to a CSV file."*

## Pitfalls to Avoid

- **Context Bloat:** Pasting huge walls of unedited text in every turn dilutes the model's attention on your latest instruction.
- **Conflicting Instructions:** Changing goals mid-conversation without explicitly telling the AI to drop earlier rules causes erratic outputs.
- **Vague Follow-Ups:** Saying "make it better" forces the model to guess; always specify *what* to change and *how*.

```text
Context window and conversation history
```

The context window is the maximum amount of text (measured in tokens) an AI model can process at one time, and conversation history is stored inside that window. Because large language models are stateless, they do not naturally remember past messages; instead, the entire conversation history is re-sent alongside your newest prompt on every turn.

## How They Work Together

- **Tokens as Currency:** Text is broken into chunks called tokens (roughly 4 characters or ¾ of a word in English). Your system instructions, every previous message, the AI's past replies, and the AI's upcoming response all count toward the total token limit.
- **Stateless Replay:** When you send a third message in a chat, the application bundles Turn 1, Turn 2, and Turn 3 into a single payload so the model can predict the next logical reply based on the full thread.
- **Sliding Window / Truncation:** Once a conversation exceeds the model's context window limit, older messages are either dropped from the front (FIFO) or compressed into a summary so new messages can fit.

## Key Challenges in Long Conversations

- **Lost in the Middle:** Models tend to pay the strongest attention to the very beginning (system prompt) and the very end (your latest message), meaning details buried in the middle of a long history can be overlooked.
- **Context Rot (Instruction Drift):** As thousands of tokens of back-and-forth accumulate, contradictory drafts, old errors, or tangential topics can confuse the model and degrade response quality.
- **Latency and Cost:** Sending a massive conversation history on every single turn requires more compute, which increases response times and API token costs.

## Best Practices for Managing History

- **Start Fresh for New Topics:** Open a new chat session whenever you switch tasks so unrelated history does not pollute the context.
- **Use Checkpoint Summaries:** In long multi-turn workflows, ask the model to summarize key decisions or final code, then paste that clean summary into a fresh thread to reset the context window.
- **Prune or Edit Bad Turns:** If the AI goes down the wrong path, edit your previous prompt rather than arguing with it over five extra turns, keeping failed attempts out of the active history.

```text
Maintaining intent across turns
```

**Maintaining intent across turns** means ensuring an AI stays aligned with your core objective, rules, and constraints throughout a multi-turn conversation without drifting into tangential topics or forgetting early requirements. Because models weigh recent tokens heavily, older goals naturally lose influence unless you actively reinforce them.

## Why Intent Drifts

- **Recency Bias:** Models prioritize the most recent messages, causing a minor follow-up question to accidentally override your primary objective from Turn 1.
- **Ambiguous Pronouns & Shortcuts:** Saying *"Now make it faster"* or *"Change that part"* forces the model to guess which previous output or constraint you are referencing.
- **Accumulated Noise:** Failed attempts, side questions, and verbose AI explanations clutter the context window and dilute your original instructions.

## Practical Techniques for Users

- **Restate the Anchor Goal:** Briefly tie new instructions back to your primary objective (e.g., *"Keeping our goal of a lightweight, zero-dependency Python script in mind, now add error logging"*).
- **Separate Exploration from Execution:** If you need to ask a quick side question, explicitly label it as a tangent so the model does not apply that answer to your main deliverable.
- **Use Constraints as Guardrails:** Repeat non-negotiable rules at the end of follow-up prompts (e.g., *"Stick to the Playwright Sync API and keep all functions under 20 lines"*).
- **Edit Instead of Correcting:** When a turn goes off-track, edit your last prompt rather than adding corrective turns, which keeps conflicting intent out of the history.

## Engineering Strategies (For AI Builders)

- **Persistent System Prompts:** Keep core persona, safety rules, and overarching goals locked at the very top of every API payload so they are never truncated.
- **Intent Rewriting (Query Contextualization):** Before sending a follow-up to the main model or a search index, use a fast step to rewrite vague user input (e.g., turning *"How much does it cost?"* into *"What is the monthly API pricing for [Product X] discussed in Turn 1?"*).
- **Structured State Tracking:** Maintain a lightweight JSON object or scratchpad outside the raw chat log that tracks confirmed user goals, constraints, and completed steps, injecting it into each turn.

```text
Conversation state
```

**Conversation state** is the structured record of facts, user goals, constraints, and progress accumulated during a multi-turn interaction. Instead of relying solely on a raw transcript of past messages, tracking conversation state gives an AI or application a reliable "working memory" of what has been decided and what needs to happen next.

## Raw History vs. Conversation State

| Feature | Raw Conversation History | Conversation State |
| --- | --- | --- |
| Format | Unstructured chronological log of user and AI messages. | Structured data (such as JSON, key-value pairs, or bulleted summaries). |
| Token Efficiency | Grows rapidly with every turn, increasing cost and latency. | Compact and fixed-size, keeping only essential facts. |
| Signal-to-Noise | Contains greetings, failed attempts, and tangents. | Stores only verified decisions, active constraints, and current progress. |
| Reliability | Subject to recency bias and "lost in the middle" forgetting. | Keeps critical rules and parameters explicitly visible on every turn. |

## Key Components of Conversation State

- **Active Intent & Goal:** What the user is ultimately trying to achieve right now (e.g., "goal": "build_playwright_scraper").
- **Collected Entities & Slots:** Specific parameters gathered across turns (e.g., target URL, output format, or preferred API).
- **Constraints & Preferences:** Rules that must remain true across turns (e.g., "use_async": false, "output": "CSV").
- **Workflow Stage:** Where the conversation sits in a multi-step process (e.g., "step": "error_handling", "completed": ["setup", "pagination"]).

## How State Is Managed in Practice

- **In Chat Interfaces (Manual State):** You can prompt the AI to maintain a visible state block at the bottom of its replies (e.g., *"End every response with a 3-line 'Current Specs' summary"*), ensuring both you and the model stay aligned.
- **In AI Applications (Programmatic State):** Backend code extracts updates from each user message into a JSON object or database, injecting that clean state into the system prompt before generating the next reply.
- **In Agentic Frameworks:** Tools like LangGraph or state machines pass an explicit State object from node to node, allowing agents to pause, resume, or branch workflows without losing track of variables.
