from app.state import get_state, append_history
from app.ai_engine import call_ai

def detect_language_from_text(text: str) -> str:
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


def route_message(phone: str, text: str) -> str:
    state = get_state(phone)
    step = state["step"]
    user_lang = state["language"]

    # =============================
    # 1) INTRO STEP
    # =============================
    if step == "intro":
        state["step"] = "language"
        return (
            "Hi, I’m Pragiti from EstatePilot.\n"
            "I help you with verified real estate projects — availability, pricing, amenities and site visits.\n\n"
            "Before we continue, which language do you prefer?\n"
            "English, Hindi or Hinglish?"
        )

    # =============================
    # 2) LANGUAGE SELECTION STEP
    # =============================
    if step == "language":
        t = text.strip().lower()

        if t in ["english", "eng", "en"]:
            state["language"] = "english"
        elif t in ["hindi", "hin", "hi"]:
            state["language"] = "hindi"
        elif t in ["hinglish", "mix"]:
            state["language"] = "hinglish"
        else:
            # FIXED: No OK confirmation — flow continues naturally
            state["language"] = "english"
            state["step"] = "project_intro"
            return (
                "No worries, I’ll continue in English for now.\n"
                "You can switch to Hindi or Hinglish anytime."
            )

        # FIXED: Immediately move to next step without waiting
        state["step"] = "project_intro"
        return f"Sure, I’ll continue in {state['language']}. Let’s move ahead."

    # =============================
    # 3) PROJECT INTRODUCTION STEP
    # =============================
    if step == "project_intro":

        project = state.get("project_context")
        if not project:
            return "Please tell me which project you are exploring, and I'll share full details."

        lang = state["language"] or "english"

        if lang == "english":
            intro = (
                f"{project['name']} is located at {project['location']}.\n\n"
                f"Price starts from {project['price_range']}.\n"
                f"It offers {project['unit_types']} with modern amenities including {project['usp']}.\n"
                "Nearby development and connectivity make it ideal for families and long-term appreciation.\n\n"
                "Would you like more detailed information,\n"
                "or should I help you plan a short site visit for clarity?"
            )

        elif lang == "hindi":
            intro = (
                f"{project['name']} {project['location']} mein located hai.\n\n"
                f"Starting price {project['price_range']} se hai.\n"
                f"Isme {project['unit_types']} units aur modern amenities milte hain — {project['usp']}.\n"
                "Nearby development aur connectivity isey families aur investment ke liye ideal banata hai.\n\n"
                "Kya aap project ke baare mein aur details chahte hain,\n"
                "ya main aapke liye short site visit plan karoon?"
            )

        else:
            intro = (
                f"{project['name']} {project['location']} mein situated hai.\n\n"
                f"Pricing approx {project['price_range']} se start hoti hai.\n"
                f"Isme {project['unit_types']} aur modern amenities milti hain — {project['usp']}.\n"
                "Area development aur connectivity good future appreciation deta hai.\n\n"
                "Aap details explore karna chahenge,\n"
                "ya short site visit plan kar du clarity ke liye?"
            )

        state["step"] = "decision"
        return intro

    # =============================
    # 4) DECISION STEP — hybrid
    # =============================
    if step == "decision":
        t = text.lower()

        # **NEW BLOCK — LEGALITY / RERA detection**
        if any(x in t for x in ["rera", "approved", "legal", "permission", "authority", "registration", "brera"]):
            state["ai_mode"] = True
            state["credibility_trigger"] = True
            return call_ai(phone, text)

        # Visit intent DURING DECISION STAGE
        if any(x in t for x in ["visit", "site", "see property", "meet", "come"]):
            state["ai_mode"] = True
            return call_ai(phone, text)

        # User wants more info → AI MODE
        if any(x in t for x in ["more", "details", "explain", "what about", "availability", "pricing"]):
            state["ai_mode"] = True
            return call_ai(phone, text)

        # Unsure → AI MODE
        if any(x in t for x in ["confused", "not sure", "thinking", "doubt"]):
            state["ai_mode"] = True
            return call_ai(phone, text)

        # Default → AI MODE
        state["ai_mode"] = True
        return call_ai(phone, text)

    # =============================
    # 5) ANY STEP AFTER AI MODE
    # =============================
    if state.get("ai_mode") is True:
        # IMPORTANT: do not reset state or restart intro here
        return call_ai(phone, text)

    # =============================
    # SAFETY FALLBACK
    # =============================
    # FIXED: Never restart intro — just continue in AI mode
    return call_ai(phone, text)
