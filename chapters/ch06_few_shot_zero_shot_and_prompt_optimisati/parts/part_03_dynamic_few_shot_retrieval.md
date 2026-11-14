# Chapter 6 - Part 3: Dynamic Few-Shot Retrieval

> Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)

**Dynamic Few-Shot Retrieval** (also known as **k-NN Prompting** or **Retrieval-Augmented Few-Shot CoT**) is a technique that automatically selects the most relevant worked examples for each incoming user query at runtime, rather than relying on a single fixed set of hardcoded examples. By embedding a curated library of solved Chain-of-Thought examples into a vector database, the system fetches the top k closest matches (typically 3 to 5) on the fly and injects them into the prompt just before inference.

### 1. How the Architecture Works

Instead of maintaining one static prompt, dynamic retrieval operates as a four-step pipeline:

- **Offline indexing.** You build a repository of verified Question + Step-by-Step Reasoning + Answer pairs, convert each question into a dense vector embedding, and store them in a vector index (such as FAISS, Pinecone, or pgvector).
- **Query embedding.** When a new user request arrives, the system embeds the incoming question using the exact same embedding model.
- **Similarity search & filtering.** The retriever searches the vector store for the top k nearest neighbors using cosine similarity, optionally applying diversity filters so the retrieved shots do not all repeat the exact same logic.
- **Similarity-ascending assembly.** The retrieved examples are formatted into the prompt in **ascending order of similarity**—putting the closest match immediately before the user's question to capitalize on the model's recency bias.

### 2. Static vs. Dynamic Few-Shot CoT

| Feature | Static Few-Shot CoT | Dynamic Few-Shot Retrieval |
| --- | --- | --- |
| Example Selection | Fixed set of 3–5 examples for every query | Customized 3–5 examples fetched per query |
| Domain Breadth | Limited to whatever fits in one static prompt | Scales to thousands of distinct edge cases and sub-tasks |
| Prompt Token Cost | Constant, low token count | Constant, low token count (only top k are injected) |
| Engineering Overhead | Minimal; just a text template | Moderate; requires an embedding pipeline and vector store |
| Latency Impact | Zero retrieval overhead | Adds ~10–50 ms for embedding and vector lookup |

### 3. Advanced Retrieval Strategies

- **Structural similarity over surface keywords.** Standard semantic embeddings sometimes match superficial topic words (e.g., matching two problems just because both mention *"apples"*) rather than matching the underlying math or logic structure. To fix this, developers either strip domain nouns before embedding or fine-tune a retriever specifically on reasoning-path similarity.
- **Maximal Marginal Relevance (MMR).** Pure top-k similarity search can accidentally return four near-duplicate examples. Using **MMR** balances relevance to the user's query with diversity among the chosen shots, ensuring broad rule coverage.
- **LLM-verified example banks (STaR / Auto-CoT).** You can bootstrap your retrieval database by running a strong model on unlabeled training questions, keeping only the generated reasoning chains that arrive at the verified ground-truth answer, and indexing those into your store.

### 4. Trade-Offs to Watch Out For

- **Prompt caching invalidation.** Modern LLM APIs offer major cost and latency discounts when the prefix of your prompt stays identical across requests. Because dynamic retrieval changes the examples on every call, it breaks prefix caching—meaning you trade higher accuracy for slightly higher per-token input costs.
- **Garbage-in, garbage-out.** If a noisy or flawed reasoning trace slips into your vector database, it will repeatedly degrade answers whenever similar user queries trigger it.

## The problem with static example sets

Static example sets fail when real-world inputs vary widely because a fixed handful of 3 to 5 examples cannot simultaneously cover every domain edge case, adapt to shifting user patterns, or stay within tight context budgets. While a static prompt works well for narrow, predictable tasks, it becomes a major bottleneck as soon as a system scales to diverse production queries.

### 1. The Coverage vs. Context-Length Trap

- **Insufficient breadth for complex domains.** Real-world tasks—like customer support routing, SQL generation across hundreds of tables, or tax rule compliance—often contain dozens of distinct logic branches. Packing only 4 static examples leaves most of those rules completely unrepresented.
- **Diminishing returns from stuffing more shots.** Trying to solve coverage by cramming 20 or 30 static examples into a single prompt drives up token costs and latency on every single request. Worse, long prompts trigger **"lost-in-the-middle" degradation**, where attention heads miss rules buried in the center of the prompt.

### 2. Surface Bias and Distribution Mismatch

- **Overfitting to narrow templates.** When every incoming query sees the exact same examples, the model develops strong biases toward the labels, phrasing, and reasoning paths shown in that fixed set—even when the user's actual question requires a different approach.
- **Irrelevant context noise.** If a user asks a question about international shipping taxes, feeding them 4 static examples about domestic return policies wastes attention bandwidth on irrelevant rules and increases the risk of hallucinated cross-contamination.

### 3. Brittleness and Maintenance Overhead

