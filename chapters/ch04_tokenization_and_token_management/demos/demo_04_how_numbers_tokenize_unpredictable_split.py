"""
Chapter 4: Tokenization and Token Management
Demo 4 - How Numbers Tokenize (Unpredictable Splits)

Auto-generated from the course document. Run: python demo_04_how_numbers_tokenize_unpredictable_split.py
"""
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

numbers = ["1", "10", "100", "1000", "10000", "100000",
           "2023", "2024", "3.14159", "0.001", "1,000,000"]

print(f"{'Number':<15}  {'Tokens':>7}  {'Split'}")
print("-" * 50)
for n in numbers:
    token_ids = enc.encode(n)
    pieces = [repr(enc.decode([t])) for t in token_ids]
    print(f"{n:<15}  {len(token_ids):>7}  {' + '.join(pieces)}")

# ---------------- Expected output ----------------
#
# Number            Tokens  Split
# --------------------------------------------------
# 1                      1  '1'
# 10                     1  '10'
# 100                    1  '100'
# 1000                   2  '100' + '0'
# 10000                  2  '100' + '00'
# 100000                 2  '100' + '000'
# 2023                   2  '202' + '3'
# 2024                   2  '202' + '4'
# 3.14159                4  '3' + '.' + '141' + '59'
# 0.001                  3  '0' + '.' + '001'
# 1,000,000              5  '1' + ',' + '000' + ',' + '000'

# Number tokenization is inconsistent - "1000" and "10000" split at different boundaries. This
# is why LLMs perform poorly at arithmetic: the model does not see a number, it sees a
# sequence of subword pieces that happen to look like digits. The model has never learned
# positional arithmetic on integers.
