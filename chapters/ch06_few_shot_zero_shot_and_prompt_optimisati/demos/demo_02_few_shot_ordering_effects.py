"""
Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)
Demo 2 - Few-Shot Ordering Effects

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_02_few_shot_ordering_effects.py
"""
# Same three examples, two different orderings. The last example acts as the strongest prior
# on output format.

# Sentiment classification with few-shot
# Three examples: positive, negative, neutral
# We test two orderings and see how the output changes

query = "The product works but I expected more for the price."

# Ordering A: neutral last
examples_neutral_last = """
Review: "This laptop is the best I've ever owned."
Sentiment: positive

Review: "Completely broke after one week. Waste of money."
Sentiment: negative

Review: "It's okay. Does what it says on the box."
Sentiment: neutral
"""

# Ordering B: negative last
examples_negative_last = """
Review: "This laptop is the best I've ever owned."
Sentiment: positive

Review: "It's okay. Does what it says on the box."
Sentiment: neutral

Review: "Completely broke after one week. Waste of money."
Sentiment: negative
"""

for ordering_name, examples in [("Neutral Last", examples_neutral_last), ("Negative Last", examples_negative_last)]:
    prompt = f"{examples}\nReview: \"{query}\"\nSentiment:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    result = response.choices[0].message.content.strip()
    print(f"Ordering: {ordering_name} -> Predicted: {result}")

# ---------------- Expected output ----------------
# Ordering: Neutral Last -> Predicted: neutral
# Ordering: Negative Last -> Predicted: negative
