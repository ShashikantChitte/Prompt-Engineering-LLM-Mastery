"""
Chapter 4: Tokenization and Token Management
Demo 8 - Prompt Compression: Measuring Token Reduction

Auto-generated from the course document. Run: python demo_08_prompt_compression_measuring_token_reduc.py
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def token_count(text: str) -> int:
    return len(enc.encode(text))

def compression_stats(original: str, compressed: str, label: str) -> None:
    orig_tokens = token_count(original)
    comp_tokens = token_count(compressed)
    reduction = (1 - comp_tokens / orig_tokens) * 100
    print(f"{label}")
    print(f"  Original:   {orig_tokens:>5} tokens")
    print(f"  Compressed: {comp_tokens:>5} tokens")
    print(f"  Reduction:  {reduction:>5.1f}%")
    print()

# Example 1: Verbose vs direct instruction
original_1 = """I would really appreciate it if you could please help me by taking a look at the following text and then providing me with a clear, concise, and well-structured summary that captures all of the main points and key ideas. Please make sure your summary is easy to understand."""

compressed_1 = "Summarize the following text. Capture the main points."

compression_stats(original_1, compressed_1, "Example 1: Verbose instruction")

# Example 2: Over-specified format vs minimal format
original_2 = """Please respond in the following format: First, provide a numbered list of all key points you identify. Second, after the numbered list, write a paragraph that summarizes the overall theme. Third, end with a one-sentence conclusion. Make sure each numbered item is on its own line."""

compressed_2 = "Format: numbered key points, then a summary paragraph, then one-sentence conclusion."

compression_stats(original_2, compressed_2, "Example 2: Over-specified format")

# Example 3: Hedged context vs direct context
original_3 = """I'm not sure if this is the right way to phrase this, but I was wondering if you might be able to assist me with something. I have a Python function that I wrote and I think there might be some issues with it, though I could be wrong. If you have time, could you take a look at it and let me know if you see any bugs or ways it could be improved?"""

compressed_3 = "Review this Python function for bugs and improvements:"

compression_stats(original_3, compressed_3, "Example 3: Hedged request")

# ---------------- Expected output ----------------
# Example 1: Verbose instruction
#   Original:      55 tokens
#   Compressed:    12 tokens
#   Reduction:   78.2%
#
# Example 2: Over-specified format
#   Original:      57 tokens
#   Compressed:    17 tokens
#   Reduction:   70.2%
#
# Example 3: Hedged request
#   Original:      82 tokens
#   Compressed:     9 tokens
#   Reduction:   89.0%

# The compressed versions are shorter AND clearer. The reduction is 60-75% in each case with
# no information lost. Hedging, politeness softeners, and redundant format specifications are
# the main sources of excess tokens in most prompts.
