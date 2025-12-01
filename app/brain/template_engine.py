# app/brain/template_engine.py

import random

TEMPLATES = {

    "PRICE_QUERY": [
        {
            "reply": "The project starts from ₹{price}. Pricing depends on unit and floor.",
            "followup_type": "clarification",
            "followup": "Is this budget close to what you were considering?"
        },
        {
            "reply": "Starting prices are around ₹{price} with options across configurations.",
            "followup_type": "preference",
            "followup": "Are you mainly looking for self-use or investment?"
        },
        {
            "reply": "Base pricing begins at ₹{price}. Final cost varies based on choice.",
            "followup_type": "assurance",
            "followup": "If the location and quality are right, would this range work for you?"
        },
        {
            "reply": "The lowest available price point is ₹{price} at the moment.",
            "followup_type": "comparison",
            "followup": "Are you comparing this with any other project nearby?"
        },
        {
            "reply": "Prices currently start from ₹{price}, depending on availability.",
            "followup_type": "progression",
            "followup": "Would you like me to share the exact location or project details?"
        },
        {
            "reply": "₹{price} is the current entry price for this project.",
            "followup_type": "soft_probe",
            "followup": "Is this within the range you’re comfortable exploring?"
        },
        {
            "reply": "At present, ₹{price} is the starting range for available units.",
            "followup_type": "context",
            "followup": "Are you planning to move soon or is this for future planning?"
        }
    ]

    # Other intents will follow the same structure
}


def generate_reply(intent: str, context: dict) -> str:
    if intent not in TEMPLATES:
        return "Sure, could you tell me a bit more about what you’re looking for?"

    template = random.choice(TEMPLATES[intent])

    reply = template["reply"].format(**context)
    followup = template["followup"]

    return f"{reply} {followup}"
