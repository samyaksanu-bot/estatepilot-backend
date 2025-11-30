def next_reply(text: str, state: dict) -> str:
    text = text.lower().strip()
    state["replies"] += 1

    # ---- INTRO ----
    if state["stage"] == "intro":
        state["stage"] = "explain"
        return (
            "Sure 🙂 happy to explain.\n\n"
            "This project offers residential plots with clear titles and road access. "
            "Before I go deeper — are you exploring casually or planning to buy soon?"
        )

    # ---- EXPLAIN ----
    if state["stage"] == "explain":
        state["stage"] = "qualify"
        return (
            "Got it. That helps.\n\n"
            "People usually look at this project based on *budget range* and *preferred location*. "
            "May I know which area you’re considering?"
        )

    # ---- QUALIFY ----
    if state["stage"] == "qualify":
        state["location"] = text
        state["stage"] = "deepen"
        return (
            "Thanks for sharing.\n\n"
            "Most buyers here consider budgets between ₹15–30L depending on plot size. "
            "Does that feel roughly comfortable for you?"
        )

    # ---- DEEPEN ----
    if state["stage"] == "deepen":
        state["budget"] = text
        if not state["visit_offered"]:
            state["visit_offered"] = True
            state["stage"] = "visit"
            return (
                "That makes sense.\n\n"
                "At this point, many people prefer a quick site visit — it clears doubts instantly. "
                "If you like, I can help coordinate that without any pressure."
            )

    # ---- VISIT ----
    if state["stage"] == "visit":
        state["stage"] = "human"
        return (
            "Perfect 👍\n\n"
            "I’ll have a site executive coordinate with you shortly. "
            "Thanks for taking the time — speak soon."
        )

    return "Understood. Let me check and get back to you shortly."
