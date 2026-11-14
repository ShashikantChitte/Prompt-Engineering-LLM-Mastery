"""
Chapter 4: Tokenization and Token Management
Demo 2 - Basic Tokenization: Seeing the Integer Sequence

Auto-generated from the course document. Run: python demo_02_basic_tokenization_seeing_the_integer_se.py
"""
import tiktoken

# cl100k_base is the tokenizer used by GPT-4 and GPT-3.5-turbo
enc = tiktoken.get_encoding("cl100k_base")

text = "Tokenization splits text into pieces a model can process."
tokens = enc.encode(text)

print("Text:", text)
print("Token IDs:", tokens)
print("Token count:", len(tokens))
print()

# Decode each token individually to see the pieces
for token_id in tokens:
    piece = enc.decode([token_id])
    print(f"  {token_id:6d}  ->  {repr(piece)}")

# ---------------- Expected output ----------------
# Text: Tokenization splits text into pieces a model can process.
# Token IDs: [3404, 2065, 41567, 1495, 1139, 9863, 264, 1646, 649, 1920, 13]
# Token count: 11
#
#     3404  ->  'Token'
#     2065  ->  'ization'
#    41567  ->  ' splits'
#     1495  ->  ' text'
#     1139  ->  ' into'
#     9863  ->  ' pieces'
#      264  ->  ' a'
#     1646  ->  ' model'
#      649  ->  ' can'
#     1920  ->  ' process'
#       13  ->  '.'

# Look at the integer sequence - that is exactly what the model receives. Notice how most
# common English words are a single token. The space before a word is often included in that
# word's token - " splits" is one token, not " " + "splits".
