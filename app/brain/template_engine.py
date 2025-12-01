# app/brain/template_engine.py

import random

TEMPLATES = {

    "PRICE_QUERY": [
        {
            "reply": "The project starts from ₹{price}. Pricing depends on unit and floor.",
            "followup": "Is this close to the budget you had in mind?"
        },
        {
            "reply": "Starting price is around ₹{price}, with multiple options available.",
            "followup": "Are you looking for self-use or investment?"
        }
    ],

    "LOCATION_QUERY": [
        {
            "reply": "The project is located in a well-connected area with daily conveniences nearby.",
            "followup": "Are you looking for something close to your workplace?"
        },
        {
            "reply": "It’s situated in a prime residential zone with smooth connectivity.",
            "followup": "Would you prefer details on nearby schools and hospitals?"
        }
    ],

    "AMENITIES_QUERY": [
        {
            "reply": "The project offers essential amenities along with a peaceful environment.",
            "followup": "Will this be for family living or investment?"
        }
    ],

    "VISIT_INTENT": [
        {
            "reply": "Sure, a site visit can be arranged at your convenience.",
            "followup": "What day and time works best for you?"
        }
    ],

    "CALLBACK_REQUEST": [
        {
            "reply": "No problem, I can arrange a callback for you.",
            "followup": "What would be a good time to call?"
        }
    ]
}


def generate_reply(intent: str, context: dict) -> str:
    if intent not in TEMPLATES:
        return "Sure. Please let me know what details you’d like to know."

    template = random.choice(TEMPLATES[intent])

    reply = template["reply"].format(**context)
    followup = template["followup"]

    return f"{reply} {followup}"
