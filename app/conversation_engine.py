def next_reply(text: str, state: dict) -> str | None:
    text = text.lower().strip()

    # ✅ STOP BOT AFTER HANDOFF
    if state.get("handoff_done"):
        return None

    # ✅ IGNORE NOISE / SHORT MSGS
    if len(text) <= 2 or text in ["ok", "okay", "cool", "hmm", "no", "yes"]:
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

