import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a polite, calm real-estate assistant.
• Sound human, not salesy
• Ask ONE question at a time
• If user shows interest in visit, politely suggest a human agent call
• Never force a site visit
"""

def generate_reply(user_id: str, user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM error:", e)
        return "Got it. Let me check that for you."
