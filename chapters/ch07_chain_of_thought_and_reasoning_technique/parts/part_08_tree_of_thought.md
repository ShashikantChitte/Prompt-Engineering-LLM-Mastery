# Chapter 7 - Part 4: Tree-of-Thought

> Chapter 7: Chain-of-Thought and Reasoning Techniques

**Tree of Thoughts (ToT)**—introduced by Yao et al. (2023)—generalizes Chain-of-Thought (CoT) prompting by framing problem-solving as a deliberate search over a branching tree of intermediate reasoning steps, rather than a single linear chain.

Instead of committing to one left-to-right token sequence and hoping it reaches the right answer, ToT allows an LLM to **explore multiple paths simultaneously, evaluate its own progress at each step, and backtrack** when a line of reasoning hits a dead end.

### 1. Why Linear CoT Hits a Wall

Both Standard CoT and Self-Consistency suffer from two structural limitations on complex planning and search problems:

- **No Local Lookahead:** The model generates step t+1 without considering whether that step leads to a viable future state.
- **No Backtracking:** If the model makes a bad strategic choice at Step 2 (such as choosing the wrong numbers in the Game of 24 or writing a flawed lemma in a proof), it cannot undo Step 2 and try a different branch—it is stuck riding that bad path to the end.

### 2. The Four Core Components of Tree of Thoughts

ToT wraps the LLM inside a classic symbolic search algorithm (like Breadth-First Search or Depth-First Search) composed of four building blocks:

1. **Thought Decomposition:**

Break the problem into coherent intermediate units ("thoughts")—such as a single equation in math, a paragraph plan in creative writing, or a move in chess—large enough to evaluate progress, yet small enough to generate multiple alternatives.

2. **Thought Generator (G):** At any given node in the tree, prompt the LLM to propose k distinct candidate next steps (either by sampling multiple CoT steps independently or prompting the model to *"propose 3 different next steps"*).
3. **State Evaluator (V):** Prompt the LLM itself (or a heuristic function) to score each candidate branch's likelihood of solving the problem—often classifying nodes into labels like **sure**, **maybe**, or **impossible**, or assigning a numerical score from 1 to 10.
4. **Search Algorithm:** Use a tree-traversal strategy to decide which branches to expand and which to prune:
  - **Breadth-First Search (BFS):** Keeps the top b most promising states at each depth level (ideal for shallow problems like the Game of 24).
  - **Depth-First Search (DFS):** Explores one promising branch deeply until solved or flagged as impossible, then backtracks to the parent node to try the next sibling (ideal for puzzles, code synthesis, or theorem proving).

### 3. Comparison: CoT vs. Self-Consistency vs. ToT

| Feature | Chain-of-Thought (CoT) | Self-Consistency | Tree of Thoughts (ToT) |
| --- | --- | --- | --- |
| Reasoning Topology | Single linear chain | Multiple independent linear chains | Branching tree with shared prefixes |
| Step-Level Evaluation | None | None (evaluates only final answers) | Explicit self-evaluation at every node |
| Backtracking & Pruning | No | No | **Yes** (abandons dead ends early) |
| Best Use Cases | Standard math & logic word problems | Discrete QA & classification | Planning, puzzles (Sudoku, Game of 24), creative outlining |
| Compute Cost | Low (1x) | Medium (N× linear passes) | **High** (10× to 100× LLM calls per problem) |

## Practical Trade-Off

While ToT achieved massive accuracy leaps on search-heavy benchmarks (e.g., jumping GPT-4 from **4% to 74%** on the Game of 24), its high token cost and latency make it impractical for routine queries. In modern systems, ToT is typically reserved for **high-stakes planning, code debugging, and complex constraint-satisfaction tasks**, or distilled into RL-trained reasoning models that learn to backtrack natively inside a single continuous stream.

## Tree of Thought - branching exploration for planning problems

**Tree of Thoughts (ToT)** excels at **planning and constraint-satisfaction problems** because it replaces blind, left-to-right token generation with deliberate branching exploration, lookahead evaluation, and backtracking.

In planning tasks—such as scheduling, multi-step code refactoring, puzzle solving, or strategic decision-making—an early choice constrains every valid move that follows. ToT prevents the model from getting trapped in dead ends by exploring multiple future trajectories before committing.

### 1. Why Planning Problems Require Branching Exploration

Linear Chain-of-Thought fails on complex planning tasks due to three structural bottlenecks:

- **Irreversible Early Commitments:** Choosing a flawed initial step (e.g., picking the wrong database schema or starting a puzzle with an unsolvable move) guarantees failure later, even if every subsequent step is executed accurately.
- **Delayed Constraint Violations:** In planning, a mistake at Step 1 often does not violate a rule until Step 4. Linear generation has no mechanism to rewind back to Step 1 once the conflict becomes visible.
- **Combinatorial Search Spaces:** Planning requires weighing competing trade-offs across multiple possible futures rather than following a single deterministic formula.

### 2. How ToT Executes Planning Step-by-Step

To solve a planning problem, ToT alternates between **expanding candidate actions** and **pruning unviable futures**:

- **Step 1: Propose Candidate Actions (Branching):** At the current plan state s_{t}, prompt the LLM to generate k distinct next actions (e.g., *"Generate 3 distinct architectural approaches to handle authentication"*).
- **Step 2: Simulate & Evaluate States (Lookahead):** For each proposed branch, prompt an evaluator call (or run a deterministic validator/compiler) to assess feasibility against problem constraints, labeling each branch as **sure** (solvable/optimal), **maybe** (plausible, needs further steps), or **impossible** (violates a constraint).
- **Step 3: Prune & Select (Search Policy):**
  - **Beam / Breadth-First Search (BFS):** Retain only the top b highest-scoring partial plans at each stage and discard the rest, keeping compute bounded while exploring parallel strategies.
  - **Depth-First Search (DFS) with Backtracking:** Follow the single highest-scoring plan step-by-step until either a complete valid plan is found or a node evaluates to impossible—at which point the search backtracks to the most recent viable parent node and tries the next sibling branch.

### 3. Concrete Planning Walkthrough: Multi-Constraint Scheduling

Suppose an LLM must schedule 4 dependent tasks across a 3-hour window with resource conflicts:

| Tree Depth | Branching Exploration & Pruning |
| --- | --- |
| Depth 1 (Initial Move) | Proposes starting with **Task A**, **Task B**, or **Task C**.   Evaluator flags **Task C** as impossible (missing prerequisite) and prunes it immediately. |
| Depth 2 (Expand A & B) | Under **Task A**, proposes A -> B and A -> D.   Under **Task B**, proposes B -> A and B -> D. |
| Depth 3 (Lookahead & Backtrack) | A -> B -> D hits a resource timeout (impossible) → **backtracks** to A.   A -> D -> B satisfies all time and resource constraints (sure) → **returns winning plan**. |

## Practical Enhancements for Production Planning

- **Hybrid Symbolic-LLM Evaluation:** Wherever possible, replace the LLM state evaluator with a **deterministic code verifier** (such as a unit test runner, SQL syntax checker, or constraint solver) to eliminate self-evaluation hallucinations.
- **Monte Carlo Tree Search (MCTS):** For deep planning horizons, combine ToT with MCTS (using Upper Confidence Bound scores) to dynamically balance exploiting high-scoring plans and exploring under-tested branches.
