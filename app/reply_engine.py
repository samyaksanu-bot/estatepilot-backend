# app/reply_engine.py

def ai_fallback_reply(
    user_text: str,
    context: dict | None = None
) -> str:
    """
    Lightweight AI fallback.
    Called ONLY when template engine cannot answer.
    Safe. No external API call.
    """

    text = user_text.lower()

    if any(k in text for k in ["price", "cost", "budget"]):
        return "Pricing depends on unit size and floor. Are you looking for 2BHK or 3BHK?"

    if any(k in text for k in ["location", "area", "kahaan", "kaha"]):
        return "The project is well-connected. Would you prefer proximity to office or schools?"

    if any(k in text for k in ["visit", "site", "dekha"]):
        return "I can help arrange a site visit. What day works for you?"

    return (
        "I can help with price, location, amenities, or site visit. "
        "What would you like to know?"
    )
