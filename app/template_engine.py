import random

# -------------------------------
# TEMPLATE POOL (INTENT → REPLIES)
# -------------------------------

TEMPLATES = {

    "greeting": [
        "Hi 👋 How can I help you with this project?",
        "Hello! Looking for price, location or flat details?",
        "Namaste 🙏 How may I assist you today?",
        "Hi there! Are you exploring or planning to buy?",
        "Hello 🙂 What would you like to know about this project?"
    ],

    "price_query": [
        "Prices depend on flat size and floor. Are you looking for 2BHK or 3BHK?",
        "The starting price varies by configuration. What size are you considering?",
        "Pricing differs by view and unit type. What’s your approximate budget?",
        "We have multiple price options. Would you prefer compact or spacious homes?",
        "Price is influenced by amenities and location. Shall I share a rough range?",
        "Is price your top priority or are you flexible for better location?"
    ],

    "location_query": [
        "The project is located in a well-connected area. Do you travel daily for work?",
        "It’s close to schools, hospitals and shopping. What’s most important to you?",
        "The location offers good road and public transport access.",
        "Nearby essentials are easily accessible. Would you like landmark details?",
        "It’s a growing area with future appreciation potential.",
        "Would you prefer living close to city or peaceful surroundings?"
    ],

    "configuration_query": [
        "We offer 2BHK and 3BHK options. What size fits your family?",
        "Are you looking for a compact home or more open space?",
        "How many family members will stay together?",
        "Would you like a balcony or utility space preference?",
        "Are you upgrading or buying your first home?"
    ],

    "site_visit": [
        "I can arrange a site visit for you. What day works best?",
        "Would weekday or weekend be more convenient for a visit?",
        "Site visits help understand layout better. Shall I schedule one?",
        "Would morning or evening be suitable for you?",
        "Our advisor can walk you through everything on site."
    ],

    "purchase_intent_high": [
        "That’s great 👍 Would you like me to arrange a site visit or call?",
        "Sounds like you’re serious. Shall I connect you with our advisor?",
        "We can block options early for you. Would you like next steps?",
        "Shall I help you with booking process details?",
        "Do you want availability and unit options now?"
    ],

    "vague": [
        "No worries 🙂 What detail would you like to start with?",
        "Sure. Are you more curious about price or location?",
        "Take your time. What matters most to you in a home?",
        "Would you like guidance based on budget or lifestyle?"
    ]
}

# --------------------------------
# TEMPLATE SELECTOR (DEPTH-AWARE)
# --------------------------------

def get_template(intent: str, state: dict) -> str | None:
    depth = state.get("intent_depth", {}).get(intent, 0)
    options = TEMPLATES.get(intent)

    if not options:
        return None

    reply = options[depth % len(options)]

    state.setdefault("intent_depth", {})
    state["intent_depth"][intent] = depth + 1

    return reply
