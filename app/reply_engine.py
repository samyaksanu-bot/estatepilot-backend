# app/reply_engine.py
"""
Template-based reply engine.
Takes an intent code + user text and returns a natural reply.
No external API calls. Safe for free-tier usage.
"""

from typing import Dict, List
import random


# ─────────────────────────────────────────────
# TEMPLATE POOL (ENGLISH + HINGLISH VARIANTS)
# ─────────────────────────────────────────────

TEMPLATES: Dict[str, List[str]] = {
    # 1) Price
    "price_query": [
        "Pricing depends on the flat size and floor. Are you looking for 1BHK, 2BHK or 3BHK?",
        "I’ll help you with price. Which configuration are you considering—2BHK or 3BHK?",
        "Price range changes by tower and view. Tell me your budget and I’ll share the best options.",
        "Instead of giving a random number, let me understand your budget first. Roughly what range are you comfortable with?",
        "Prices are dynamic and change with offers. Share your budget and I’ll tell you what is realistically possible here.",
        "We have options from mid-range to premium. What budget and BHK size are you targeting?",
    ],

    # 2) Location
    "location_query": [
        "This project is in a prime residential pocket with good road connectivity. Are you coming from office side or home side usually?",
        "Location is well connected to main roads and daily-need markets. Which area do you travel from daily?",
        "We’re close to schools, hospitals and basic shopping. What’s more important for you—office distance or kids’ school distance?",
        "Happy to share exact location + map link. Do you prefer landmark-based directions or a Google Maps pin?",
    ],

    # 3) Configuration / size
    "configuration_query": [
        "We have multiple configurations. Are you mainly considering 2BHK or also open to 3BHK?",
        "Do you have any minimum size in mind—for example 900 sqft, 1100 sqft etc.?",
        "Some buyers prefer compact usable layouts, others want bigger living room. What’s your priority?",
        "Tell me who will stay in the flat—only couple or full family. I’ll suggest the best BHK option.",
    ],

    # 4) Site visit
    "site_visit": [
        "Great, a site visit will give you real clarity. Which day suits you better—weekday evening or weekend?",
        "Happy to arrange a visit. Are you planning to come alone or with family so we can keep enough time?",
        "We can schedule a visit as early as tomorrow, subject to your time. What slot works for you?",
        "If you share your preferred date and time window, I’ll coordinate with the site team and confirm.",
    ],

    # 5) Amenities
    "amenities_query": [
        "Project has modern amenities like clubhouse, gym and kids’ play area. Any specific amenity that’s must-have for you?",
        "We’ve focused on practical amenities—parking, security, lifts, power backup—along with lifestyle features. What do you use most?",
        "There’s a good balance of green spaces and activity zones. Do you prefer more greenery or more sports facilities?",
    ],

    # 6) Possession / readiness
    "possession_query": [
        "We have both under-construction and near-possession options. Are you looking for ready-to-move or can you wait 1–2 years?",
        "Rough timeline is fixed as per approvals. By when are you planning to actually shift in?",
        "Some towers will be ready sooner than others. What is your ideal possession month or year?",
    ],

    # 7) Payment / loan
    "payment_plan_query": [
        "We support both bank loan and self-funded buyers. Are you planning with a home loan?",
        "There are flexible payment plans depending on stage of construction. What down payment can you arrange initially?",
        "Typically buyers keep 10–20% as booking/down payment and rest via loan. Does that fit your plan?",
        "We can connect you with our home-loan partners for eligibility check. Are you okay with that?",
    ],

    # 8) Availability
    "availability_query": [
        "Inventory keeps moving fast. Are you looking for a particular floor or facing so I can check availability?",
        "Corner and garden-facing units are usually limited. Do you have any strong preference?",
        "I’ll check current availability. Do you prefer higher floors or something closer to ground?",
    ],

    # 9) Builder trust
    "builder_trust": [
        "Builder has delivered multiple projects in the city. What matters more to you—timely delivery or long-term maintenance quality?",
        "Happy to share details of completed projects so you can cross-check. Would you like photos, location links or both?",
        "It’s good you’re asking about the builder; that’s smart. Are delays your main concern or quality issues?",
    ],

    # 10) Greeting
    "greeting": [
        "Hi, thanks for reaching out. What would you like to know first—price, location, or flat size?",
        "Hello! I can help you with price, location details, and site visit. What’s on your mind?",
        "Namaste! Are you just exploring options or actively planning to buy within the next few months?",
    ],

    # 11) Thanks / closing
    "thanks": [
        "You’re welcome! If you think of any other questions on price, location or loan, just drop a message here.",
        "Glad to help. When you’re ready, we can plan a quick site visit to give you full clarity.",
        "Happy to assist. Before you decide, it’s always best to see the project once in person.",
    ],

    # 12) Small talk / fallback
    "small_talk": [
        "I’m here to help you with this project—pricing, location, size, loan, anything. What would you like to start with?",
        "Got it. Tell me what matters most to you in a home—budget, location or space? I’ll guide you accordingly.",
        "Sure. Are you just checking options or seriously planning to buy within this year?",
    ],
}


def _pick_template(intent: str) -> str:
    if intent not in TEMPLATES:
        intent = "small_talk"
    return random.choice(TEMPLATES[intent])


def generate_reply(intent: str, user_text: str) -> str:
    """
    Main public function.
    - intent: result from detect_intent(...)
    - user_text: raw message from user (not heavily used yet, but available)
    """
    # For now we mostly use intent; later we can personalize using user_text.
    return _pick_template(intent)
