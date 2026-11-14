"""
Chapter 5: Prompt Design Patterns and Frameworks
Demo 3 - Persona and Tone via System Prompt

Auto-generated from the course document. Run: python demo_03_persona_and_tone_via_system_prompt.py
"""
import openai
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

user_message = "My order hasn't arrived and it was supposed to be here yesterday."

personas = [
    {
        "label": "No Persona (default)",
        "system": None
    },
    {
        "label": "Formal Corporate Support",
        "system": "You are a customer support representative for a logistics company. Respond formally. Acknowledge the issue, explain possible causes, and offer to escalate. Keep responses under 80 words."
    },
    {
        "label": "Friendly Direct Support (Maya)",
        "system": "You are Maya, a support specialist at Bloom Florists. You are warm, direct, and solution-focused. Always ask for the order number immediately. Never say 'may be delayed' without giving a specific next step. Keep responses under 60 words."
    }
]

for persona in personas:
    messages = []
    if persona["system"]:
        messages.append({"role": "system", "content": persona["system"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=120
    )
    print(f"\n--- {persona['label']} ---")
    print(response.choices[0].message.content)

# ---------------- Expected output ----------------
# --- No Persona (default) ---
# I'm sorry to hear your order hasn't arrived yet. There are a few possible
# reasons for a delay — weather, carrier backlogs, or an issue at a sorting
# facility. I'd recommend checking the tracking link in your confirmation
# email for the latest status. If it hasn't updated in 24 hours, or if you'd
# like us to open a case with the carrier, just let me know your order number
# and I'll take it from there.
#
# --- Formal Corporate Support ---
# We sincerely apologize for the delay with your order. Delays of this nature
# are typically caused by carrier processing times, weather conditions, or
# temporary sorting-facility backlogs. To resolve this promptly, we would be
# glad to escalate the matter to our carrier liaison team. Please provide your
# order number so we may initiate the escalation on your behalf.
#
# --- Friendly Direct Support (Maya) ---
# Hey! So sorry your blooms haven't arrived yet — that's not the experience we
# want. Can you send me your order number? I'll pull up the tracking right now
# and give you a concrete next step within the hour.
