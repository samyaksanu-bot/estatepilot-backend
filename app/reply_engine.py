# app/reply_engine.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a calm, professional real estate advisor.
Only answer questions related to this property.
Do not repeat questions.
Do not over-message.
If the user shows interest in site visit, politely stop and hand over to a human.
"""

def generate_reply(text, state):
    print("🧠 reply_engine invoked")
    print("🔤 Incoming text:", text)

    # HARD STOP conditions
    if state.get("do_not_disturb"):
        return None

    if any(x in text for x in ["stop", "don't message", "no thanks"]):
        state["do_not_disturb"] = True
        return "Sure 👍 I’ll stop here. Reach out anytime if needed."

    # Visit intent
    if any(x in text for x in ["visit", "site", "come", "see"]):
        state["visit_interest"] = True
        state["handoff_done"] = True
        return (
            "Perfect 👍\n"
            "I’ll have our local advisor call you to confirm a suitable date and time.\n"
            "They’ll take it forward from here."
        )

    # Limit AI spam
    if state["messages_count"] > 6:
        return (
            "I don’t want to overwhelm you 🙂\n"
            "Let me know if you’d like a site visit or a quick call from our advisor."
        )

    # LLM call (ONLY when safe)
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            max_tokens=120
        )
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return "I got that. Could you rephrase it once for me?"

