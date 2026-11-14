# Chapter 4 - Part 2: Byte-Pair Encoding (BPE) - how the algorithm builds a vocabulary from scratch

> Chapter 4: Tokenization and Token Management

**Byte-Pair Encoding (BPE)** is a data compression algorithm adapted into the standard subword tokenization method used by modern LLMs (such as GPT-4, Llama 3, and Mistral). It builds a fixed-size vocabulary by starting with individual characters (or raw UTF-8 bytes) and iteratively merging the most frequently occurring adjacent pairs into new single tokens.

## How BPE Builds a Vocabulary (Training)

Before training an LLM, the tokenizer runs a deterministic counting loop over a large text corpus until it reaches a target vocabulary size (e.g., 50,000 or 128,000 tokens).

1. **Initialize with Base Units.** Break all text into the smallest base units—typically the 256 possible raw UTF-8 bytes (Byte-Level BPE).
2. **Count Adjacent Pairs.** Scan the corpus and count how often every adjacent pair of tokens appears side-by-side.
3. **Merge the Winner.** Find the single most frequent pair (say, 'e' + 'r' appearing 50,000 times), mint a new token 'er' with the next available integer ID, and replace every adjacent 'e' 'r' in the corpus with 'er'.
4. **Repeat.** Run steps 2 and 3 thousands of times. Common roots ('play'), suffixes ('ing'), and whole frequent words (' the') naturally emerge as single tokens, while rare words stay broken into smaller pieces.

## Step-by-Step Mini Example

Suppose our tiny training corpus consists of just three words with their frequency counts: "low" (5×), "lower" (2×), and "newest" (6×).

| Step | Current Tokenized Corpus | Most Frequent Pair | New Token Created |
| --- | --- | --- | --- |
| Start | l o w (5), l o w e r (2), n e w e s t (6) | e + s (appears 6× in newest) | es |
| Merge 1 | l o w (5), l o w e r (2), n e w es t (6) | es + t (appears 6×) | est |
| Merge 2 | l o w (5), l o w e r (2), n e w est (6) | l + o (appears 7× across low/lower) | lo |
| Merge 3 | lo w (5), lo w e r (2), n e w est (6) | lo + w (appears 7×) | low |
| Result | low (5), low e r (2), n e w est (6) | — | Vocabulary now includes es, est, lo, low |

## How BPE Encodes New Text at Inference

When you send a prompt to a trained model, the tokenizer does **not** recount frequencies. Instead, it applies its saved **merge table** in exact priority order:

