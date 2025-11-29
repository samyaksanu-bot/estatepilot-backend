def route_message(text, state, counters):
    text = text.lower().strip()

    if "price" in text:
        state["last_question"] = "price_query"
        return counters["price_query"]["responses"]["english"]

    if "location" in text:
        state["last_question"] = "location_query"
        return counters["location_query"]["responses"]["english"]

    if text in ["yes", "ok", "haan"]:
        return counters["vague_confirmation"]["responses"]["english"]

    return "I want to guide you properly. Are you checking price, location, or availability?"
