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
    # VISIT RECOGNITION
    # ==========================================================
    positive_visit_words = [
        "visit", "site visit", "see property", "want to visit",
        "schedule visit", "arrange visit", "book visit",
        "show me property", "property visit"
    ]

    if (
        any(w in text_l for w in positive_visit_words)
        and state.get("ai_mode") is True
        and state.get("stop_questions") is False
        and ("not" not in text_l and "later" not in text_l and "after clarity" not in text_l)
    ):
        reply = (
            "Great — a short site visit really gives clarity.\n"
            "If you like, I can arrange a call with our project expert.\n"
            "Share a preferred time."
        )
        state["visit_pending_confirmation"] = True
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # VISIT HANDOFF CONFIRMATION
    # ==========================================================
    if state.get("visit_pending_confirmation") is True and any(
        p in text_l for p in ["yes", "ok", "sure", "call", "confirm", "tomorrow", "morning", "evening"]
    ):
        state["qualified"] = True
        state["stop_questions"] = True
        state["ai_mode"] = False
        state["visit_pending_confirmation"] = False
        mark_handoff(phone)

        reply = (
            "Perfect — our expert will call you shortly to finalize availability and visit planning."
        )
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # SAFETY FILTER
    # ==========================================================
    personal = [
        "who are you", "real name", "login", "password",
        "email", "phone number", "personal details",
        "openai account"
    ]
    if any(w in text_l for w in personal):
        reply = (
            "I am Pragiti, your real estate assistant for this project. "
            "I help with verified information, availability and visit planning."
        )
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # PROJECT MUST EXIST
    # ==========================================================
    if not project:
        reply = "Tell me which project you are exploring and I will help."
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
        "hindi": "Reply in conversational Hindi.",
        "hinglish": "Reply in natural Hinglish."
    }.get(lang, "Reply in natural English.")

    # ==========================================================
    # STOP MODE AFTER QUALIFICATION
    # ==========================================================
    if state.get("stop_questions") is True:
        system_prompt = f"""
You are Pragiti, a real estate assistant.

STOP qualification questions.
Only support with answers or clarifications.

Be short, polite and factual.
Confirm politely if user asks for visits.

{lang_hint}
"""
        msgs = [{"role": "system", "content": system_prompt}]
        for h in history[-6:]:
            msgs.append({"role": "assistant" if h["from"] == "bot" else "user", "content": h["text"]})
        msgs.append({"role": "user", "content": user_text})

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs,
            temperature=0.35,
            max_tokens=70,
        )
        reply = res.choices[0].message.content.strip()
        append_history(phone, "user", user_text)
        append_history(phone, "bot", reply)
        return reply

    # ==========================================================
    # NORMAL MODE — EXCLUSIVITY / REDIRECTION / SHORT REPLIES
    # ==========================================================
    project_name = project.get("name") or "this project"
    project_location = project.get("location") or ""
    project_price = project.get("price_range") or ""
    project_units = project.get("unit_types") or ""
    project_status = project.get("status") or ""
    project_amenities = project.get("usp") or ""

    hesitation_words = [
        "just exploring", "time pass", "not sure", "thinking", "browsing"
    ]
    user_hesitant = any(w in text_l for w in hesitation_words)

    legality_words = [
        "rera", "legal", "approval", "approved", "registration",
        "noc", "title", "occupancy", "certificate"
    ]
    legality_trigger = any(w in text_l for w in legality_words)

    system_prompt = f"""
You are PRAGITI — a WhatsApp-style professional advisor for one builder/project only.

PROJECT CONTEXT:
- {project_name}, {project_location}, price {project_price}
- Units: {project_units}
- Status: {project_status}
- Amenities: {project_amenities}

COMMUNICATION RULES (MANDATORY):
- Replies must be 2–4 sentences max, WhatsApp style.
- Never send long paragraphs or lectures.
- Answer the user's question directly first.
- Speak warm, advisory, calm — not robotic.

PROJECT EXCLUSIVITY RULE:
- You only represent this builder’s verified projects.
- Never suggest or search competitors' properties.
- If users ask for another locality/project:
    - Redirect focus back to this project’s advantages (ROI, lifestyle, connectivity).
    - IF builder has another project there, mention it briefly in 1 line.
    - Only elaborate if user explicitly says “Tell me more.”
    - Always return focus to {project_name}.

LEGITIMACY / RERA LOGIC:
- If user asks about legality or RERA:
    - Give the factual status.
    - Add one line on developer compliance & buyer safety.
- Do not talk legality unless user triggers it.

UNCERTAINTY HANDLING:
- If information is unknown or pending:
    - Say: “this requires expert verification, I will confirm,”
    - Do NOT make up data, timelines or guarantees.

QUALIFICATION BEHAVIOR:
- Extract details from user statements.
- Ask at most ONE qualification question every 2–3 turns.
- If user is hesitant or “just exploring” → DO NOT qualify, only support.

PERSUASION BEHAVIOR:
- Use ROI, appreciation potential, convenience, family comfort.
- Keep it mild — no pressure.
- After deeper clarity, gently suggest visit.

{lang_hint}

FORMAT:
- short, human-like WhatsApp replies
- answer-first
- advisory tone
"""

    msgs = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:
        msgs.append({"role": "assistant" if h["from"] == "bot" else "user", "content": h["text"]})
    msgs.append({"role": "user", "content": user_text})

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msgs,
        temperature=0.5,
        max_tokens=75,
    )

    reply = res.choices[0].message.content.strip()
    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)
    return reply