- **Greedy Priority Merges.** It breaks your input string into UTF-8 bytes, checks which adjacent pair in your prompt appears earliest in its learned merge list, merges that pair, and repeats until no more valid merges exist.
- **Zero Unknown (<UNK>) Tokens.** Because modern **Byte-Level BPE** starts with all 256 single-byte values in its base vocabulary, any character—including emojis, typos, rare scripts, or raw code—can always fall back to its individual UTF-8 bytes if no larger merges exist.
- **Pre-Tokenization Rules.** Modern BPE tokenizers (like OpenAI's tiktoken) apply regex splitting rules *before* merging so punctuation and numbers don't accidentally fuse with words (for example, preventing "dog.", "dog!", and "dog?" from becoming three separate vocabulary entries).

## Trade-Offs of BPE

- **Strengths.** Simple, deterministic, lossless (reversing the IDs reconstructs the exact original string), and adapts automatically to whatever languages or code appear in the training corpus.
- **Weaknesses.** Greedy merging can occasionally split words awkwardly (e.g., splitting "unfair" differently from "un-fair"), and languages underrepresented in the tokenizer's training data get fragmented into many single-byte tokens, slowing down inference.

## How the algorithm builds a vocabulary from scratch

Building a **Byte-Pair Encoding (BPE)** vocabulary from scratch is an iterative, greedy compression loop that starts with individual raw bytes and repeatedly fuses the most frequent adjacent pairs into new tokens until a target vocabulary size is reached.

### The 5-Step Algorithm

### Step 1: Pre-Tokenize and Count Word Frequencies

Instead of scanning a massive 10-terabyte text file linearly on every pass, the algorithm first splits the training text into chunks (using whitespace and regex rules) and counts how often each unique chunk occurs.

- **Chunking Rules.** Punctuation, numbers, and leading spaces are separated cleanly so merges cannot cross word boundaries (preventing "dog." and "dog!" from becoming separate tokens).
- **Frequency Dictionary.** A corpus of billions of words collapses into a compact dictionary of unique chunks and their counts, such as {" apple": 45000, " apples": 12000, " eating": 31000}.

### Step 2: Initialize the Base Vocabulary

Every unique chunk is broken down into its smallest indivisible units—typically the **256 possible raw UTF-8 bytes**.

- **Starting Tokens.** IDs 0 through 255 are assigned to every possible single byte (0x00 to 0xFF).
- **Special Tokens.** Control tokens like <|endoftext|>, <|begin_of_text|>, or <|im_start|> are reserved either at the very beginning or added at the very end of the vocabulary.
- **Initial Split.** " apple" becomes a sequence of 6 byte tokens: [' ', 'a', 'p', 'p', 'l', 'e'].

### Step 3: Tally All Adjacent Pair Frequencies

The algorithm iterates through every unique chunk in the frequency dictionary and counts how often each adjacent pair of tokens appears across the entire dataset.

- **Weighted Counting.** If the pair ('p', 'p') appears inside " apple" (which occurs 45,000 times) and " apples" (which occurs 12,000 times), its total corpus score is 45,000 + 12,000 = 57,000.
- **Pair Table.** Every adjacent pair receives an exact total occurrence count across the whole corpus.

### Step 4: Merge the Highest-Scoring Pair

The algorithm selects the single pair with the highest global frequency and creates a new token.

- **Mint a New Token ID.** Suppose (' ', 't') has the highest score. The algorithm assigns it the next available integer ID (e.g., ID 256 = ' t').
- **Record the Merge Rule.** It saves the rule (' ', 't') -> ' t' to an ordered **merge table**. The exact order in which rules are learned becomes the strict priority order used later during inference.
- **Rewrite the Corpus.** Every adjacent ' ' followed by 't' in the working dictionary is replaced with the single new token ' t'.

### Step 5: Loop Until Target Vocabulary Size

Steps 3 and 4 repeat in a tight loop until the vocabulary hits the engineer's chosen size (for example, 50,257 for GPT-2 or 128,256 for Llama 3).

- **Incremental Updates.** Rather than recounting the entire dictionary from scratch on every step, optimized implementations (like Hugging Face tokenizers or minbpe) only update pair counts for the specific words affected by the latest merge.
- **Final Output.** Once the target size is reached, the algorithm exports two artifacts: the **Vocabulary Map** (token string <-> integer ID) and the **Ordered Merge List**.

### Concrete Code Walkthrough (Minimal Python Implementation)

Here is the exact core loop in plain Python (popularized by Andrej Karpathy's minbpe):

```python
def get_stats(ids):
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, new_id):
    new_ids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            new_ids.append(new_id)
            i += 2
        else:
            new_ids.append(ids[i])
            i += 1
    return new_ids

# Start with raw UTF-8 bytes (IDs 0..255)
text = "low low lower newest newest"
tokens = list(text.encode("utf-8"))
merges = {}

# Perform 5 merges to grow vocabulary from 256 to 261
for i in range(5):
    stats = get_stats(tokens)
    top_pair = max(stats, key=stats.get)
    new_id = 256 + i
    tokens = merge(tokens, top_pair, new_id)
    merges[top_pair] = new_id
```

**Output**

```text
merges = {
    (101, 119): 256,  # "ew" -> 256
    (108, 111): 257,  # "lo" -> 257
    (257, 119): 258,  # "low" -> 258
    (101, 115): 259,  # "es" -> 259
    (256, 259): 260,  # "ewes" -> 260
}

tokens = [258, 32, 258, 32, 258, 101, 114, 32, 110, 260, 116, 32, 110, 260, 116]
```

### Critical Engineering Decisions When Building a Tokenizer

- **Training Data Mix Matters.** If you train BPE exclusively on English prose, Python indentation (4 spaces) and Hindi or Marathi UTF-8 sequences will rarely merge, forcing the LLM to burn 3x–4x more tokens on code and non-English prompts.
- **Regex Pre-Splitting Rules.** Without a regex that isolates digits into 1–3 character groups (used in GPT-4 and Llama 3), frequent numbers like 1999 or 2024 become single tokens while 2025 splits into 20 + 25, hurting math performance.
