# app/ai_engine.py

import os
from openai import OpenAI
from app.state import get_state, append_history, mark_handoff

# Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def _detect_language(text: str) -> str:
    """
    Very lightweight heuristic:
    - returns "hindi", "hinglish", or "english"
    """
    hindi_words = [
        "kya", "kab", "kaise", "ghar", "zameen", "flat",
        "booking", "visit", "kal", "aaj", "weekend",
        "paisa", "loan", "possession", "dekho", "dekhna",
        "side", "wali", "area", "ke", "ki"
    ]
    t = text.lower()
    hits = sum(1 for w in hindi_words if w in t)

    if hits >= 4:
        return "hindi"
    if 2 <= hits < 4:
        return "hinglish"
    return "english"


def call_ai(phone: str, user_text: str) -> str:
    """
    AI conversation handler for WhatsApp.
    - GPT-4o-mini
    - Project-aware
    - Language-aware
    - Persuasive but short
    - Real estate ONLY
    - Emotion-aware and non-pushy
    """

    state = get_state(phone)
    project = state.get("project_context")
    history = state.get("conversation_history", [])

    text_l = user_text.lower()

    # =====================================
    # 1) SITE VISIT TRIGGER DURING AI MODE
    # =====================================
    visit_triggers = [
        "visit", "site visit", "see property", "property visit",
        "come and see", "want to see", "want to visit", "schedule visit",
        "plan a visit", "plan site", "book visit", "arrange visit",
        "meet at site", "location visit", "show me the property",
        "call me", "i want call", "talk to executive", "talk to agent"
    ]

    if any(v in text_l for v in visit_triggers):
        state["qualified"] = True
        state["stop_questions"] = True
        state["ai_mode"] = False

        mark_handoff(phone)

        reply = (
            "Great — I’ll arrange a call with our project expert who will guide you with "
            "availability, exact location and site visit planning.\n"
            "Please share your preferred time."
        )

        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # =====================================
    # 2) SAFETY FILTER: PERSONAL / INTERNAL
    # =====================================
    if any(w in text_l for w in [
        "who are you",
        "real name",
        "where do you live",
        "who made you",
        "your email",
        "your phone number",
        "personal details",
        "login details",
        "password",
        "openai account",
        "account details"
    ]):
        reply = (
            "I am Pragiti, your real estate assistant. I help only with this project’s "
            "information, pricing, availability and site visits. I don’t share personal or internal data."
        )
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # =====================================
    # 3) MISSING PROJECT CONTEXT SAFETY
    # =====================================
    if not project:
        reply = (
            "Tell me which project you’re exploring, and I’ll guide you with pricing, availability and visit planning."
        )
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # =====================================
    # 4) LANGUAGE DETECTION + STORE
    # =====================================
    lang = _detect_language(user_text)
    state["language"] = lang

    lang_hint = {
        "english": "Reply in natural English.",
        "hindi": "Reply purely in comfortable conversational Hindi.",
        "hinglish": "Reply in natural Hinglish (mix of Hindi and English) like people chat on WhatsApp."
    }.get(lang, "Reply in natural English.")

    # =====================================
    # 5) STOP MODE: NO MORE QUALIFICATION
    # =====================================
    if state.get("stop_questions") is True:
        # Support-only mode: no more probing, no persuasion
        system_prompt = f"""
You are Pragiti, a real estate assistant.

User has either:
- already been qualified, OR
- requested a call/visit, OR
- shown irritation, OR
- avoided qualification questions.

RULE:
Stop ALL qualification or probing questions.

Your replies must:
- answer only what the user asks
- be short, friendly and factual
- no nudging, no persuasion
- no new qualification questions
- assist only with information, availability or support
- if user asks for call/visit, politely confirm and say our expert will call.

Real-estate only. Ignore unrelated topics.
{lang_hint}
"""

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-6:]:
            messages.append({
                "role": "assistant" if h["from"] == "bot" else "user",
                "content": h["text"]
            })
        messages.append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=100,
        )

        reply = response.choices[0].message.content.strip()
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # =====================================
    # 6) NORMAL AI MODE (WITH QUALIFICATION)
    # =====================================
    system_prompt = f"""
You are PRAGITI, a HUMAN-LIKE real estate sales assistant for EstatePilot.

PROJECT (FACT-ONLY):
- Name: {project.get("name")}
- Location: {project.get("location")}
- Price Range: {project.get("price_range")}
- Unit Types: {project.get("unit_types")}
- Status: {project.get("status")}
- Amenities / USP: {project.get("usp")}

STRICT RULES:
1) {lang_hint}
2) Answer in MAX 2–4 sentences.
   - First: clear factual answer.
   - Then: a soft, non-pushy suggestion (e.g., a short visit can give clarity with no obligation).
3) NO HALLUCINATION:
   If you are not sure, say:
   "Our advisor will confirm this on call."
   Do NOT invent builder history, distances, bank tie-ups or future developments.
4) REAL-ESTATE ONLY:
   If user asks about unrelated topics (tech, politics, jokes, personal life, hacking, etc.),
   reply briefly:
   "I assist only with this real estate project, its pricing, availability and site visits."
5) EMOTION + FRUSTRATION:
   If user sounds irritated, confused or hesitant:
       - Calm them
       - Do NOT repeat the same question
       - Reduce pressure
       - Suggest a simple next step (like: “you can just explore without any pressure to book”).
6) NATURAL QUALIFICATION (INTERNAL ONLY):
   Without sounding like interrogation:
       - If user talks budget, timing, purpose, family size, loan/cash → treat as qualification signals.
       - Ask light, natural questions only if user is already engaged.
       - If user dodges or avoids → accept and move on, do not push.
       - If user asks to talk to agent or visit → gently lean towards scheduling.
   NEVER mention scoring, qualification or rank.
7) SALES INTELLIGENCE:
   Every answer should:
       - increase clarity
       - build comfort and trust
       - softly move user towards site visit if appropriate
       - never feel like pressure or script.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add trimmed recent history for continuity
    for h in history[-6:]:
        messages.append({
            "role": "assistant" if h["from"] == "bot" else "user",
            "content": h["text"]
        })

    # latest user message
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.55,
        max_tokens=140,
    )

    reply = response.choices[0].message.content.strip()

    # store history
    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)

    return reply
