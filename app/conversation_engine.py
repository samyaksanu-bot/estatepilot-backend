def next_reply(text: str, state: dict) -> str:
    text = text.lower().strip()

    # STEP 1: INTRO
    if state["step"] == "intro":
        state["step"] = "discover"
        return (
            "Got it 👍\n"
            "To guide you properly, what would you like to know first?\n\n"
            "1️⃣ Price range\n"
            "2️⃣ Location\n"
            "3️⃣ Project details"
        )

    # STEP 2: DISCOVERY
    if state["step"] == "discover":
        if "price" in text or "budget" in text:
            state["step"] = "budget"
            return "Sure. What budget range are you considering?"

        if "location" in text or "where" in text:
            state["step"] = "location"
            return "Which preferred location are you looking at?"

        if "detail" in text or "more" in text or "project" in text:
            return (
                "This is a gated project with verified plots, clear titles, "
                "and good connectivity.\n\n"
                "Would you like to check price or location first?"
            )

        return "Just to help you better—are you checking price, location, or details?"

    # STEP 3: BUDGET
    if state["step"] == "budget":
        state["budget"] = text
        state["step"] = "soft_visit"
        return (
            "Thanks 👍\n"
            "Based on that budget, we have suitable options.\n\n"
            "Would you like me to share the location or schedule a site visit?"
        )

    # STEP 4: LOCATION
    if state["step"] == "location":
        state["location"] = text
        state["step"] = "soft_visit"
        return (
            f"Great choice. {text.title()} is a promising area.\n\n"
            "Would you like price details or plan a visit to see the project?"
        )

    # STEP 5: SOFT VISIT (NOT PUSHY)
    if state["step"] == "soft_visit":
        if "visit" in text or "see" in text:
            state["step"] = "handoff"
            return (
                "Perfect. I'll arrange a site visit for you.\n"
                "Our local advisor will coordinate with you shortly."
            )

        return (
            "No rush 🙂\n"
            "I can share price breakup, layout, or nearby landmarks—"
            "what would you like?"
        )

    # FALLBACK
    return "I’m here to help—tell me what you’d like to know 😊"
