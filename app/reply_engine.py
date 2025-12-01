import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """You are a polite, calm real-estate assistant.
Sound human. Never be salesy.
Ask only one question at a time.
If user wants a site visit, politely suggest a human agent call.
"""

def generate_reply(user_id: str, user_message: str) -> str:
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.4,
            },
            timeout=15,
        )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("❌ LLM error:", e)
        return "Got it. Let me check that for you."
