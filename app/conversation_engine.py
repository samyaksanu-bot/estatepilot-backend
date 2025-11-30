# app/conversation_engine.py

def next_reply(text: str, state: dict) -> str:
    text = text.lower().strip()

    # ---------------- START ----------------
    if state["stage"] == "start":
        state["stage"] = "discover"
        return (
            "Hi 👋 Glad you reached out.\n"
            "Tell me—are you exploring plots or flats at the moment?"
        )

    # ---------------- DISCOVER ----------------
    if state["stage"] == "discover":
        if "plot" in text or "land" in text:
            state["interest"] = "plot"
        elif "flat" in text or "apartment" in text:
            state["interest"] = "flat"
        else:
            return (
                "Got it 👍\n"
                "Are you more interested in plots or ready-to-move flats?"
            )

        state["stage"] = "qualify"
        return (
            f"Nice choice. {state['interest'].title()} projects are in strong demand.\n"
            "What kind of location do you prefer?"
        )

    # ---------------- QUALIFY ----------------
    if state["stage"] == "qualify":
        if state["location"] is None:
            state["location"] = text
            return (
                f"Understood. {text.title()} is a solid area.\n"
                "Do you already have a budget range in mind?"
            )

        if state["budget"] is None:
            state["budget"] = text
            state["stage"] = "engage"
            return (
                "Thanks for sharing 👍\n"
                "Based on what you told me, I have a few good options.\n"
                "Would you like details first or prefer to see the site once?"
            )

    # ---------------- ENGAGE (HUMAN FEEL) ----------------
    if state["stage"] == "engage":
        if any(k in text for k in ["visit", "see", "site", "come"]):
            state["visit_ready"] = True
            state["stage"] = "handoff"
            return (
                "That makes sense 👍\n"
                "A quick site visit usually clears everything.\n"
                "I’ll ask our local advisor to call and fix a convenient time for you."
            )

        if any(k in text for k in ["price", "cost", "detail", "more"]):
            return (
                "Sure.\n"
                "These projects have clear titles, good access roads, and planned development.\n"
                "No rush at all—whenever you feel comfortable, we can plan a visit."
            )

        return (
            "I’m here to help—tell me what you’d like to know next 😊"
        )

    # ---------------- HANDOFF ----------------
    if state["stage"] == "handoff":
        if not state["handoff_done"]:
            state["handoff_done"] = True
            return (
                "✅ Request noted.\n"
                "Our advisor will call you shortly to confirm date and time.\n"
                "Meanwhile, feel free to ask me anything."
            )

        return "Our advisor will connect with you shortly. 👍"

    # ---------------- FALLBACK ----------------
    return "Tell me a bit more so I can guide you better 🙂"
