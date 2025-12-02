# app/reply_engine.py

import random
import re

# -----------------------------
# INTENT KEYWORDS (EN + HINGLISH)
# -----------------------------

INTENT_KEYWORDS = {
    "GREETING": [
        "hi", "hello", "hey", "namaste", "hii", "hy"
    ],

    "PRICE_QUERY": [
        "price", "cost", "rate", "budget", "amount",
        "kitna", "kitne ka", "daam", "price range"
    ],

    "LOCATION_QUERY": [
        "location", "where", "area", "address",
        "kaha", "kis area", "location kaha"
    ],

    "AMENITIES_QUERY": [
        "amenities", "facilities", "features",
        "kya kya", "amenities kya", "facility"
    ],

    "CONFIG_QUERY": [
        "bhk", "2bhk", "3bhk", "size", "sqft",
        "plot size", "configuration"
    ],

    "SITE_VISIT": [
        "visit", "site visit", "dekhna", "mil sakte",
        "location pe", "kab aa sakta"
    ],

    "CONFIRMATION": [
        "ok", "okay", "yes", "haan", "hmm", "sure"
    ]
}

# -----------------------------
# TEMPLATE POOL (6–10 PER INTENT)
# -----------------------------

TEMPLATES = {

    "GREETING": [
        "Hi! Happy to help 😊 What would you like to know about the project?",
        "Hello 👋 Are you looking for price, location, or project details?",
        "Namaste 🙏 How can I assist you today?"
    ],

    "PRICE_QUERY": [
        "Prices currently start around ₹45L. 
Would you like details on configurations or payment plans?",

        "The project starts approx ₹45L onwards. 
Are you checking budget first or location details?",

        "Budget roughly starts near ₹45L. 
Shall I explain what options come under this range?"
    ],

    "LOCATION_QUERY": [
        "The project is located in a well-developed area with good connectivity. 
Would nearby landmarks help?",

        "It’s in a growing residential zone with schools and daily needs nearby. 
Want exact map location?",

        "Location wise kaafi prime hai. 
Aap nearby landmarks dekhna chahenge?"
    ],

    "AMENITIES_QUERY": [
        "The project offers modern amenities like clubhouse, security, and green spaces. 
Want a full list?",

        "Amenities include lift, parking, and recreational areas. 
Koi specific facility chahiye?",

        "Basic to premium amenities available hain. 
Aap kis cheez ko priority dete ho?"
    ],

    "CONFIG_QUERY": [
        "We have multiple layout options available. 
Are you looking for a specific BHK or plot size?",

        "Different configurations hain depending on budget. 
2BHK ya 3BHK dekh rahe ho?",

        "Size options flexible hain. 
Approx kitna sqft aap expect kar rahe ho?"
    ],

    "SITE_VISIT": [
        "Sure 👍 I can arrange a site visit. 
Shall I have our advisor call you to confirm timing?",

        "Site visit possible hai. 
Date aur time bata do, team coordinate karegi.",

        "Best way is seeing it in person 🙂 
May I ask someone from our team to connect?"
    ],

    "CONFIRMATION": [
        "Got it 👍 Would you like to explore anything else?",
        "Perfect. Let me know what you’d like next.",
        "Sure 😊 What should we discuss next?"
    ],

    "FALLBACK": [
        "Got it. Could you tell me a bit more so I can guide you better?",
        "I want to help accurately 😊 Can you clarify what you’d like to know?",
        "Understood. Are you asking about price, location, or site visit?"
    ]
}

# -----------------------------
# INTENT DETECTION
# -----------------------------

def detect_intent(text: str) -> str:
    txt = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", txt):
                return intent
    return "FALLBACK"

# -----------------------------
# MAIN ENTRY POINT
# -----------------------------

def generate_reply(user_id: str, text: str, intent=None, depth=0) -> str:
    """
    Safe rule-based reply engine (EN + Hinglish)
    """

    intent = intent or detect_intent(text)

    template_pool = TEMPLATES.get(intent) or TEMPLATES["FALLBACK"]
    reply = random.choice(template_pool)

    return reply
