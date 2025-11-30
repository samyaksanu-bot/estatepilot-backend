import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a calm, polite, non-pushy real estate advisor.

Rules:
- You talk like a human advisor, not a bot.
- Never repeat the same sentence.
- Never oversell.
- Ask natural follow-up questions.
- If the user shows irritation, reduce replies.
- If the user agrees for a site visit, stop selling.
- After handoff, only reply if user asks.
- If user says "stop", acknowledge once and go silent.

Goal:
Understand the user's intent, give helpful information,
and gently move toward a site visit only when appropriate.
"""

def load_project_knowledge():
    try:
        with open("app/knowledge/project.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def should_be_silent(text: str) -> bool:
    stop_words = ["ok", "okay", "cool", "fine", "thanks", "thank you", "no"]
    return text.strip().lower() in stop_words

def generate_reply(user_text: str, state: dict) -> str | None:
    if state["handoff_done"]:
        return None

    if should_be_silent(user_text):
        return None

    project_knowledge = load_project_knowledge()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Project information:\n{project_knowledge}"},
    ]

    if state["summary"]:
        messages.append({
            "role": "system",
            "content": f"Conversation so far:\n{state['summary']}"
        })

    messages.append({"role": "user", "content": user_text})

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5
    )

    reply = response.choices[0].message.content.strip()

    if "site visit" in reply.lower():
        state["handoff_done"] = True

    # update conversation memory
    state["summary"] += f"\nUser: {user_text}\nAdvisor: {reply}"

    return reply
