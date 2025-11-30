import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def should_stay_silent(text: str) -> bool:
    silence_words = {
        "ok", "okay", "cool", "fine", "thanks",
        "thank you", "no", "stop", "leave it", "later"
    }
    return text.lower().strip() in silence_words


def load_project_knowledge() -> str:
    try:
        with open("app/knowledge/project.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def generate_reply(user_text: str, state: dict) -> str | None:
    # ✅ If handed off → bot must stop
    if state.get("handoff_done"):
        return None

    # ✅ Respect user silence
    if should_stay_silent(user_text):
        return None

    project_info = load_project_knowledge()

    system_prompt = f"""
You are a human real estate advisor chatting on WhatsApp.

Rules:
- Never sound robotic
- Never repeat messages
- Never oversell
- Ask gently
- If site visit confirmed → STOP messaging

Project details:
{project_info}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.6
    }

    try:
        response = requests.post(
            OPENAI_URL,
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()

        reply = response.json()["choices"][0]["message"]["content"].strip()

        # ✅ Detect handoff intent
        if any(x in reply.lower() for x in ["visit", "advisor", "call you"]):
            state["handoff_done"] = True

        return reply

    except Exception as e:
        print("❌ LLM error:", e)
        return "I’ll have our advisor assist you shortly."
