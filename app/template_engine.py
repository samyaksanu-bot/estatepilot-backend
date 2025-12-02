# app/template_engine.py

import random

TEMPLATES = {

    "configuration": [
        "We have spacious 3BHK options with good ventilation. Is this for self-use or investment?",
        "3BHK flats are available with multiple layouts. Do you prefer bigger bedrooms or a large living area?",
        "Our 3BHK units suit families planning long-term. Any minimum size you have in mind?",
        "That works. Are you currently staying nearby or relocating?",
        "3BHK inventory is limited. Would you be open to exploring floor plans?",
        "Good choice. Many buyers choose 3BHK for future needs—budget range kya socha hai?"
    ],

    "location_query": [
        "The project is in a well-connected area close to daily essentials. Office location bata sakte ho?",
        "Location wise, it’s peaceful yet accessible. School ya workplace distance important hai?",
        "This area has good future growth. Kya aap end-use ke liye dekh rahe ho?",
        "Nearby schools, hospitals and markets are easily accessible. Highway ya metro proximity chahiye?",
        "Location works well for families. Aap kis side ka area prefer karte ho?",
        "Surroundings are developed. Would you like a map or landmarks?"
    ],

    "price_query": [
        "Pricing depends on size and floor. Budget range batao, main best option suggest karunga.",
        "3BHK pricing varies slightly based on view and floor. Approx budget?",
        "Is this purchase budget-fixed or flexible for the right home?",
        "Current pricing is competitive for the area. Loan option chahiye?",
        "Would EMI planning help you decide better?",
        "Are you comparing with other projects nearby?"
    ],

    "site_visit": [
        "Site visit can be arranged easily. Weekday ya weekend convenient rahega?",
        "Perfect. Morning ya evening slot better lagega?",
        "I’ll arrange a visit with our site advisor. Preferred date?",
        "Seeing the site clarifies everything. Kisi family member ko bhi lana chahoge?",
        "We can block a slot. Location share kar doon?",
        "After visit, pricing discussions become clearer."
    ]
}


def get_template(intent: str, depth: int = 0) -> str:
    options = TEMPLATES.get(intent)

    if not options:
        return None

    # rotate templates by depth
    index = depth % len(options)
    return options[index]
