import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BRAIN_DIR = BASE_DIR / "brain" / "logic"

def load_brain():
    with open(BRAIN_DIR / "counters.json", "r", encoding="utf-8") as f:
        counters = json.load(f)

    with open(BRAIN_DIR / "scoring.json", "r", encoding="utf-8") as f:
        scoring = json.load(f)

    return counters, scoring
