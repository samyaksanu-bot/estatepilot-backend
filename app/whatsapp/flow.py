# app/whatsapp/flow.py

from app.state import get_state


def detect_intent(text: str) -> str:
    """
    Basic keyword-based intent detector + language commands.
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

    # explicit language triggers
    if "english" in t:
        return "lang_english"
    if "hindi" in t:
        return "lang_hindi"
    if "hinglish" in t:
        return "lang_hinglish"

    return "unknown"


def detect_language_from_text(text: str) -> str:
    """
    Lightweight silent language detector — user may switch mid-flow.
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


def route_message(phone: str, text: str) -> str:
    """
    Improved WhatsApp flow:
    intro → language choice → budget → location → visit → done
    With silent language adaptation.
    """

    state = get_state(phone)
    step = state["step"]
    intent = detect_intent(text)
    state["last_intent"] = intent

    # ----------------------------------------------------
    # SILENT LANGUAGE ADAPTATION (AFTER SELECTION DONE)
    # ----------------------------------------------------
    if state.get("language") and step not in ["intro", "language"]:
        detected = detect_language_from_text(text)
        if detected != state["language"]:
            state["language"] = detected
        # do NOT say anything — continue normally

    # ----------------------------------------------------
    # STEP 1: INTRO
    # ----------------------------------------------------
    if step == "intro":
        state["step"] = "language"
        return (
            "Hi, I’m Pragiti — your property assistant.\n\n"
            "Before we continue, which language do you prefer?\n"
            "Options: English / Hindi / Hinglish"
        )

    # ----------------------------------------------------
    # STEP 2: LANGUAGE SELECTION
    # ----------------------------------------------------
    if step == "language":

        # explicit language triggers
        if intent == "lang_english":
            state["language"] = "english"
            state["step"] = "budget"
            return (
                "Great, continuing in English.\n\n"
                "What’s your approximate budget range?"
            )

        if intent == "lang_hindi":
            state["language"] = "hindi"
            state["step"] = "budget"
            return (
                "Theek hai, main Hindi mein continue karungi.\n\n"
                "Approx budget range kya hoga? Jaise 40–50L?"
            )

        if intent == "lang_hinglish":
            state["language"] = "hinglish"
            state["step"] = "budget"
            return (
                "Perfect, main Hinglish mein continue karoongi.\n\n"
                "Approx budget batao? Jaise 40–50L?"
            )

        # fallback option
        if len(text.strip()) < 3 or intent == "unknown":
            return (
                "No worries. If preference is unclear, I’ll continue in English.\n"
                "Say OK to continue, or specify Hindi/Hinglish anytime."
            )

        if text.strip().lower() in ["ok", "okay", "yes", "sure"]:
            state["language"] = "english"
            state["step"] = "budget"
            return (
                "Done. Continuing in English.\n\n"
                "What’s your approximate budget range?"
            )

    # ----------------------------------------------------
    # STEP 3: BUDGET
    # ----------------------------------------------------
    if step == "budget":
        if len(text.strip()) < 2 and intent != "price":
            return (
                "Just rough budget — 40–50L or 80–90L type.\n"
                "No need to be exact."
            )

        state["budget"] = text.strip()
        state["step"] = "location"
        return (
            f"Noted: budget '{state['budget']}'.\n\n"
            "Which area or locality do you prefer?"
        )

    # ----------------------------------------------------
    # STEP 4: LOCATION
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # STEP 5: VISIT
    # ----------------------------------------------------
    if step == "visit":
        state["visit_time"] = text.strip()
        state["qualified"] = True
        state["step"] = "done"

        return (
            "Site visit preference noted.\n\n"
            "Next step: Advisor will call you and send location.\n"
            "Meanwhile, if you want pricing or availability, ask me here."
        )

    # ----------------------------------------------------
    # STEP 6: DONE
    # ----------------------------------------------------
    if step == "done":
        if intent == "price":
            return (
                "Pricing depends on unit type. During call we match exact options.\n"
                "If you prefer EMI or structured plan, just tell me."
            )

        if intent == "location":
            return (
                "Exact map will be shared before visit.\n"
                "Area matches what you mentioned."
            )

        return (
            "Team already picked your lead. If call is missed, message me for follow-up."
        )

    # ----------------------------------------------------
    # SAFETY FALLBACK
    # ----------------------------------------------------
    state["step"] = "intro"
    return (
        "Let's restart.\n"
        "Which language do you prefer: English, Hindi, Hinglish?"
    )
