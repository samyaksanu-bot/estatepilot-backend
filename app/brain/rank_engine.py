# app/brain/rank_engine.py

from app.brain.scoring_rules import (
    INTENT_SCORES,
    NEGATIVE_SIGNALS,
    HOT_SCORE,
    WARM_SCORE
)


def update_score(state: dict, intent: str, text: str):
    # Positive scoring
    score = INTENT_SCORES.get(intent, 0)
    state["score"] += score

    # Negative scoring (basic text-based)
    lowered = text.lower()
    for phrase, penalty in NEGATIVE_SIGNALS.items():
        if phrase in lowered:
            state["score"] += penalty


def update_rank(state: dict):
    if state["score"] >= HOT_SCORE:
        state["rank"] = "HOT"
    elif state["score"] >= WARM_SCORE:
        state["rank"] = "WARM"
    else:
        state["rank"] = "COLD"
