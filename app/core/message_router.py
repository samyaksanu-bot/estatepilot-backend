def decide_reply(message_text: str, config: dict) -> str:
    msg = message_text.lower()

    replies = config["auto_replies"]
    project = config["project"]
    client = config["client"]

    if "brochure" in msg:
        return replies["brochure"].format(
            brochure_url=project["brochure_url"]
        )

    if "location" in msg or "address" in msg or "site" in msg:
        return replies["location"].format(
            google_maps=project["google_maps"]
        )

    if "price" in msg or "cost" in msg or "budget" in msg:
        return replies["price"].format(
            starting_price=project["starting_price"]
        )

    if "call" in msg or "contact" in msg or "number" in msg:
        return replies["contact"].format(
            sales_number=client["sales_number"]
        )

    return replies["fallback"]
