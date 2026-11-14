# Chapter 8 - Part 1: ReAct: Reason + Act - where it came from, the Thought-Action-Observation loop, when it beats plain CoT

> Chapter 8: Advanced Prompting: ReAct, Safety and Responsible AI

**ReAct (Reason + Act)**—introduced by Yao et al. (2022)—is an agentic prompting and execution framework that interleaves Chain-of-Thought reasoning traces with external tool actions in a continuous loop until a task is solved.

While standard Chain-of-Thought (CoT) isolates an LLM inside its own frozen parametric memory (leading to hallucinations on fresh facts or exact math), ReAct connects the model's reasoning engine directly to the outside world via APIs, search engines, databases, or code interpreters.

### 1. The Core ReAct Loop (Thought -> Action -> Observation)

Instead of generating a single uninterrupted block of text, a ReAct agent alternates between three distinct stages inside its context window:

1. **Thought (Reason):** The model analyzes the current goal, identifies missing information, and plans its next step.
2. **Action (Act):** The model emits a structured tool call (such as search("current inflation rate") or run_python("245 * 19")) and **pauses generation**.
3. **Observation (Environment Feedback):** The external runtime executes the tool, injects the real-world output back into the prompt as an Observation:, and resumes the LLM so it can reason over the new facts.

This cycle repeats until the model emits a terminal Final Answer.

### 2. Why Combining Reasoning and Acting Works

Pure reasoning (CoT) and pure acting (tool-only agents) both suffer from major failure modes when used alone:

- **Reasoning Grounded in Reality:** Standard CoT hallucinates facts when its internal knowledge is outdated or incomplete. ReAct stops to fetch real data via Observation steps before continuing its deduction.
- **Acting Guided by Planning:** Tool-only models blindly fire API calls without tracking why they called them or how to recover from empty search results. Explicit Thought steps allow the model to decompose complex queries, reformulate failed searches, and track sub-goals across multiple turns.

### 3. Concrete Walkthrough Example

Suppose a user asks: *"What is the square root of the current population of Pune, India?"*

| Step | Component | Content |
| --- | --- | --- |
| 1 | **Thought** | I need to find the current population of Pune first, then calculate its square root. |
| 2 | **Action** | web_search("Pune population 2026") |
| 3 | **Observation** | *Search returns: "The estimated metro population of Pune in 2026 is 7,610,000."* |
| 4 | **Thought** | Now that I have the exact number (7,610,000), I should use Python to compute the square root accurately rather than estimating. |
| 5 | **Action** | python_exec("import math; math.sqrt(7610000)") |
| 6 | **Observation** | *Python returns: 2758.6228* |
| 7 | **Final Answer** | Based on an estimated population of 7.61 million, the square root is approximately **2,758.62**. |

## Comparison: CoT vs. Tool-Only vs. ReAct

| Paradigm | Internal Reasoning | External Tool Use | Key Limitation |
| --- | --- | --- | --- |
| Chain-of-Thought (CoT) | Yes | No | Prone to factual hallucinations and arithmetic slips |
| Action-Only (Tool Calling) | No | Yes | Struggles with multi-hop planning and error recovery |
| ReAct (Reason + Act) | **Yes** | **Yes** | Higher latency and token cost due to multi-turn loops |

## ReAct: Reason + Act - where it came from, the Thought-Action-Observation loop, when it beats plain CoT

**ReAct (Reason + Act)** was introduced in October 2022 by **Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao** (a collaboration between Princeton University and Google Research) in their landmark paper, ***"ReAct: Synergizing Reasoning and Acting in Language Models."***

The paper bridged a critical divide in AI research by uniting **internal verbal reasoning** (like Chain-of-Thought) with **external environment interaction** (tool use and API execution).

### 1. Where It Came From: The 2022 Divide

Before October 2022, LLM research had split into two disconnected tracks that each suffered from a major blind spot:

- **Reasoning-Only Models (CoT):** Could break down logic problems step-by-step, but operated as "brains in a vat." Because they had no access to external tools, they hallucinated facts when knowledge was missing or outdated and suffered from error propagation across long chains.
- **Action-Only Models (Early RL / Tool Agents):** Could click buttons or issue API calls, but lacked explicit internal planning. Without verbal working memory, they failed at multi-hop decomposition and struggled to recover when an action returned unexpected results.

Yao et al. observed that **human intelligence seamlessly interleaves both**: we think to plan our next action, act to gather real-world feedback, and update our thinking based on what we observe.

### 2. The Thought -> Action -> Observation Loop

ReAct implements this synergy by structuring the model's context window as an alternating sequence of three explicit steps:

1. **Thought (Internal Reasoning):** The model decomposes the goal, tracks state, diagnoses failures, and decides what information or tool is needed next. *(Generated by the LLM)*
2. **Action (External Tool Call):** The model outputs a structured command from a predefined toolset—such as Search[query], Lookup[term], SQL[query], or Python[code]—and **pauses text generation**. *(Generated by the LLM)*
3. **Observation (Environment Feedback):** The external runtime intercepts the Action, executes it against the real world, appends the raw output as Observation: ... into the prompt context, and hands control back to the LLM. *(Injected by the system)*

This loop repeats dynamically until the model accumulates enough verified evidence to emit a terminal Finish[Answer].

### 3. When ReAct Beats Plain CoT (and When It Doesn't)

ReAct outperforms plain Chain-of-Thought whenever solving the task requires **grounding in external, dynamic, or exact information** rather than pure internal deduction:

| Task Scenario | Winner | Why It Wins |
| --- | --- | --- |
| Multi-Hop Fact Verification & QA (e.g., HotpotQA, Fever) | **ReAct** | Plain CoT hallucinates obscure bridge facts; ReAct searches step-by-step to verify every entity before answering. |
| Live Data & Private Enterprise Systems | **ReAct** | Plain CoT is frozen at its pretraining cutoff; ReAct queries live APIs, SQL databases, and current documentation. |
| Exact Math, Code Execution & Data Analysis | **ReAct** | Plain CoT makes arithmetic slips on large numbers; ReAct delegates computation to a Python interpreter (Observation = exact result). |
| Interactive Environments (Web navigation, ALFWorld) | **ReAct** | Plain CoT cannot observe dynamic state changes; ReAct adapts its plan immediately when a click or API call fails. |
| Pure Self-Contained Logic & Creative Writing | **Plain CoT** | When all facts are already in the prompt (e.g., closed-book riddles or style rewriting), tool calls add unnecessary latency and token overhead. |

## Key Takeaway

In the original 2022 benchmarks, **combining CoT + ReAct** (falling back to internal CoT when search returned nothing, and falling back to ReAct when CoT lacked confidence) achieved the highest overall accuracy—proving that internal reasoning and external acting are complementary rather than mutually exclusive.
