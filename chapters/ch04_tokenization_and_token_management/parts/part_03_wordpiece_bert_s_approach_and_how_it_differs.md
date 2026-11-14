# Chapter 4 - Part 3: WordPiece - BERT's approach and how it differs from BPE

> Chapter 4: Tokenization and Token Management

**WordPiece** is a subword tokenization algorithm developed by Google and famously used in BERT, DistilBERT, and Electra. While it looks structurally similar to Byte-Pair Encoding (BPE), it builds its vocabulary using **likelihood (mutual information)** rather than raw pair frequency, and it tokenizes new text at inference using **greedy longest-match-first** scanning instead of an ordered merge table.

### 1. How WordPiece Builds a Vocabulary (Training)

Like BPE, WordPiece starts with a small base vocabulary of individual characters and iteratively merges pairs until reaching a target size (for example, 30,522 tokens in BERT). However, it uses a smarter scoring formula to pick which pair to fuse next:

$$
\text{Score}\left( A, B \right) = \frac{\text{freq}\left( AB \right)}{\text{freq}\left( A \right) \times \text{freq}\left( B \right)}
$$

- **Prioritizing Rare, Tightly Coupled Pairs.** Instead of blindly merging the most frequent pair overall (which often merges common letters like 'e' + 'r' or 't' + 'h'), WordPiece divides the pair's frequency by the product of each individual token's frequency.
- **Intuition Behind the Formula.** If 'q' and 'u' almost *always* appear together—even if neither letter is super common on its own—their denominator freq(q) × freq(u) is small, giving 'qu' a huge score. Conversely, two hyper-frequent letters that just happen to bump into each other occasionally get penalized.
- **Subword Continuation Prefix (##).** WordPiece marks tokens that do not start a word with a double-hash prefix (##). For instance, "unbelievable" splits into ["un", "##believ", "##able"], preserving exact word-boundary information so the model knows whether "able" appeared as a standalone word or a suffix.

### 2. How WordPiece Encodes Text at Inference

Unlike BPE—which replays an ordered list of merge rules step-by-step—WordPiece uses a fast **Maximum Matching (Longest-Match-First)** algorithm:

1. **Split by Whitespace and Punctuation.** Input text is first broken into whole words (e.g., "unaffordable").
2. **Scan Left-to-Right for the Longest Substring.** Starting from the beginning of the word, the tokenizer searches its vocabulary for the longest prefix that exists in the dictionary (finding "un").
3. **Prepend ## and Repeat.** For the remaining substring ("affordable"), it searches for the longest match starting with ## (finding "##afford"), and repeats on the remainder ("##able").
4. **Fallback to [UNK].** Because classic WordPiece uses a character-level base vocabulary rather than all 256 raw UTF-8 bytes, if a word contains an unseen character (like a rare emoji or foreign symbol), the entire word collapses into a single [UNK] (unknown) token.

## BPE vs. WordPiece Comparison

| Feature | Byte-Pair Encoding (BPE) | WordPiece |
| --- | --- | --- |
| Famous Models | GPT-2/3/4, Llama 3, Mistral, DeepSeek | BERT, DistilBERT, Electra, MobileBERT |
| Merge Selection Criterion | **Raw frequency** (freq(AB)) — merges the most common adjacent pair. | **Likelihood / PMI** (freq(AB) / (freq(A) * freq(B))) — merges pairs that boost corpus probability most. |
| Inference Encoding Algorithm | Replays learned merge rules in **exact priority order**. | **Longest-match-first** greedy scanning from left to right (no merge table saved). |
| Word Boundary Marker | Encodes spaces directly into tokens (e.g., " apple" vs "apple" or Ġ). | Strips spaces and prefixes non-initial subwords with ## (e.g., "##ing"). |
| Unknown Character Handling | **Lossless** (Byte-level BPE falls back to raw UTF-8 bytes; zero <UNK>). | **Lossy** (Classic WordPiece maps words with out-of-vocabulary characters to [UNK]). |

## Why Modern LLMs Favor BPE Over WordPiece

While WordPiece's likelihood criterion produces clean morphological splits (like "play" + "##ing"), modern generative LLMs overwhelmingly use **Byte-Level BPE** or **Unigram/SentencePiece** because WordPiece lacks byte-level fallback—making it fragile on multilingual text, code, and emojis—and its ## prefix convention alters spacing rather than preserving raw text losslessly.

## BERT's approach and how it differs from BPE

**BERT’s approach** uses **WordPiece** tokenization paired with special structural markers ([CLS], [SEP], ##) tailored for bidirectional text understanding, whereas **BPE** (used in GPT, Llama, and Mistral) uses raw frequency merges and lossless byte-level encoding tailored for open-ended text generation.

### 1. How BERT’s Tokenization Pipeline Works

When you feed text into BERT, it runs through three distinct stages before touching the neural network:

- **Basic Pre-Tokenization & Normalization.** BERT splits text on whitespace and punctuation, strips accents (in uncased models like bert-base-uncased), and lowercases all characters. It also separates CJK (Chinese, Japanese, Korean) characters with spaces so each character acts as its own token.
- **WordPiece Subword Splitting.** Every resulting word is scanned from left to right using **longest-match-first** lookup against BERT's fixed 30,522-token vocabulary. Any subword that does not begin a word gets prefixed with ## (for example, "tokenization" splits into ["token", "##ization"]).
- **Special Control Tokens.** BERT wraps every input with task-specific structural tokens:
  - [CLS] is placed at the very start of every sequence to aggregate a sentence-level representation for classification tasks.
  - [SEP] marks the end of a sentence or separates Sentence A from Sentence B in pair tasks (like question answering or natural language inference).
  - [MASK] replaces hidden words during Masked Language Modeling pre-training.

### 2. Core Differences: BERT (WordPiece) vs. BPE

| Dimension | BERT (WordPiece) | Modern LLMs (Byte-Level BPE) |
| --- | --- | --- |
| How Merges Are Chosen | **Mutual Information / Likelihood:**    Scores pairs by$\frac{\text{freq}\left( AB \right)}{\text{freq}\left( A \right) \times \text{freq}\left( B \right)},$    favoring rare pairs that strongly belong together (like q + u). | **Raw Frequency:** Simply merges whichever adjacent pair appears most often in the training corpus. |
| Inference Encoding Rule | **Longest-Match-First:** Greedily grabs the longest matching prefix in the vocabulary; does not store merge history. | **Ordered Merge Replay:** Applies learned merge rules in exact chronological priority order. |
| Whitespace & Word Boundaries | **Destructive (## prefix):** Strips spaces and marks mid-word continuations with ## (e.g., "play" + "##ing"). | **Lossless (Ġ or raw space):** Keeps spaces attached to tokens (e.g., " play" vs "play"), allowing exact reconstruction of formatting and indentation. |
| Handling Unknown Text | **Falls back to [UNK]:** If a word contains an unseen character or emoji, the entire word becomes [UNK]. | **Zero <UNK> tokens:** Falls back to the 256 raw UTF-8 bytes, handling any symbol, code, or script cleanly. |
| Case & Formatting | Commonly lowercases text and strips accents (uncased), losing capitalization cues. | Preserves exact capitalization, newlines, and tabs—critical for coding and multilingual text. |

### 3. Why Each Design Fits Its Architecture

- **Why BERT Used WordPiece.** BERT is an **encoder-only** model built for reading and classifying existing text (sentiment analysis, search ranking, named entity recognition). Losing exact whitespace or mapping a rare emoji to [UNK] rarely hurts classification accuracy, while clean morphological splits (##ed, ##ing) help the bidirectional encoder grasp grammar.
- **Why Generative LLMs Use Byte-Level BPE.** Autoregressive decoders (like GPT-4 and Llama 3) must generate valid Python indentation, JSON syntax, emojis, and multilingual scripts character-for-character. Because BERT's normalization strips spaces and collapses unknown characters into [UNK], it cannot reconstruct arbitrary raw strings—making Byte-Level BPE essential for modern LLMs.
