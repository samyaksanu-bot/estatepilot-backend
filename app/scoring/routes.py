from fastapi import APIRouter
from app.scoring.engine import calculate_score

router = APIRouter(prefix="/scoring")

@router.post("/")
def score_lead(payload: dict):
    score = calculate_score(payload)
    return {"score": score}
