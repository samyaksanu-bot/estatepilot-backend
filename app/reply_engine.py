import os
from typing import Optional
from openai import OpenAI

# ✅ OpenAI client (new SDK compatible)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ System behavior – human, non-pushy
SYSTEM_PROMPT = """
You are a professional real estate advisor chatting on WhatsApp.

Rules:
- Speak naturally like a human.
- Never repeat the same sentence twice.
- Do NOT sound salesy or robotic.
- If user says ok / fine / no → stay silent.
- Ask soft follow-ups, not forced ones.
- Once site visit is agreed → stop pitching.
"""

# ✅ Load project-specific knowledge
def load_project_knowledge() -> str:
    try:
        with open("app/knowledge/project.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

# ✅ Silence detection
def should_be_silent(text: str) -> bool:
    stop_words = {
        "ok", "okay", "cool", "fine", "thanks", "thank you",
        "no", "stop", "leave it", "later"
    }
    return text.strip().lower() in stop_words

# ✅ Main reply generator
def generate_reply(user_text: str, state: dict) -> Optional[str]:
    # Hard stop after handoff
    if state.get("handoff_done"):
        return None

    if should_be_silent(user_text):
        return None

    knowledge = load_project_knowledge()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Project Information:\n{knowledge}"}
    ]

    # Maintain conversation memory (short)
    if state.get("summary"):
        messages.append({
            "role": "system",
            "content": f"Conversation so far:\n{state['summary']}"
        })

    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.6
    )

    reply = response.choices[0].message.content.strip()

    # Detect visit handoff
    if "visit" in reply.lower() or "advisor" in reply.lower():
        state["handoff_done"] = True

    # Save rolling memory (compact)
    state["summary"] = (
        state.get("summary", "") +
        f"\nUser: {user_text}\nAdvisor: {reply}"
    )[-2000:]

    return reply
