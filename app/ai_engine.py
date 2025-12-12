# app/ai_engine.py

import os
import re
import json
from time import sleep
from typing import Any, Dict, Optional

from openai import OpenAI
from app.state import get_state, append_history, mark_handoff

# ==========================================================
# OPENAI CLIENT INIT
# ==========================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


# ==========================================================
# LANGUAGE DETECTION (USED BY WHATSAPP BOT)
# ==========================================================
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


# ==========================================================
# WHATSAPP BOT AI (EXISTING LOGIC: keep behavior identical)
# ==========================================================
def call_ai(phone: str, user_text: str) -> str:
    """
    WhatsApp conversational handler (unchanged behavior).
    Returns the assistant reply as a string.
    """
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


# ==========================================================
# NEW: HELPER FOR PILLAR-2 (STRICT JSON OUTPUT FOR GPT-4.1)
# ==========================================================
# We'll add call_gpt_json and helper functions here — ensure no conflict
import typing  # kept minimal import if needed

def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Try to extract a JSON object from a text response.
    Returns parsed dict or None.
    """
    m = re.search(r"(\{[\s\S]*\})", text)
    candidate = m.group(1) if m else text.strip()
    try:
        return json.loads(candidate)
    except Exception:
        try:
            cand2 = candidate.replace("'", '"')
            return json.loads(cand2)
        except Exception:
            return None


def call_gpt_json(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4.1",
    temperature: float = 0.2,
    max_tokens: int = 900,
    retries: int = 2,
    retry_delay: float = 0.8
) -> Dict[str, Any]:
    """
    Call the OpenAI chat completion, expect a JSON object in the assistant reply.
    Returns a dict: either the parsed JSON or {'error': '...'}.
    Retries a small number of times if parsing fails.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    last_err = None
    for attempt in range(retries + 1):
        try:
            res = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = res.choices[0].message.content.strip()
            parsed = _extract_json_from_text(content)
            if parsed is not None:
                return parsed
            last_err = f"parse_failed: could not extract JSON from model output. raw: {content[:500]}"
        except Exception as e:
            last_err = f"api_error: {str(e)}"
        # small backoff before retry
        if attempt < retries:
            sleep(retry_delay)
    return {"error": "strategy_generation_failed", "reason": last_err}

