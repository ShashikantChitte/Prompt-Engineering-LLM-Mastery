# Chapter 4 - Part 4: Why the same word costs different tokens in different contexts

> Chapter 4: Tokenization and Token Management

The same word costs a different number of tokens across different contexts because modern subword tokenizers (like Byte-Pair Encoding) encode raw character sequences—including leading spaces, capitalization, and adjacent punctuation—rather than semantic words. Whenever the surrounding characters change, the tokenizer slices the string differently and maps it to completely different integer IDs.

## 1. Leading Spaces Change Everything

In BPE tokenizers (used by GPT-4, Llama 3, and Mistral), spaces are attached directly to the front of the word that follows them rather than treated as separate tokens.

- **Mid-sentence vs. Start of sentence.** When "apple" appears mid-sentence as " apple" (with a leading space), it matches a single frequent token ID. When "Apple" or "apple" appears at the very start of a prompt or right after a newline ("\napple"), there is no leading space, forcing the tokenizer to use a different ID or split it into multiple subwords ("ap" + "ple").
- **Double spaces.** Adding an accidental extra space (" apple") detaches the space from the word, turning one token into two (" " + " apple").

### 2. Capitalization Shifts Vocabulary Coverage

Because modern generative LLMs preserve exact casing, "hello", "Hello", and "HELLO" are three completely unrelated strings to the tokenizer.

- **Lowercase efficiency.** Lowercase words appear most frequently in training data and almost always earn a single token (" token" = 1 token).
- **Title case and ALL CAPS.** Title-cased words (" Token") often still get 1 token, while all-caps words (" TOKEN" or " BELIEVABLE") appear less often in training corpora and frequently shatter into multiple subword pieces (" TO" + "KEN" or " BEL" + "IEV" + "ABLE").

### 3. Punctuation and Symbols Alter Pre-Tokenization Boundaries

Before applying BPE merges, tokenizers run regex splitting rules to separate letters, numbers, and symbols. Surrounding characters dictate where those cuts happen.

- **Attached symbols or code syntax.** Writing "user" takes 1 token, whereas "user_id" or "userId" triggers camelCase/underscore splits ("user" + "_id" or "user" + "Id").
- **Contractions and quotes.** A word inside quotes or parentheses—such as "(apple)" vs "apple"—changes how pre-tokenization groups the boundary characters, occasionally splitting rare words differently when prefixes or suffixes attach.

### 4. Numbers Split Depending on Neighboring Digits

Modern tokenizers (such as GPT-4's cl100k_base and Llama 3) use a regex rule that chunks numbers into groups of **1 to 3 digits** from left to right.

- **Context-dependent grouping.** The number "25" on its own is **1 token**. Inside "2025", it groups as "202" + "5" (or "20" + "25"), so "25" shares a token with "20". Inside "1250", it splits as "125" + "0", completely breaking "25" across two separate tokens.

## Quick Summary: Same Word, Different Token Costs

| Text String | Typical Token Split (GPT-4 / Llama 3 style) | Token Count | Why It Changed |
| --- | --- | --- | --- |
| " apple" | [" apple"] | **1 token** | Most common mid-sentence form; single vocabulary entry. |
| "apple" | ["apple"] | **1 token** (different ID) | No leading space (start of prompt or after punctuation). |
| " APPLE" | [" AP", "PLE"] | **2 tokens** | All-caps form is rarer in training data, forcing a subword split. |
| "apple-pie" | ["apple", "-", "pie"] | **3 tokens** | Hyphen triggers a pre-tokenization boundary split. |

## Why This Matters in Practice

- **Prompt Engineering & API Costs.** Trailing spaces at the end of a prompt ("Translate this: ") force the model's next generated word to lose its expected leading space, hurting both token efficiency and output quality.
- **Multilingual & Code Workloads.** A word or variable embedded inside dense code syntax or mixed-script text (such as Hinglish or Marathi mixed with English punctuation) loses its standard spacing cues, causing token counts—and inference latency—to spike unexpectedly.
