# app/whatsapp/flow.py

from app.state import get_state


def detect_intent(text: str) -> str:
    """
    Very simple keyword-based intent detection.
    We don't need GPT here yet.
    """
    t = text.lower()

    if any(w in t for w in ["price", "budget", "cost", "rate"]):
        return "price"
    if any(w in t for w in ["location", "where", "area", "site"]):
        return "location"
    if any(w in t for w in ["available", "availability", "possession", "ready to move"]):
        return "availability"
    if any(w in t for w in ["visit", "see", "come", "site visit", "dekna", "dekhna"]):
        return "visit"
    if any(w in t for w in ["more", "details", "detail", "project", "information", "info"]):
        return "overview"

    # language detection keywords
    if "english" in t:
        return "lang_english"
    if "hindi" in t:
        return "lang_hindi"
    if "hinglish" in t:
        return "lang_hinglish"

    return "unknown"

def detect_language_from_text(text: str) -> str:
    """
    Lightweight rule-based language detector.
    We only care about: english / hindi / hinglish
    """

    hindi_words = [
        "kya", "kab", "kaise", "ghar", "zameen", "flat",
        "booking", "visit", "kal", "aaj", "weekend",
        "paisa", "loan", "possession", "dekho", "dekhna",
        "side", "wali", "area", "ke", "ki"
    ]

    t = text.lower()
    hits = sum(1 for w in hindi_words if w in t)

    # strong hindi
    if hits >= 4:
        return "hindi"

    # mixed hinglish
    if 2 <= hits < 4:
        return "hinglish"

    # default: english
    return "english"

def route_message(phone: str, text: str) -> str:
    """
    Updated conversation flow (SAFE UPGRADE):

    intro → language → (existing budget/location/visit)
    """

    state = get_state(phone)
    step = state["step"]
    intent = detect_intent(text)
    state["last_intent"] = intent  # backwards compatibility

    # ==================================================
    # STEP 1: INTRO (ALWAYS FIRST MESSAGE)
    # ==================================================
    if step == "intro":
        state["step"] = "language"
        return (
            "Hi, I’m Pragiti — your property assistant.\n\n"
            "Before we continue, which language do you prefer?\n"
            "Options: English / Hindi / Hinglish"
        )

    # ==================================================
    # STEP 2: LANGUAGE SELECTION
    # ==================================================
    if step == "language":

        # explicit language command detected
        if intent == "lang_english":
            state["language"] = "english"
            state["step"] = "budget"
            return (
                "Great, I’ll continue in English.\n\n"
                "What’s your approximate budget range? e.g. 40–50L or 80–90L?"
            )

        if intent == "lang_hindi":
            state["language"] = "hindi"
            state["step"] = "budget"
            return (
                "Theek hai, main Hindi mein continue karungi.\n\n"
                "Aapka approx budget range kya hoga? Jaise 40–50L ya 80–90L."
            )

        if intent == "lang_hinglish":
            state["language"] = "hinglish"
            state["step"] = "budget"
            return (
                "Perfect, main Hinglish mein continue karoongi.\n\n"
                "Approx budget batao? Jaise 40–50L ya 80–90L."
            )

        # user gives vague answer — fallback handling
        # DO NOT push repeatedly — just propose English (safe default)
        if len(text.strip()) < 3 or intent == "unknown":
            return (
                "No worries. If language preference is unclear, I can continue in English.\n"
                "Say OK to continue, or you can specify Hindi/Hinglish anytime."
            )

        # if user replies OK to fallback
        if text.strip().lower() in ["ok", "okay", "yes", "sure"]:
            state["language"] = "english"
            state["step"] = "budget"
            return (
                "Done — continuing in English.\n\n"
                "What’s your approximate budget range?"
            )

    # ==================================================
    # AFTER STEP 2: USE YOUR ORIGINAL FLOW (BUDGET → LOCATION → VISIT → DONE)
    # ==================================================

    # =================== BUDGET ======================
    if step == "budget":
        # accept any meaningful text as budget
        if len(text.strip()) < 2 and intent != "price":
            return (
                "Just give rough budget — 40–50L or 80–90L type.\n"
                "No need to be exact."
            )

        state["budget"] = text.strip()
        state["step"] = "location"
        return (
            f"Noted: budget '{state['budget']}'.\n\n"
            "Which area or locality do you prefer?"
        )

    # =================== LOCATION ======================
    if step == "location":
        if len(text.strip()) < 3 and intent != "location":
            return (
                "Tell me area preference — airport side, ring road, school belt, etc."
            )

        state["location"] = text.strip()
        state["step"] = "visit"
        return (
            f"Location '{state['location']}' noted.\n\n"
            "When would you be comfortable for a site visit? Today, tomorrow, weekend?"
        )

    # =================== VISIT ======================
    if step == "visit":
        state["visit_time"] = text.strip()
        state["qualified"] = True
        state["step"] = "done"

        return (
            "Site visit preference noted.\n\n"
            "Next step: Advisor will call you and send location.\n"
            "Meanwhile, if you want pricing or availability, ask me here."
        )

    # =================== DONE ======================
    if step == "done":
        if intent == "price":
            return (
                "Pricing depends on unit type. During call we match exact options.\n"
                "If you prefer EMI or structured plan, just tell me."
            )

        if intent == "location":
            return (
                "Exact map will be shared before visit. Landmark is easy to reach.\n"
                "For now area matches what you mentioned."
            )

        return (
            "Team already picked your lead. If call is missed, message me for follow-up."
        )

    # fallback safety
    state["step"] = "intro"
    return (
        "Let's restart. Which language do you prefer: English, Hindi, Hinglish?"
    )

