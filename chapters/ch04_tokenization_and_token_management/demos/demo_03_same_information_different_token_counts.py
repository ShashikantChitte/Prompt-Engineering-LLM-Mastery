"""
Chapter 4: Tokenization and Token Management
Demo 3 - Same Information, Different Token Counts (Non-English Cost)

Auto-generated from the course document. Run: python demo_03_same_information_different_token_counts.py
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# The same sentence in four languages
sentences = {
    "English":  "Artificial intelligence is transforming the world.",
    "Spanish":  "La inteligencia artificial está transformando el mundo.",
    "Hindi":    "कृत्रिम बुद्धिमत्ता दुनिया को बदल रही है।",
    "Arabic":   "الذكاء الاصطناعي يحول العالم.",
}

print(f"{'Language':<10}  {'Tokens':>7}  {'Characters':>12}  {'Tokens/Char':>12}")
print("-" * 48)
for lang, text in sentences.items():
    tokens = enc.encode(text)
    print(f"{lang:<10}  {len(tokens):>7}  {len(text):>12}  {len(tokens)/len(text):>12.2f}")

# ---------------- Expected output ----------------
# Language     Tokens    Characters   Tokens/Char
# ------------------------------------------------
# English           8            50          0.16
# Spanish          10            55          0.18
# Hindi            43            41          1.05
# Arabic           20            29          0.69

# Hindi and Arabic cost significantly more tokens than English for the same information. The
# tokenizer was trained on a corpus that was heavily English. Non-Latin scripts get fragmented
# into many small pieces. If you are building a multilingual product, factor this into your
# cost estimates - you may pay 3-4x more per message in some languages.
