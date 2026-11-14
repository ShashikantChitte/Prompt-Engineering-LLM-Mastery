"""
Chapter 9: System Prompt Architecture
Demo 4 - Multi-Turn: How Conversation History Accumulates

Note: this demo reuses names defined in earlier demos of this chapter: client.
Run the earlier demos first (or paste their setup here).

Auto-generated from the course document. Run: python demo_04_multi_turn_how_conversation_history_accu.py
"""
# Show how conversation history builds up and what the model actually receives on each turn
SYSTEM = """You are a meal planning assistant. Help users plan weekly meals.
Keep track of dietary restrictions the user mentions. Reference them in future responses."""
# Simulate a 3-turn conversation manually
conversation_history = []
turn_inputs = [
    "Hi! I'm vegetarian and I'm trying to eat high protein.",
    "What should I have for lunch on Monday?",
    "Can you suggest something for Tuesday dinner that uses lentils?"
]
print("MULTI-TURN CONVERSATION")
print("Showing token count growth at each turn")
print("=" * 60)
for turn_num, user_input in enumerate(turn_inputs, 1):
    # Add user message to history
    conversation_history.append({"role": "user", "content": user_input})
    # Token count of current context (rough estimate)
    total_chars = len(SYSTEM) + sum(len(m["content"]) for m in conversation_history)
    estimated_tokens = total_chars // 4  # rough 4 chars/token estimate
    # Make the API call with full history
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=150,
        system=SYSTEM,
        messages=conversation_history
    )
    assistant_reply = response.content[0].text
    # Add assistant reply to history for next turn
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    print(f"\nTurn {turn_num} | Estimated context: ~{estimated_tokens} tokens")
    print(f"User: {user_input}")
    print(f"Assistant: {assistant_reply[:200]}")
print("\n" + "=" * 60)
print(f"Messages in history: {len(conversation_history)}")
print(f"Turn 3 sent {len(conversation_history)} messages to the API (full history, every time)")

# ---------------- Expected output ----------------
# MULTI-TURN CONVERSATION
# Showing token count growth at each turn
# ============================================================
#
# Turn 1 | Estimated context: ~55 tokens
# User: Hi! I'm vegetarian and I'm trying to eat high protein.
# Assistant: Hi! Great to meet you — vegetarian and aiming for high protein is a very doable combo. To help me plan your week, a few quick questions: Do you eat eggs and dairy, or are you fully plant-based? Any foods you dislike or want to avoid? And roughly how many meals per day are you planning for?
#
# Turn 2 | Estimated context: ~175 tokens
# User: What should I have for lunch on Monday?
# Assistant: Given that you're vegetarian and focused on high protein, here's a solid Monday lunch idea: a **lentil and quinoa bowl** with roasted vegetables and a tahini dressing — roughly 20g of protein and very filling. Alternatives if you want variety: a chickpea-and-feta salad, or a tofu stir-fry with brown rice. Want me to suggest sides or prep steps?
#
# Turn 3 | Estimated context: ~330 tokens
# User: Can you suggest something for Tuesday dinner that uses lentils?
# Assistant: Absolutely — and nice that it builds on Monday's lentil bowl without repeating it. For Tuesday dinner, try a **high-protein lentil curry**: red lentils simmered with coconut milk, spinach, and spices, served over rice or with whole-grain flatbread. It's vegetarian, packs ~18–20g of protein per serving, and holds up well as leftovers. Want a quick recipe or a prep-ahead plan?
#
# ============================================================
# Messages in history: 6
# Turn 3 sent 6 messages to the API (full history, every time)
