# app/whatsapp/flow.py

from app.state import get_state


def detect_intent(text: str) -> str:
    """
    Very simple keyword-based intent detection.
    We don't need GPT here yet.
    """
    t = text.lower()

    if any(w in t for w in ["price", "budget", "cost", "rate"]):
        return "price"
    if any(w in t for w in ["location", "where", "area", "site"]):
        return "location"
    if any(w in t for w in ["available", "availability", "possession", "ready to move"]):
        return "availability"
    if any(w in t for w in ["visit", "see", "come", "site visit", "dekna", "dekhna"]):
        return "visit"
    if any(w in t for w in ["more", "details", "detail", "project", "information", "info"]):
        return "overview"

    return "unknown"


def extract_budget(text: str) -> str | None:
    """
    For now we just store whatever user typed as budget text.
    Later we can parse numbers properly.
    """
    t = text.strip()
    if len(t) < 2:
        return None
    return t


def route_message(phone: str, text: str) -> str:
    """
    Core conversation flow.

    ONE job: take (phone, text) → update state → return reply.
    No WhatsApp API calls here.
    """
    state = get_state(phone)
    step = state["step"]

    intent = detect_intent(text)
    state["last_intent"] = intent

    # 1) INTRO STEP – user just came from ad
    if step == "intro":
        state["step"] = "budget"
        return (
            "Namaste! 😊 Main project ki team se EstatePilot bot hoon.\n"
            "Short me bolun toh yeh project me plots / flats available hain with legal clearance and basic amenities.\n\n"
            "Sabse pehle, approx budget range bataoge? Jaise 40–50L, 80–90L, ya 1–1.2Cr."
        )

    # 2) BUDGET STEP
    if step == "budget":
        budget = extract_budget(text)
        if not budget and intent != "price":
            return (
                "Bas approx batao, strict nahi hai. Example: 40–50L, 80–90L, ya 1–1.2Cr.\n"
                "Is range se main aapko sahi options filter kar sakta hoon."
            )

        if budget:
            state["budget"] = budget
            state["step"] = "location"
            return (
                f"Perfect, approx budget '{budget}' note kar liya. ✅\n\n"
                "Ab batao, kaunsa area ya location prefer kar rahe ho? "
                "City ke andar koi specific side (east / west / main road ke paas, etc.)?"
            )

    # 3) LOCATION STEP
    if step == "location":
        # If user says anything meaningful, accept as location preference
        if len(text.strip()) < 3 and intent != "location":
            return (
                "Thoda sa detail me batao, kaunsi side ya area soch rahe ho?\n"
                "Example: 'Ring road ke paas', 'Airport side', ya specific locality ka naam."
            )

        state["location"] = text.strip()
        state["step"] = "visit"
        return (
            f"Got it, location preference note kar li: '{state['location']}'. ✅\n\n"
            "Aapko site visit kab comfortable rahega? "
            "Main builder ki team se call + location share karwa dunga.\n"
            "Options: Aaj, Kal, Weekend, ya koi specific date/time likh sakte ho."
        )

    # 4) VISIT STEP
    if step == "visit":
        # Whatever user says, treat as visit preference
        state["visit_time"] = text.strip()
        state["qualified"] = True
        state["step"] = "done"

        return (
            "Awesome, site visit preference note ho gaya. ✅\n\n"
            "Ab next step:\n"
            "• Project expert aapko call karega\n"
            "• Exact location + landmark WhatsApp par aayega\n"
            "• Visit ke time pe aapko personally project dikhaenge\n\n"
            "Agar price, payment plan, ya availability ke bare me koi specific sawal hai "
            "toh yahin puch sakte ho, main short and clear answer dunga."
        )

    # 5) DONE STEP – conversation already qualified
    if step == "done":
        # Keep it simple, avoid loop
        if intent == "price":
            return (
                "Price details phone par thoda customise karke hi batayenge, "
                "taaki aapke budget ke hisaab se right option mile.\n"
                "Team ka call aayega jaldi. Tab tak agar koi specific question hai, "
                "jaise 'minimum booking amount' ya 'EMI option', toh yahan puch lo."
            )
        if intent == "location":
            return (
                "Location: site visit se just pehle aapko Google Maps location share hogi, "
                "taaki easily reach ho sake. Area roughly wahi hai jo aapne mention kiya tha.\n"
                "Baaki exact landmark call par explain kar denge."
            )

        return (
            "Team aapka case already pick kar chuki hai. Call agar miss ho jaye toh "
            "yahan bata dena, main follow-up trigger kara dunga. 🙂"
        )

    # Fallback (should rarely hit)
    state["step"] = "intro"
    return (
        "Main thoda confuse ho gaya. Chalo fir se start karte hain.\n"
        "Aap approx budget range batao, jaise 40–50L, 80–90L, ya 1–1.2Cr."
    )
