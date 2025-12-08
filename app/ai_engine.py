import os
from openai import OpenAI
from app.state import get_state, append_history

# Load API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def call_ai(phone: str, user_text: str) -> str:
    """
    AI conversation handler for WhatsApp.
    - GPT-4o-mini
    - Project-aware
    - Language-aware
    - Persuasive but short
    - Real estate ONLY
    - Emotion-aware
    """

    state = get_state(phone)
    # =====================================================
# GLOBAL STOP MODE: NO MORE QUALIFICATION QUESTIONS
# =====================================================
if state.get("stop_questions") is True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
You are Pragiti, a real estate assistant.

User has either:
- been qualified, OR
- requested a call, OR
- shown irritation, OR
- skipped funnel questions

RULE:
Stop ALL qualification or probing questions.

Your replies must:
- answer only what user asks
- be short, friendly and factual
- no nudging or pushing
- no new qualification questions
- assist with availability, pricing, details or site visit

If user asks irrelevant or non-real-estate topics:
Reply: "I assist only with this project information, pricing or site visits."
"""},
            {"role": "user", "content": user_text}
        ],
        temperature=0.4,
        max_tokens=100
    )

    reply = response.choices[0].message.content.strip()

    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)

    return reply
    project = state.get("project_context")
    history = state.get("conversation_history", [])
    rank = state.get("rank")

    # ---------------- LANGUAGE DETECT -----------------
    # Simple heuristic: detect language from user message
    def detect_language(t: str) -> str:
        hindi_words = ["kya", "kab", "kaise", "ghar", "zameen", "flat",
                       "booking", "visit", "kal", "aaj", "weekend",
                       "paisa", "loan", "possession", "area", "ke", "ki"]
        hits = sum(1 for w in hindi_words if w in t.lower())

        if hits >= 4:
            return "hindi"
        if 2 <= hits < 4:
            return "hinglish"
        return "english"

    detected_lang = detect_language(user_text)
    state["language"] = detected_lang  # store for continuity
    # =====================================
    # SITE VISIT TRIGGER DURING AI MODE
    # =====================================
text_l = user_text.lower()

visit_triggers = [
    "visit", "site visit", "see property", "property visit",
    "come and see", "want to see", "want to visit", "schedule visit",
    "plan a visit", "plan site", "book visit", "arrange visit",
    "meet at site", "location visit", "show me the property"
]

if any(v in text_l for v in visit_triggers):
    state["qualified"] = True
    state["stop_questions"] = True
    from app.state import mark_handoff
    mark_handoff(phone)

    reply = (
        "Great — I’ll arrange a call with our project expert who will guide you with "
        "location, availability and site planning.\n"
        "Please share your preferred time."
    )

    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)
    return reply


    # --------------- SAFETY FILTER --------------------
    if any(w in user_text.lower() for w in [
        "who are you",
        "real name",
        "where do you live",
        "who made you",
        "your email",
        "your phone number",
        "personal details",
        "login details",
        "password",
        "openai account"
    ]):
        reply = (
            "I am Pragiti, your property assistant. I help only with project "
            "details, pricing, availability and site visits. I don’t share personal or unrelated data."
        )
        append_history(phone, "bot", reply)
        return reply

    # If no project info, fallback
    if not project:
        reply = (
            "Tell me which project you are exploring, and I’ll guide you with pricing, availability and visit planning."
        )
        append_history(phone, "bot", reply)
        return reply


    # ---------------------- SYSTEM PROMPT -----------------------

    system_prompt = f"""
You are PRAGITI, a HUMAN-LIKE real estate sales assistant.

STRICT RULES:
1) ALWAYS answer in the SAME language as LAST USER MESSAGE:
   english / hindi / hinglish. Detect automatically.

2) Use ONLY the following verified project details:
   NAME: {project.get("name")}
   LOCATION: {project.get("location")}
   PRICE RANGE: {project.get("price_range")}
   UNIT TYPES: {project.get("unit_types")}
   STATUS: {project.get("status")}
   USP / AMENITIES: {project.get("usp")}

3) NO HALLUCINATION:
   If a detail is unknown, say:
   "I will confirm this on call with our advisor."
   NEVER invent approvals, builder history, distances, EMI partners or future developments.

4) REAL ESTATE ONLY:
   If user asks ANYTHING unrelated to this project (tech, jokes, gossip, politics, philosophy, math, personal info),
   reply politely:
   "I assist only with this real estate project, pricing, availability and site visits."

5) ANSWER STYLE:
   - MAX 2–4 sentences total
   - Short factual answer FIRST
   - THEN soft persuasive nudge (example: “A short visit gives clarity with no obligation.”)
   - Friendly tone, not robotic
   - Human natural phrasing
   - Use low tokens
   - Avoid bullet lists unless necessary

6) SHORT ANSWERS RULE:
   If a VERY SHORT answer is sufficient, KEEP IT SHORT.
   Example:
       USER: “Is this project in Patna?”
       ANSWER: “Yes, it is located in Saguna More, Patna. If you like, I can help you plan a short visit.”

7) EMOTION + FRUSTRATION:
   If user sounds irritated, confused, upset or hesitant:
       - Calm them
       - Avoid repeating same question
       - Reduce pressure
       - Propose simple forward steps

8) INTERNAL QUALIFICATION:
   Without showing it explicitly to user:
       - If user gives budget → treat as qualification data
       - If user asks serious questions → increase seriousness
       - If user expresses urgency → treat as HOT
       - If user avoids sharing details → continue softly, do not interrogate
       - If user asks to talk to agent → recommend handoff

   DO NOT mention scoring, qualification, or rank.

9) SALES INTELLIGENCE:
   Every answer should help nudge user:
       - toward clarity
       - toward sharing a detail naturally
       - toward scheduling a site visit
       - without pressure or interrogation
"""


    # ---------------- MESSAGE BUILD ----------------

    messages = [{"role": "system", "content": system_prompt}]

    # Add trimmed chat history (last 6 exchanges)
    for h in history[-6:]:
        messages.append({
            "role": "assistant" if h["from"] == "bot" else "user",
            "content": h["text"]
        })

    # Add latest user message
    messages.append({"role": "user", "content": user_text})


    # ---------------- AI CALL ----------------

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.55,
        max_tokens=130
    )
# =====================================================
# GLOBAL STOP MODE: NO MORE QUALIFICATION QUESTIONS
# =====================================================
if state.get("stop_questions") is True:
    # AI reply should NOT ask any more probing questions
    # Only answer user queries politely and SHORT
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
You are Pragiti, a real estate assistant.

RULE:
User has completed qualification OR shown irritation.
STOP asking qualification questions.

Your replies must:
- be short, factual and polite
- no funnel questions
- no nudging
- no persuasion
- assist only with information, availability, or support
- if user asks for call/visit, politely confirm
"""},
            {"role": "user", "content": user_text}
        ],
        temperature=0.4,
        max_tokens=90
    )

    reply = response.choices[0].message.content.strip()
    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)
    return reply

    reply = response.choices[0].message.content.strip()

    # ---------------- STORE HISTORY ----------------

    append_history(phone, "user", user_text)
    append_history(phone, "bot", reply)

    return reply
