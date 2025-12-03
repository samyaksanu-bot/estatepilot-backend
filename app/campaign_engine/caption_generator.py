# app/campaign_engine/caption_generator.py

def generate_caption(project: dict, intent_profile: dict, creative_brief: dict) -> list:
    """
    Writes high-intent real estate captions.
    Acts like a senior sales-focused copywriter.
    """

    property_type = intent_profile["property_type"]
    location = intent_profile["location"]
    price_min, price_max = intent_profile["budget_range"]
    timeline = intent_profile["planning_timeline"]
    intent_level = intent_profile["intent_level"]

    captions = []

    # ---------------- Caption Version 1: Direct Filter ----------------
    caption_1 = f"""
Looking for a {property_type} in {location}?

Price range ₹{price_min}–{price_max} lakh.
Clear title | Verified project.

Best suited for buyers planning to purchase within {timeline}.
WhatsApp now to check availability & exact details.
""".strip()

    captions.append(caption_1)

    # ---------------- Caption Version 2: Trust + Qualification ----------------
    caption_2 = f"""
Serious buyers only.

{property_type.capitalize()} available near {location},
starting from ₹{price_min} lakh.

Ideal for end-users looking to finalize within {timeline}.
Message on WhatsApp for verified information.
""".strip()

    captions.append(caption_2)

    # ---------------- Caption Version 3: Disqualification Focus ----------------
    if intent_level == "high":
        caption_3 = f"""
Planning to buy a {property_type} soon?

Location: {location}
Budget: ₹{price_min}–{price_max} lakh

Not suitable for brokers or casual enquiries.
WhatsApp to confirm availability.
""".strip()

        captions.append(caption_3)

    return captions
