# Chapter 4 - Quick Check

> Chapter 4: Tokenization and Token Management

> Related part: Context window limits - hard limits, soft limits, and the LostInTheMiddle failure

### Q1. You send the same 500-word document to GPT-4 in English and in Hindi. The Hindi version costs about 3x more tokens. Why? What property of the tokenizer causes this?

The Hindi version costs about **3x more tokens** because Byte-Pair Encoding (BPE) tokenizers learn merges based on raw corpus frequency, and GPT-4's tokenizer (cl100k_base) was trained overwhelmingly on English text—combined with the fact that **UTF-8 encodes each Devanagari character as 3 bytes** rather than 1 byte.

#### 1. The Two Tokenizer Properties Behind the 3x Penalty

- **English-Skewed Training Data (Vocabulary Allocation).** During BPE training, the algorithm allocates its fixed vocabulary slots (e.g., 100,000 tokens) to the most frequent byte pairs in the training corpus. Because English dominated that training mix, common English words ("information", "government", "understanding") earned single whole-word tokens. Hindi appeared far less frequently, so Hindi words received far fewer merge slots and break down into tiny syllable fragments, individual characters, or raw bytes.
- **Multi-Byte UTF-8 Encoding (3 Bytes per Devanagari Character).** Every ASCII English letter (a–z) takes **1 byte** in UTF-8. Every Hindi Devanagari character (क, ा, म, ्) requires **3 bytes** in UTF-8 (0xE0 0xA4 ...). When a Hindi character or vowel sign (*matra*) hasn't been merged into a dedicated vocabulary token, Byte-Level BPE falls back to representing that single character as **2 or 3 separate byte tokens**.

#### 2. Concrete Example: English vs. Hindi

| Phrase | Character Count | UTF-8 Bytes | Approximate Token Split (cl100k_base) | Token Count |
| --- | --- | --- | --- | --- |
| "How are you?" | 12 chars | 12 bytes | ["How", " are", " you", "?"] | **4 tokens** |
| "आप कैसे हैं?" | 12 chars | 28 bytes | Split across individual Devanagari consonants, *matras*, and byte fallbacks | **~11–13 tokens** |

#### 3. Real-World Impact & How Newer Tokenizers Improve This

This phenomenon—known in NLP research as **high tokenizer fertility** (average tokens per word)—causes three direct penalties for Indian languages like Hindi and Marathi:

- **3x Higher API Cost.** You pay per token, so translating or analyzing a Hindi document costs ~3x more than the identical English document.
- **3x Slower Generation & Smaller Context Window.** A 128K context window holds ~95,000 English words, but only ~30,000–35,000 Hindi words, and autoregressive decoding takes 3x as many forward passes to emit the same sentence.
- **How Newer Models Fix It.** Later tokenizers—such as OpenAI's **o200k_base** (used in GPT-4o / o3) and Indic-focused models (like **Sarvam** or **Gemma 2/3** with 256K vocabularies)—doubled vocabulary sizes and included significantly more Devanagari training text, cutting Hindi token bloat down from **~3x–4x** to roughly **1.3x–1.6x** compared to English.

### Q2. A colleague says "we have a 128k context window so we can safely use 128k tokens of retrieved documents." What is wrong with this reasoning?

Stuffing **128k tokens of retrieved documents** into a 128k context window fails both mechanically (it leaves zero room for system prompts, the user's question, and the model's answer) and **qualitatively** (accuracy, latency, and cost degrade severely long before hitting the hard limit).

#### 1. Hard Budget Violations (The Math Doesn't Leave Room to Answer)

A 128k context window is the **total shared budget** for everything in a single request—not just your retrieved documents:

- **Zero Space for the Output Reply.** The model's generated response (and any hidden reasoning tokens) must fit *inside* that same 128k window. If retrieved documents take 128,000 tokens, the API will either reject the request immediately or leave **0 tokens** for the model to generate an answer.
- **No Room for Prompts, Schemas, or Chat History.** System instructions, JSON tool definitions, conversation history, and the user's actual query all consume tokens before a single document chunk is added.

#### 2. Soft-Limit Failures (Quality, Speed, and Cost Break Down)

Even if you trimmed the documents slightly to 120k tokens so the request technically succeeds, dumping massive amounts of retrieved text degrades system performance across four dimensions:

