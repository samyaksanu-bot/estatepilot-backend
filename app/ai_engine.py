# app/ai_engine.py

import os
from openai import OpenAI
from app.state import get_state, append_history, mark_handoff

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def _detect_language(text: str) -> str:
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
    state = get_state(phone)
    project = state.get("project_context")
    history = state.get("conversation_history", [])

    text_l = user_text.lower()

    # ==========================================================
    # VISIT RECOGNITION (BUT NOT IMMEDIATE HANDOFF)
    # ==========================================================

    positive_visit_words = [
        "visit", "site visit", "see property", "want to visit",
        "schedule visit", "arrange visit", "book visit",
        "show me property", "property visit"
    ]

    # If user expresses visit interest AFTER already exploring details,
    # AND NOT confused, AND NOT hesitant → CONFIRM then handoff
    if (
        any(w in text_l for w in positive_visit_words)
        and state.get("ai_mode") is True
        and state.get("stop_questions") is False
        and ("not" not in text_l and "later" not in text_l and "after clarity" not in text_l)
    ):
        # AI now confirms one more time softly
        reply = (
            "Great — a short site visit really gives clarity with no obligation.\n"
            "If you like, I can arrange a call with our project expert to plan a visit.\n"
            "Share a preferred time."
        )

        # Mark qualified ONLY AFTER USER CONFIRMS NEXT MESSAGE
        state["visit_pending_confirmation"] = True

        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # HARD CONFIRMATION for handoff (OPTION B)
    # ==========================================================
    if state.get("visit_pending_confirmation") is True and any(
        p in text_l for p in ["yes", "ok", "sure", "call", "confirm", "let's do", "tomorrow", "morning", "evening"]
    ):
        state["qualified"] = True
        state["stop_questions"] = True
        state["ai_mode"] = False
        state["visit_pending_confirmation"] = False
        mark_handoff(phone)

        reply = (
            "Perfect — I will arrange a call with our expert to finalize availability and visit planning.\n"
            "They will contact you shortly."
        )

        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # SAFETY FILTER: Personal Queries
    # ==========================================================
    personal = [
        "who are you", "real name", "login", "password",
        "email", "phone number", "personal details",
        "openai account"
    ]
    if any(w in text_l for w in personal):
        reply = (
            "I am Pragiti, your real estate assistant. I only assist with this project information, "
            "pricing, availability and visit planning."
        )
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # Project MUST EXIST
    # ==========================================================
    if not project:
        reply = "Tell me which project you are exploring and I will guide you."
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # LANGUAGE DETECTION
    # ==========================================================
    lang = _detect_language(user_text)
    state["language"] = lang

    lang_hint = {
        "english": "Reply in natural English.",
        "hindi": "Reply in comfortable conversational Hindi.",
        "hinglish": "Reply in natural Hinglish like WhatsApp chat."
    }.get(lang, "Reply in natural English.")

    # ==========================================================
    # STOP MODE (ONLY after full qualification)
    # ==========================================================
    if state.get("stop_questions") is True:
        system_prompt = f"""
You are Pragiti, a real estate assistant.

STOP asking qualification questions.
Only support with details or information.

Be short, polite and factual.
No persuasion.
If user asks for call/visit, confirm politely.

Real-estate only.
{lang_hint}
"""
        msgs = [{"role": "system", "content": system_prompt}]
        for h in history[-6:]:
            msgs.append({"role": "assistant" if h["from"] == "bot" else "user", "content": h["text"]})
        msgs.append({"role": "user", "content": user_text})

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=0.4,
            max_tokens=90,
        )
        reply = res.choices[0].message.content.strip()
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # NORMAL AI MODE (BEST)
    # ==========================================================
    system_prompt = f"""
You are PRAGITI, a professional real estate advisor.

PROJECT:
- Name: {project.get("name")}
- Location: {project.get("location")}
- Price: {project.get("price_range")}
- Units: {project.get("unit_types")}
- Status: {project.get("status")}
- Amenities: {project.get("usp")}

RULES:
1) {lang_hint}
2) Keep responses short (2–4 sentences)
3) Softly increase clarity but never interrogate
4) Accept hesitation, avoid pressure
5) If user is confused, calm them and clarify
6) Never hallucinate — unknown → say “advisor will confirm”
7) If user becomes serious, you may ASK LIGHT QUESTIONS ONLY IF NATURAL
8) If user avoids → accept and move on
9) When clarity increases → again suggest visit softly

INTERNAL:
NEVER mention scoring, qualification or rank.
"""

    msgs = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:
        msgs.append({"role": "assistant" if h["from"] == "bot" else "user", "content": h["text"]})
    msgs.append({"role": "user", "content": user_text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=0.55,
        max_tokens=140,
    )
    reply = res.choices[0].message.content.strip()
    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)
    return reply
