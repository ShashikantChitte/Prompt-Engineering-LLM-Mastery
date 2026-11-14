# Chapter 3 - Part 1: What an LLM actually is (the idea, before the architecture)

> Chapter 3: What is an LLM? + Transformers and How They Work

A **Large Language Model (LLM)** is an advanced type of artificial intelligence designed to process, understand, and generate human-like text. Built on deep learning neural networks, LLMs are trained on massive datasets containing billions of words from books, articles, and websites. This scale allows them to capture the context, nuance, and patterns of human language rather than just matching simple keywords. LLMs are the underlying technology powering modern AI assistants like OpenAI ChatGPT, Google Gemini, and Anthropic Claude.

## How an LLM Works

Instead of thinking or understanding like a human, an LLM acts as a massive statistical prediction machine. It breaks down language using a multi-step workflow:

- **Tokenisation:** The input text is split into smaller units called tokens (words, syllables, or single characters).
- **Embeddings:** Tokens are converted into mathematical vectors that capture their meaning and relationship to other words.
- **Transformer Architecture:** The model processes these vectors using a specialized structure called a "transformer". Through a mechanism known as **self-attention**, it determines which words in a sentence are most relevant to each other, allowing it to capture long-range context.
- **Next-Token Prediction:** The model calculates the mathematical probability of every possible next word and selects the most appropriate one. It repeats this cycle word-by-word until a coherent response is formed.

## Key Capabilities and Use Cases

Because LLMs learn general language patterns during their massive training phase, they can adapt to a wide variety of tasks without needing separate programs for each one:

- **Content Generation:** Drafting essays, formal emails, stories, and creative copy.
- **Coding Assistance:** Writing, debugging, and explaining programming code across multiple languages.
- **Text Processing:** Summarizing extensive documents, analyzing user sentiment, and extracting data fields.
- **Language Translation:** Translating text fluidly across dozens of languages while preserving cultural context.

## Prominent LLM Families

LLMs are broadly divided into proprietary models managed via cloud APIs and open-weight models that developers can run locally.

- **GPT (OpenAI):** The foundational series behind ChatGPT, optimized for reasoning, complex instructions, and coding tasks.
- **Claude (Anthropic):** Known for its deep contextual window, long-form content writing, and analytical reasoning capabilities.
- **Gemini (Google DeepMind):** A natively multimodal architecture built to process text, audio, images, and video simultaneously.
- **Llama (Meta):** A leading open-weight model family widely used by developers and researchers for custom fine-tuning

## The idea, before the LLM architecture

Before the modern **Transformer architecture** took over in 2017, engineers and linguists spent decades trying to teach computers how to process language. The ultimate goal was always the same—to create a machine that could read, understand, and write like a human—but the methods used were radically different.

The evolution of the "idea" before LLMs can be broken down into three major eras.

### 1. The Rule-Based Era (1950s–1980s): Language as Math Logic

Early AI pioneers viewed human language as a complex set of strict code rules, much like algebra.

- **The Idea:** If we can just write down every single grammatical rule, dictionary definition, and syntax law by hand, the computer will understand language.
- **How it worked:** Systems like **ELIZA (1966)** used rigid pattern matching. If you said "I am sad," ELIZA looked for the pattern "I am [X]" and flipped it into a pre-written response: "Why are you [X]?"
- **Why it failed:** Human language is messy, highly ambiguous, and filled with idioms and slang. You cannot hardcode human context; the systems broke the moment someone spoke outside the pre-programmed template.

### 2. The Statistical Era (1990s–2010s): Counting and Guessing

As the early internet grew, researchers stopped trying to write rules and started using statistics to count word patterns.

- **The Idea:** A computer doesn't need to know why a word follows another; it just needs to know the probability that it will.
- **How it worked (N-Grams):** The AI looked at chunks of 2 or 3 words (bi-grams or tri-grams) to guess the next word. For example, if it read "The cat sat on the...", it would look at thousands of internet pages to see whether "mat", "floor", or "refrigerator" appeared most frequently next.
- **Why it failed:** They had no conceptual understanding. Worse, the vocabulary exploded. To track every possible combination of 4, 5, or 6 words, the database grew too massive for computers to compute, limiting the model's memory to just 2 or 3 words at a time.

### 3. The Early Neural Era (2013–2016): Meaning as a Direction

With the rise of deep learning, AI researchers realized words could be turned into math equations using neural networks. This era introduced the immediate predecessors to LLMs.

- **Word Embeddings (Word2Vec):** Developed by Google in 2013, this technique mapped words into a multi-dimensional grid where words with similar meanings clustered together. It famously proved that the model understood concepts algebraically: King - Man + Woman = Queen.
- **Recurrent Neural Networks (RNNs) & LSTMs:** To read text, AI used architectures that read sentences one word at a time, left to right, like a human. A loop mechanism carried a "memory" of previous words forward to help process the next one.

## The Massive Bottleneck That Led to LLMs

While RNNs and LSTMs were a massive leap forward, they hit a hard technical ceiling that prevented them from scaling into the "Large" Language Models we have today:

| Old Architecture Limitation | What It Blocked | How the Transformer Fixed It (2017) |
| --- | --- | --- |
| Sequential Processing (One word at a time) | Could not use modern GPUs efficiently. Training on the whole internet would take centuries. | **Parallel Processing:** Reads the entire sentence or document all at once, speeding up training exponentially. |
| Forgetting Context (Vanishing Gradient) | By the time the AI reached the end of a long paragraph, it completely forgot how the sentence started. | **Self-Attention:** Tracks the mathematical relationships between all words simultaneously, no matter how far apart. |

In short, the *ambition* to build an LLM existed for decades, but the AI field was stuck in a traffic jam—reading text word-by-word. The 2017 Transformer architecture didn't change the underlying goal; it simply built the multi-lane highway that allowed AI to ingest the whole internet at once.