| Failure Mode | What Happens at ~120k+ Tokens | Why It Hurts Production Apps |
| --- | --- | --- |
| "Lost in the Middle" & Attention Dilution | Retrieval accuracy forms a U-shaped curve—facts buried in the middle of 120k tokens get missed, and irrelevant chunks distract the model's attention weights. | Precision on multi-hop questions often drops by **15% to 30%+** compared to passing only the top 5–10 relevant chunks. |
| Time-to-First-Token (TTFT) Latency Spikes | Self-attention prefill must process all 120k tokens before emitting the very first word. | Users wait several seconds (or tens of seconds) staring at a blank screen on every turn. |
| Runaway API Costs & Rate-Limit Throttling | You pay per input token on every request, and massive prompts rapidly burn through Tokens-Per-Minute (**TPM**) quotas. | Ten concurrent users sending 120k tokens each consumes **1.2M tokens** in seconds, throttling your entire app. |
| KV Cache VRAM Exhaustion (Self-Hosted) | A single 128k request consumes gigabytes of GPU High Bandwidth Memory (HBM) just for its KV cache. | Collapses batch sizes to 1 or triggers Out-of-Memory (OOM) crashes under concurrent traffic. |

#### 3. The Right Rule of Thumb for RAG

Instead of filling the context window to capacity, **treat the context window like RAM, not a hard drive**:

- **Retrieve Broadly, Pass Selectively.** Retrieve 30–50 candidate chunks using hybrid search, run a fast **Cross-Encoder reranker** to keep only the top **5 to 10 highest-signal chunks** (~3k–8k tokens), and place the best chunks at the very top and bottom of the prompt.
- **Reserve Budget Explicitly.** Cap retrieved documents at **50% to 70%** of the window at most, reserving clear headroom for system instructions, conversation history, and maximum output tokens.

### Q3. You are building a RAG pipeline that retrieves 5 documents. Research shows the answer is in document 3 (the middle one). How should you reorder the documents to minimize the LostInTheMiddle risk?

To minimize the **"Lost in the Middle"** risk, you should reorder the 5 documents using a **U-shaped (sandwich) interleaving strategy**—placing the highest-relevance documents at the **very beginning** and **very end** of the context, while pushing lower-relevance documents into the middle.

If you know (or your reranker scores) that **Document 3** holds the answer, place **Document 3 first (or last)** rather than leaving it in position 3.

### Optimal Ordering Strategy (Ranked by Relevance)

Suppose a reranker scores your 5 retrieved documents from most relevant (Rank 1) to least relevant (Rank 5). Instead of feeding them in standard descending order (1, 2, 3, 4, 5), arrange them so the strongest evidence sits at the **primacy** and **recency** edges:

