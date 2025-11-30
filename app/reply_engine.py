def generate_reply(text: str, state: dict) -> str | None:
    text = text.lower().strip()

    # ✅ BLOCK BOT AFTER HANDOFF
    if state.get("handoff_done"):
        return None

    # ✅ IGNORE VERY SHORT OR NOISE MESSAGES
    if len(text) <= 2 or text in ["ok", "okay", "cool", "no", "yes", "hmm"]:
        return None

    # STEP 1: INTRO
    if state["step"] == "intro":
        state["step"] = "discover"
        return (
            "Hi 👋 Happy to help.\n\n"
            "What would you like to know first?\n"
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
            return "Which location are you looking at?"

        if "detail" in text or "project" in text:
            return (
                "This is a gated project with clear titles and good connectivity.\n"
                "Would you like to check price or location?"
            )

        return "Just to guide you better—are you checking price, location, or project details?"

    # STEP 3: BUDGET
    if state["step"] == "budget":
        state["budget"] = text
        state["step"] = "soft_visit"
        return (
            "That works 👍 Based on this budget, we have suitable options.\n\n"
            "Would you like the location details or shall I help arrange a site visit?"
        )

    # STEP 4: LOCATION
    if state["step"] == "location":
        state["location"] = text
        state["step"] = "soft_visit"
        return (
            f"Great choice. {text.title()} is a promising area.\n\n"
            "Would you like price details or plan a site visit?"
        )

    # STEP 5: SOFT VISIT (NON-PUSHY)
    if state["step"] == "soft_visit":
        if "visit" in text or "see" in text or "come" in text:
            sta