- **Silent performance drift.** As user behavior, product catalogs, or business policies evolve over time, a static prompt slowly goes out of sync with live production data.
- **Fragile manual tuning.** Updating a static prompt to fix one newly discovered edge case often degrades accuracy on previously working cases, forcing developers into endless, brittle prompt-tweaking cycles instead of simply adding a new example to a searchable database.

### Static vs. Dynamic Scaling Limits

| Failure Mode | Why Static Example Sets Break | How Dynamic Retrieval Solves It |
| --- | --- | --- |
| Edge-Case Blindness | Cannot fit 50+ distinct rule variations into a single prompt. | Stores thousands of edge cases offline; injects only the 3–5 relevant ones. |
| Irrelevant Distractions | Every query pays the attention penalty of unrelated examples. | Filters out unrelated domains before the LLM ever sees the prompt. |
| Label & Format Skew | Fixed label ratios bias the model toward majority outcomes. | Adapts the example mix to match the structural profile of the live query. |
| High Update Friction | Editing a live system prompt risks breaking existing workflows. | Adding a new example to the vector index fixes edge cases without touching prompt logic. |

## Embedding-based retrieval: pick the best examples per query

**Embedding-based retrieval** picks the best Few-Shot Chain-of-Thought examples per query by converting both your stored example bank and the incoming user question into dense numerical vectors, then using mathematical similarity (like cosine similarity) to fetch the closest matches at runtime. This ensures the LLM always receives worked examples that mirror the exact logic, vocabulary, or edge cases of the current problem without bloating the context window.

### 1. The Four-Stage Retrieval Pipeline

- **Step 1: Offline indexing.** Take a curated repository of verified (Question, Reasoning Trace, Final Answer) records. Pass only the **Question** (or a normalized structural summary of it) through an embedding model to generate a vector, and store that vector alongside the full example in a vector index (e.g., FAISS, pgvector, Qdrant).
- **Step 2: Online query encoding.** When a user submits a new prompt, run the incoming question through the **exact same embedding model** to map it into the identical vector space.
- **Step 3: Nearest-neighbor & diversity filtering.** Compute the cosine similarity between the query vector and all stored example vectors to rank candidates. Apply **Maximal Marginal Relevance (MMR)** to select the top k examples (typically 3 to 5) that are both highly relevant to the query and distinct from one another.
- **Step 4: Similarity-ascending prompt assembly.** Inject the selected examples into the prompt ordered from **least similar to most similar**, placing the closest match right before the target query to exploit the LLM's recency bias.

### 2. Fixing the "Surface-Keyword Trap"

Standard semantic embeddings often match superficial topic words rather than underlying reasoning structure—for example, pairing two math problems just because both mention *"trains"* even though one requires algebra and the other requires probability. You can solve this with three targeted upgrades:

| Technique | How It Works | Best When To Use |
| --- | --- | --- |
| Entity Masking / Skeletonizing | Replace domain nouns and numbers with placeholders (e.g., [ENTITY_A] bought [NUM] items) before generating embeddings. | Math word problems, logic puzzles, and structured SQL/code generation. |
| Reasoning-Trace Indexing | Embed a brief summary of the *solution strategy* or *required rules* alongside the question. | Policy compliance, customer support routing, and legal/tax workflows. |
| Contrastive Fine-Tuning | Fine-tune a small encoder (like BGE or E5) on pairs of questions that share the exact same solution steps. | High-volume production pipelines where retrieval precision directly drives accuracy. |

### 3. Minimal Reference Implementation

```python
import numpy as np


def cosine_similarity(a, b):
  return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_few_shot(
    query_vec, example_bank, top_k=3, diversity_weight=0.7
):
  # example_bank: list of dicts with 'vec' and 'prompt_text'
  scored = [
      (cosine_similarity(query_vec, ex["vec"]), ex) for ex in example_bank
  ]
  scored.sort(key=lambda x: x[0], reverse=True)

  # Greedy MMR selection to avoid near-duplicate examples
  selected = [scored[0][1]]
  candidates = [item[1] for item in scored[1:20]]

  while len(selected) < top_k and candidates:
    best_cand, best_score = None, -1e9
    for cand in candidates:
      rel = cosine_similarity(query_vec, cand["vec"])
      max_sim = max(
          cosine_similarity(cand["vec"], s["vec"]) for s in selected
      )
      mmr = diversity_weight * rel - (1 - diversity_weight) * max_sim
      if mmr > best_score:
        best_score, best_cand = mmr, cand
    selected.append(best_cand)
    candidates.remove(best_cand)

  # Reverse so the closest match sits immediately before the target question
  return list(reversed(selected))
```

### 4. Key Production Guardrails

- **Set a similarity floor.** If the highest cosine similarity score falls below a calibrated threshold (e.g., < 0.65), fall back to a default set of general-purpose "gold standard" examples so the model is not misled by irrelevant matches.
- **Audit the bank continuously.** Log which retrieved example IDs correlate with user thumbs-down or validation failures, and prune or rewrite low-performing traces.
