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
            "Hi, I’m Pragiti.\n"
            "I help with verified details, pricing, availability and site visits or any information about this project.\n\n"
            "Please tell me Which language do you prefer — English, Hindi, or Hinglish?"
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
            state["language"] = "english"
            state["step"] = "project_intro"
            return (
                "No worries, I’ll continue in English.\n"
                "You can switch anytime."
            )

        # Smooth transition (NO OK CONFIRMATION)
        state["step"] = "project_intro"
        return f"Sure, I’ll continue in {state['language']}. Let’s move ahead."

    # =============================
    # 3) PROJECT INTRODUCTION STEP
    # =============================
    if step == "project_intro":

        project = state.get("project_context")
        if not project:
            return "Please tell me which project you are exploring."

        lang = state["language"] or "english"

        # *** IMPORTANT CHANGE ***
        # INTRO SHOULD NOW BE SHORTER AND CLEANER
        if lang == "english":
            intro = (
                f"{project['name']} at {project['location']}.\n\n"
                f"Starting price: {project['price_range']}\n"
                f"Units: {project['unit_types']} with modern amenities.\n\n"
                "Would you like more details or explore floor plans?"
            )
        elif lang == "hindi":
            intro = (
                f"{project['name']} {project['location']} mein.\n\n"
                f"Starting price: {project['price_range']}\n"
                f"Units: {project['unit_types']} modern amenities ke sath.\n\n"
                "Aap details explore karna chahenge ya floor plans dekhna chahenge?"
            )
        else:
            intro = (
                f"{project['name']} {project['location']} mein.\n\n"
                f"Pricing: {project['price_range']}\n"
                f"Units: {project['unit_types']} modern amenities ke sath.\n\n"
                "Aap details explore karna chahenge ya floor plans dekhna chahenge?"
            )

        state["step"] = "decision"
        return intro

    # =============================
    # 4) DECISION STEP — hybrid
    # =============================
    if step == "decision":
        t = text.lower()

        # ==============================================
        #  ** NEW BUSINESS-SAFETY BLOCK **
        # ==============================================
        # If user asks about another locality or project
        # Example:
        # "Do you have property in Raja Bazar?"
        # "Any other projects?"
        # "I want different location"
        #
        # → DO NOT allow competitor suggestion
        # → AI must redirect and preserve exclusivity

        locality_change_words = [
            "any project in", "any flat in", "different location",
            "other project", "other locality", "another place",
            "raja bazar", "raza bazar", "kankarbagh", "boring road",
            "search other", "alternative project"
        ]

        if any(word in t for word in locality_change_words):
            state["ai_mode"] = True
            state["exclusive_redirect"] = True  # IMPORTANT FLAG
            return call_ai(phone, text)

        # ==============================================
        # LEGALITY TRIGGER
        # ==============================================
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
        # NO RESTART — maintain context
        return call_ai(phone, text)

    # =============================
    # SAFETY FALLBACK
    # =============================
    return call_ai(phone, text)
