# app/conversation_engine.py

def next_reply(text: str, state: dict) -> str:
    text = text.lower().strip()
    state["messages_count"] += 1

    # ---------------- STEP 1: INTRO ----------------
    if state["step"] == "intro":
        state["step"] = "intent"
        return (
            "Hi 👋 Happy to help.\n\n"
            "What would you like to know about?\n"
            "1️⃣ Price range\n"
            "2️⃣ Location\n"
            "3️⃣ Project details"
        )

    # ---------------- STEP 2: INTENT ----------------
    if state["step"] == "intent":
        if "price" in text or "budget" in text:
            state["intent"] = "price"
            state["step"] = "budget"
            return "Sure. What budget range are you considering?"

        if "location" in text or "where" in text:
            state["intent"] = "location"
            state["step"] = "location"
            return "Which area or locality are you looking at?"

        if "detail" in text or "project" in text or "more" in text:
            state["intent"] = "details"
            return (
                "This is a verified project with clear titles and good connectivity.\n"
                "Would you like to check price or location first?"
            )

        return "Just to guide you better—are you checking price, location, or details?"

    # ---------------- STEP 3: BUDGET ----------------
    if state["step"] == "budget":
        state["budget"] = text
        state["step"] = "soft_visit"
        return (
            "That works 👍 Based on this budget, there are suitable options.\n\n"
            "Would you like the project location, or should I help arrange a site visit?"
        )

    # ---------------- STEP 4: LOCATION ----------------
    if state["step"] == "location":
        state["location"] = text
        state["step"] = "soft_visit"
        return (
            f"{text.title()} is a good choice.\n\n"
            "Would you like price details or prefer to visit the site?"
        )

    # ---------------- STEP 5: SOFT VISIT (NOT PUSHY) ----------------
    if state["step"] == "soft_visit":
        if "visit" in text or "see" in text or "site" in text:
            state["step"] = "handoff"
            state["handoff"] = True
            return (
                "Perfect 👍\n"
                "I’ll have our local advisor call you shortly to coordinate a site visit.\n"
                "They’ll confirm the date and timing with you."
            )

        return (
            "No rush at all 🙂\n"
            "I can share price breakup, layout plan, or nearby landmarks.\n"
            "What would you like?"
        )

    # ---------------- STEP 6: HANDOFF ----------------
    if state["step"] == "handoff":
        return (
            "Our advisor will reach out shortly.\n"
            "Meanwhile, feel free to ask if you need anything else."
        )

    # ---------------- FALLBACK ----------------
    return "I’m here to help 🙂 Tell me what you’d like to know."
