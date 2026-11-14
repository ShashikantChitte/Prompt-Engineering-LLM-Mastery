"""
Chapter 4: Tokenization and Token Management
Demo 7 - LostInTheMiddle: Position Matters

Auto-generated from the course document. Run: python demo_07_lostinthemiddle_position_matters.py
"""
# # This demo simulates the LostInTheMiddle problem without an API call.

# # We construct prompts that bury the answer in different positions,

# # then show the token cost and position of the relevant content.

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

filler = "This document contains general background information about software engineering practices, team structures, and project management methodologies. It covers topics from agile development to deployment pipelines. " * 10

fact = "The quarterly revenue target for Q3 2025 is $4.2 million."

question = "What is the Q3 2025 revenue target?"

def build_prompt(position: str) -> str:
    if position == "start":
        context = fact + "\n\n" + filler
    elif position == "middle":
        half = len(filler) // 2
        context = filler[:half] + fact + filler[half:]
    else:  # end
        context = filler + "\n\n" + fact
    return f"{context}\n\nQuestion: {question}"

for pos in ["start", "middle", "end"]:
    prompt = build_prompt(pos)
    tokens = enc.encode(prompt)
    total = len(tokens)

    # Find where the fact appears (in tokens)
    fact_tokens = enc.encode(fact)
    fact_str_pos = prompt.find(fact)
    char_fraction = fact_str_pos / len(prompt)

    print(f"Position: {pos.upper()}")
    print(f"  Total tokens:          {total:,}")
    print(f"  Fact location:         {char_fraction:.0%} into the prompt")
    print(f"  Estimated retrieval:   {'HIGH' if pos in ['start', 'end'] else 'DEGRADED (LostInTheMiddle risk)'}")
    print()

# ---------------- Expected output ----------------
# Position: START
#   Total tokens:          321
#   Fact location:         0% into the prompt
#   Estimated retrieval:   HIGH
#
# Position: MIDDLE
#   Total tokens:          320
#   Fact location:         48% into the prompt
#   Estimated retrieval:   DEGRADED (LostInTheMiddle risk)
#
# Position: END
#   Total tokens:          321
#   Fact location:         95% into the prompt
#   Estimated retrieval:   HIGH

# When the relevant fact is at 50% into the prompt, retrieval reliability drops - this is the
# LostInTheMiddle problem from Liu et al. 2023. For RAG pipelines: put the most relevant
# retrieved chunks at position 0 or at the very end of the context block. Never sort them
# randomly.
