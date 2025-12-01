import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a polite, professional WhatsApp business assistant.
Reply briefly, clearly, and helpfully.
Avoid emojis unless friendly.
If something is unclear, ask a short follow-up question.
"""

def generate_reply(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=120,
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ LLM error:", str(e))
        return "Thanks for your message. I’ll get back to you shortly."
