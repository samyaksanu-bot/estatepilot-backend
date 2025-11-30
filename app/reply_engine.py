import os
from typing import Optional
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a calm, polite real estate advisor.

Rules:
- Talk like a real human, not a bot.
- NEVER repeat the same sentence.
- Do not oversell.
- Ask soft follow-up questions.
- If user says stop / no / ok repeatedly — go silent.
- If site visit is confirmed, stop selling.
"""

def load_project_knowledge() -> str:
    try:
        with open("app/knowledge/project.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def should_be_silent(text: str) -> bool:
    stop_words = {"ok", "okay", "cool", "fine", "thanks", "thank you", "no"}
    return text.strip().lower() in stop_words

def generate_reply(user_text: str, state: dict) -> Optional[str]:
    if state.get("handoff_done"):
        return None

    if should_be_silent(user_text):
        return None

    knowledge = load_project_knowledge()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Project Info:\n{knowledge}"},
    ]

    if state.get("summary"):
        messages.append({"role": "system", "content": state["summary"]})

    messages.append({"role": "user", "content": user_text})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5
    )

    reply = completion.choices[0].message.content.strip()

    if "site visit" in reply.lower():
        state["handoff_done"] = True

    state["summary"] = (state.get("summary", "") +
                        f"\nUser: {user_text}\nAdvisor: {reply}")

    return reply

