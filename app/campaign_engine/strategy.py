import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_strategy(brief: dict) -> dict:
    """
    GPT-4.0 powered real estate strategy engine.
    STRICT: no hallucination of factual data.
    """
    system_prompt = """
You are ESTATEPILOT STRATEGY ENGINE — an expert real-estate Meta Ads strategist.
Your job is to create a COMPLETE, HIGH-INTENT, LOW-JUNK campaign strategy.

NON-NEGOTIABLE RULES:
- Never invent amenities, prices, RERA, or factual data.
- Only use the factual fields provided in the Project Brief.
- If a field is missing, ignore it — do NOT fabricate it.

YOUR OUTPUT MUST INCLUDE:
1. Buyer Persona (ICP)
2. Target Radius (3–5 km default unless location missing)
3. Age Filter (28–55 unless price → luxury)
4. Behavior Filters (Likely to Move, Home Loan Intent)
5. Exclusions (agents, brokers, renters)
6. Placement Selection (Feeds + Reels ONLY)
7. Budget Logic (simple recommendation)
8. CTA Selection
9. High-Intent Lead Form Structure:
    - budget question
    - timeline question
    - unit preference
    - self-use vs investment
10. Key Messaging Pillars
11. WhatsApp Bot Notes:
    - what to emphasize
    - what to avoid
    - qualification priorities

IMPORTANT:
- Output in CLEAN JSON. No explanation text.
"""

    user_prompt = f"""
PROJECT BRIEF:
{brief}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    try:
        content = response.choices[0].message.content
        return eval(content) if content.strip().startswith("{") else {"error": "Invalid JSON"}
    except Exception:
        return {"error": "Strategy generation failed"}
