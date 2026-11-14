# Chapter 4 - Part 1: Why tokenization exists - models never see words, only integers

> Chapter 4: Tokenization and Token Management

**Tokenization** exists because neural networks cannot process raw text directly—they can only perform math on numbers—and splitting text into subword chunks (**tokens**) balances **vocabulary size**, **sequence length**, and the ability to handle **unseen or misspelled words**.

### 1. Neural Networks Only Understand Numbers

At its core, an LLM is a giant matrix-multiplication engine. Before a model can read a sentence, every piece of text must be mapped to a unique integer ID from a fixed lookup table (the vocabulary), which then fetches a dense numerical vector (an embedding). Tokenization defines the exact boundary of each lookup entry.

### 2. Why Not Characters or Whole Words?

Modern LLMs use **subword tokenization** (like Byte-Pair Encoding, or BPE) because both extremes fail in practice:

| Granularity | How It Splits "unbelievable" | Why It Fails for LLMs |
| --- | --- | --- |
| Character-Level | ["u", "n", "b", "e", "l", "i", "e", "v", "a", "b", "l", "e"] | **Sequences become way too long.** A 1,000-word essay turns into ~5,000+ tokens, exploding quadratic attention compute and shrinking the effective context window. Characters also carry very little semantic meaning on their own. |
| Whole-Word-Level | ["unbelievable"] | **Vocabulary explodes and breaks on new words.** English alone has hundreds of thousands of inflections, compound words, typos, code variables, and URLs. Any word missing from the dictionary becomes an <UNK> (unknown) token, destroying information. |
| Subword-Level (Modern Standard) | ["un", "believ", "able"] | **Hits the sweet spot.** Common words stay single tokens ("the", "apple"), while rare words split into meaningful roots and affixes. It handles any new word, typo, or programming syntax without ever falling back to <UNK>. |

### 3. Direct Impact on Inference Performance & Cost

How a tokenizer chunks text directly governs how fast and expensive an LLM is to run:

- **Compression Ratio = Speed.** A smarter tokenizer packs more text into fewer tokens. For example, upgrading from GPT-3's 50K vocabulary to Llama 3's 128K vocabulary reduced token counts by ~15%, which directly cuts **prefill compute**, **KV cache VRAM usage**, and **decode latency** without changing the model weights.
- **Multilingual and Code Efficiency.** Early tokenizers trained mostly on English broke non-Latin scripts (like Hindi, Marathi, or Japanese) into individual UTF-8 bytes—making non-English prompts 3x to 5x slower and more expensive. Modern tokenizers allocate dedicated vocabulary slots to multilingual scripts and whitespace indentation so they run efficiently.
- **Quirky LLM Failure Modes.** Because models see token IDs rather than individual letters, tokenization explains classic blind spots like struggling to count the number of "r"s in "strawberry" (seen as ["str", "aw", "berry"]) or doing multi-digit arithmetic poorly when numbers split inconsistently ("1234" vs "123" + "4").

## Models never see words, only integers

An LLM never sees strings, letters, or words at any point during training or inference—it strictly receives a sequence of **integer IDs** and outputs a probability distribution over those same **integer IDs**. Everything involving human-readable text happens outside the neural network in a separate pre- and post-processing step.

### The Full Pipeline: Text to Integers and Back

When you send a prompt to an LLM, the text goes through a strict four-stage conversion loop:

1. **Tokenizer Encoding (Text → Integers).** A rule-based algorithm (like BPE) splits your string into chunks and looks up each chunk's index in a fixed dictionary. For example, "Hello world!" becomes [9906, 1917, 0].
2. **Embedding Lookup (Integers → Vectors).** Inside the model's very first layer, those integers act as **row indices** into a massive matrix called the embedding table (shape: vocab_size × d_model). Integer 9906 simply fetches row 9,906—a list of floating-point numbers representing that token's learned meaning.
3. **Transformer Math (Vectors → Logits).** Every attention layer, MoE router, and feed-forward block operates purely on those floating-point vectors. At the final layer, the model multiplies the output vector by an unembedding matrix to produce one raw score (logit) for every integer ID in the vocabulary (e.g., 128,256 scores).
4. **Decoding & Detokenization (Integers → Text).** A sampling rule picks one winning integer ID (say, 2746), appends it to the integer list, and the tokenizer maps 2746 back to its corresponding text string (" How").

### Why This Mental Model Explains Weird LLM Behavior

Keeping in mind that models only process arbitrary row indices clears up many confusing LLM quirks:

- **No Inherent Spelling Awareness.** To the model, token 1917 (" world") and token 14957 ("world", without a leading space) are completely separate rows in a matrix. The model does not know they share the same five letters unless it learns that relationship indirectly across billions of training examples.
- **Glitch Tokens.** If a specific string appeared in training data only in weird contexts (like Reddit usernames or corrupted logs), its corresponding integer row receives bizarre gradient updates, causing the model to hallucinate or crash whenever that exact integer ID is fed in.
- **Exact Arithmetic Struggles.** Because numbers are chunked arbitrarily into integers (e.g., 380 might be one integer while 381 is split into 38 and 1), the model cannot align place values column-by-column like a calculator—it has to memorize numerical relationships across thousands of distinct token IDs.
