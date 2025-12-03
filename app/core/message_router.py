def decide_reply(message_text: str, config: dict) -> dict:
    msg = message_text.lower()

    replies = config["auto_replies"]
    project = config["project"]
    client = config["client"]

    HIGH_INTENT_KEYWORDS = [
        "visit", "book", "meeting", "meet",
        "schedule", "today", "tomorrow",
        "interested", "buy", "ready"
    ]

    for word in HIGH_INTENT_KEYWORDS:
        if word in msg:
            return {
                "type": "escalate",
                "text": "✅ Thank you for your interest. Our sales team will contact you shortly."
            }

    if "brochure" in msg:
        return {"type": "reply", "text": replies["brochure"].format(
            brochure_url=project["brochure_url"])}

    if "location" in msg or "address" in msg:
        return {"type": "reply", "text": replies["location"].format(
            google_maps=project["google_maps"])}

    if "price" in msg or "cost" in msg:
        return {"type": "reply", "text": replies["price"].format(
            starting_price=project["starting_price"])}

    if "call" in msg or "contact" in msg:
        return {"type": "reply", "text": replies["contact"].format(
            sales_number=client["sales_number"])}

    return {"type": "reply", "text": replies["fallback"]}
    
from app.campaign_engine.campaign_preview import generate_campaign_preview


def test_campaign_preview(payload: dict):
    """
    TEMP TEST FUNCTION
    This does not touch WhatsApp or Meta.
    """
    print("✅ Campaign Preview Test Triggered")
    return generate_campaign_preview(payload)
