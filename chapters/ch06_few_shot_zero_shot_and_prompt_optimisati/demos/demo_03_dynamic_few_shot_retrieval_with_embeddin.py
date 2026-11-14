"""
Chapter 6: Few-Shot, Zero-Shot and Prompt Optimisation (Advanced)
Demo 3 - Dynamic Few-Shot Retrieval with Embeddings

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_03_dynamic_few_shot_retrieval_with_embeddin.py
"""
# A small example library. For each incoming query, retrieve the top-2 most similar examples
# by cosine similarity, then use them as the few-shot context.

# Note: This demo uses embeddings covered in Module 3 (Class 22). Run to see output; full understanding comes after that class.

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Example library: input-output pairs
example_library = [
    {"input": "My payment failed but I was still charged.", "output": "billing"},
    {"input": "I cannot log into my account.", "output": "technical"},
    {"input": "Where can I find my invoice?", "output": "billing"},
    {"input": "The app crashes when I open it.", "output": "technical"},
    {"input": "How do I cancel my subscription?", "output": "billing"},
    {"input": "I want to speak to a human agent.", "output": "general"},
    {"input": "My password reset email never arrived.", "output": "technical"},
    {"input": "Do you offer student discounts?", "output": "general"},
]

def get_embeddings(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return np.array([e.embedding for e in response.data])

# Embed all examples once (offline indexing step)
example_inputs = [e["input"] for e in example_library]
example_embeddings = get_embeddings(example_inputs)
print(f"Indexed {len(example_library)} examples.")

def retrieve_examples(query, k=2):
    query_embedding = get_embeddings([query])
    similarities = cosine_similarity(query_embedding, example_embeddings)[0]
    top_k_indices = np.argsort(similarities)[::-1][:k]
    return [example_library[i] for i in top_k_indices], similarities[top_k_indices]

def classify_with_dynamic_few_shot(query):
    retrieved, scores = retrieve_examples(query, k=2)

    # Build few-shot prompt from retrieved examples
    few_shot_text = ""
    for ex in retrieved:
        few_shot_text += f'Message: "{ex["input"]}"\nIntent: {ex["output"]}\n\n'

    prompt = few_shot_text + f'Message: "{query}"\nIntent:'

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    prediction = response.choices[0].message.content.strip()

    print(f"Query: {query}")
    print(f"Retrieved examples:")
    for ex, score in zip(retrieved, scores):
        print(f"  [{score:.3f}] {ex['input']} -> {ex['output']}")
    print(f"Prediction: {prediction}")
    print()

# Test with different query types
classify_with_dynamic_few_shot("The billing page shows an error.")
classify_with_dynamic_few_shot("What are your office hours?")

# ---------------- Expected output ----------------
# Indexed 8 examples.
#
# Query: The billing page shows an error.
# Retrieved examples:
#   [0.62] My payment failed but I was still charged. -> billing
#   [0.51] I cannot log into my account. -> technical
# Prediction: billing
#
# Query: What are your office hours?
# Retrieved examples:
#   [0.44] Do you offer student discounts? -> general
#   [0.41] I want to speak to a human agent. -> general
# Prediction: general