- **Recommended Order:** [Doc 3 (Rank 1), Doc 2 (Rank 3), Doc 5 (Rank 5), Doc 4 (Rank 4), Doc 1 (Rank 2)] *(or placing the single highest-scoring document at the very end right before the user's question: [Rank 2, Rank 4, Rank 5, Rank 3, Rank 1])*.

| Prompt Position | Attention Strength | Which Document to Place Here |
| --- | --- | --- |
| Position 1 (Start) | **High (Primacy Peak)** | **Document 3** (the primary answer source) or your #2 strongest document. |
| Position 2 | Moderate | Moderate-relevance supporting context. |
| Position 3 (Middle) | **Lowest (Attention Valley)** | Least relevant / noisy distractor document (Rank 5). |
| Position 4 | Moderate | Moderate-relevance supporting context. |
| Position 5 (End) | **High (Recency Peak)** | Your #2 strongest document—or **Document 3** right before the final question. |

### Why This Works in Production

- **Exploits Both Edges.** LLMs pay disproportionately high attention to the very start of the prompt (due to **attention sinks**) and the very end right before generation begins (due to **recency bias**).
- **Standardizes RAG Post-Processing.** In real pipelines where you don't know ahead of time which document contains the answer, frameworks like **LangChain** (LongContextReorder) and **LlamaIndex** automatically run a Cross-Encoder reranker on retrieved chunks and interleave them so odd-ranked documents (1, 3, 5...) sit at the edges and even-ranked documents (2, 4...) move toward the center.
- **Bonus Tip—Repeat the Question at the End.** Placing the user's query *after* the 5 reordered documents ensures the model attends to the final document (Position 5) immediately before generating its first answer token.

### Q4. What is the difference between BPE and WordPiece in terms of how they select which subword units to create? Which one does GPT-4 use?

BPE (Byte-Pair Encoding) selects subword units based on raw frequency, while WordPiece selects them based on likelihood (mutual information). **GPT-4 uses Byte-Level BPE** (implemented via OpenAI's tiktoken library with the cl100k_base encoding).

#### 1. How They Differ in Selecting Subwords

Both algorithms start with individual base units (characters or raw bytes) and iteratively merge pairs until hitting a target vocabulary size, but they score candidate pairs differently:

- **BPE (Raw Pair Frequency).** At every step, BPE counts how many times each adjacent pair (A, B) appears across the corpus and merges the single pair with the **highest raw count**:

$$
{\text{Score}}_{\text{BPE}}\left( A, B \right) = \text{freq}\left( AB \right)
$$

Because it only looks at raw counts, BPE frequently merges common letters or prefixes (like 'e' + 'r' or 't' + 'h') simply because those letters appear everywhere.

- **WordPiece (Likelihood / Mutual Information).** WordPiece chooses the pair whose merge increases the overall probability of the training corpus the most. It divides the pair's frequency by the product of each individual token's frequency:

$$
{\text{Score}}_{\text{WordPiece}}\left( A, B \right) = \frac{\text{freq}\left( AB \right)}{\text{freq}\left( A \right) \times \text{freq}\left( B \right)}
$$

By penalizing tokens that are already hyper-frequent on their own, WordPiece prioritizes **tightly coupled pairs** (like 'q' + 'u' or specific morphological roots) that almost always co-occur, even if their raw count is lower.

#### 2. Quick Comparison

| Feature | Byte-Pair Encoding (BPE) | WordPiece |
| --- | --- | --- |
| Selection Criterion | **Highest raw frequency** (freq(AB)). | **Highest likelihood gain** (freq(AB) / (freq(A) * freq(B))). |
| Encoding at Inference | Replays learned merge rules in exact chronological priority order. | Uses greedy **longest-match-first** scanning left-to-right. |
| Models That Use It | **GPT-4**, GPT-4o, Llama 3, Mistral, DeepSeek | BERT, DistilBERT, Electra |

### Q5. Why does tiktoken not require an API key to count tokens? What is actually happening when you call enc.encode(text)?

tiktoken does not require an API key because tokenization is a purely deterministic, local preprocessing step—not a neural network inference call. When you call enc.encode(text), a fast Rust-backed engine runs entirely on your local CPU using a static, pre-trained vocabulary file to slice your string into subword chunks and map them to integer IDs.

#### 1. Why No API Key Is Needed

- **Separate From the Model.** Tokenizers live outside the LLM. OpenAI openly publishes the vocabulary lookup tables (such as cl100k_base.tiktoken and o200k_base.tiktoken) as public static files.
- **Zero GPU or Cloud Compute.** Counting tokens does not run any matrix multiplications or touch OpenAI's servers. Once the ~2 MB vocabulary file is downloaded and cached locally on your first run, tiktoken works 100% offline.

#### 2. What Actually Happens Inside enc.encode(text)

When you invoke enc.encode(text), tiktoken executes a four-stage deterministic pipeline in Rust:

1. **Regex Pre-Tokenization (Splitting into Chunks).** First, tiktoken applies a compiled regular expression (specific to the encoding) to split your raw string into coarse pieces—separating contractions ('s, 're), words with their leading spaces (" apple"), punctuation, whitespace runs, and 1–3 digit number groups. This prevents merges from crossing word or punctuation boundaries.
2. **UTF-8 Byte Conversion.** Each regex chunk is converted into its raw **UTF-8 byte sequence** (a list of integers from 0 to 255). For example, " cat" becomes [32, 99, 97, 116].
3. **Greedy BPE Merge Loop (Priority-Ordered Fusions).** Inside each chunk, tiktoken checks all adjacent byte/token pairs against its loaded **merge rank table** (a hash map storing the exact priority rank learned during tokenizer training). It repeatedly finds the pair with the **lowest rank number (highest priority)**, fuses them into a single new token ID, and repeats until no adjacent pairs remain in the merge table.
4. **Integer Array Output.** Finally, tiktoken concatenates the resulting token IDs from every chunk into a single flat Python list[int] (e.g., [9906, 1917, 0]) and returns it.

### Quick Summary

| Step | Operation | Where It Runs |
| --- | --- | --- |
| 1. Pre-Tokenize | Splits text into words, spaces, numbers, and punctuation via regex. | Local CPU (Rust) |
| 2. UTF-8 Encode | Turns each piece into base byte IDs (0–255). | Local CPU (Rust) |
| 3. BPE Merges | Repeatedly merges adjacent pairs using the cached .tiktoken priority dictionary. | Local CPU (Rust) |
| 4. Return IDs | Outputs the final list of integer token IDs. | Local Python memory |

### Q6. A prompt has this opening sentence: "I would be very grateful if you could please assist me in analyzing the following data and providing your expert insights and recommendations." How many tokens could this be compressed to without losing any actual instruction? Rewrite it.

The original 26-word sentence (**28 tokens** in GPT-4 / GPT-4o) can be compressed down to **7–8 tokens**—a **~75% reduction**—without losing a single bit of actual instruction.

### Compressed Rewrite

**"Analyze this data and provide key recommendations."** *(8 tokens)*

*(Or even tighter:* ***"Analyze this data; provide insights and recommendations."*** *—* ***7 tokens****)*

### Token-by-Token Breakdown

| Version | Text | Token Count (o200k_base) | What Changed |
| --- | --- | --- | --- |
| Original | *"I would be very grateful if you could please assist me in analyzing the following data and providing your expert insights and recommendations."* | **28 tokens** | Contains 14 tokens of pure conversational politeness (*"I would be very grateful if you could please assist me in..."*) and redundant filler (*"the following"*, *"your expert"*). |
| Compressed | *"Analyze this data; provide insights and recommendations."* | **7 tokens** | Preserves all three core imperatives (**analyze**, **insights**, **recommendations**) and the target object (**data**) while stripping 100% of the fluff. |

### Q7. The number "2023" tokenizes differently from "2024" in some tokenizers. Why does this happen, and what does it reveal about how LLMs handle arithmetic?

"2023" and "2024" tokenize differently in older tokenizers because BPE allocates vocabulary tokens based on raw frequency in the training data, rather than understanding mathematical structure. If a tokenizer was trained on a dataset collected around 2023 or 2024, whichever year appeared more frequently in the text earned its own dedicated single token (e.g., ["2023"] = 1 token), while a less frequent or future year got split into arbitrary subword pieces (e.g., ["202", "4"] or ["20", "24"] = 2 tokens).

#### 1. Why the Token Split Differs

- **Corpus Frequency Bias.** During Byte-Pair Encoding (BPE) training, digit strings compete alongside words for a fixed number of vocabulary slots. Years like 1999, 2020, or 2023 appear millions of times in dates, copyright footers, and articles, so BPE merges them into a single token ID. A year that appeared less often in the snapshot—such as 2024 or 2047—fails to make the frequency cutoff and stays split into smaller chunks.
- **Regex Pre-Tokenization Rules.** To prevent arbitrary long numbers from eating up the entire vocabulary, modern tokenizers (like GPT-4's cl100k_base and Llama 3) apply a regex rule that slices numbers into **1-to-3-digit chunks** (or single digits in Llama 3). Even with 3-digit chunking, "2023" splits into ["202", "3"] while "100" stays ["100"], and left-to-right grouping shifts boundaries depending on total digit count ("1234" → ["123", "4"] vs. "12345" → ["123", "45"]).

#### 2. What This Reveals About How LLMs Handle Arithmetic

This inconsistent chunking exposes three fundamental truths about LLM math capabilities:

- **LLMs See Arbitrary Symbols, Not Place Values.** Inside the Transformer, "2023" (say, integer ID 15482) and "2024" (two separate integer IDs, 12345 + 19) are completely unrelated rows in an embedding matrix. Unlike a human or calculator that aligns **ones, tens, hundreds, and thousands columns** systematically, an LLM has no built-in structural awareness of place value.
- **Arithmetic Is Learned Pattern Matching, Not Symbolic Execution.** Because digit boundaries shift unpredictably (e.g., adding 1 to 2023 changes a 1-token input into a 2-token output), the model cannot learn a single universal addition rule. Instead, it relies on memorized statistical associations across thousands of subword combinations—which is why LLMs easily solve common sums (2000 + 24) yet stumble on large, arbitrary multi-digit multiplication (73849 × 29184).
- **Why Single-Digit Tokenization Improved Math.** Recognizing this flaw, architectures like **Llama 3**, **Gemma**, and **PaLM** deliberately forced their tokenizers to split *all* numbers into **individual single digits** ("2024" → ["2", "0", "2", "4"]). Consistent 1-digit granularity gives every number uniform place-value alignment, dramatically boosting multi-digit arithmetic accuracy.
