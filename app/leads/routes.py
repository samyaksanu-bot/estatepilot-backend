from fastapi import APIRouter
from app.leads.service import create_lead, get_leads, update_lead_score

router = APIRouter(prefix="/leads")

@router.post("/")
def new_lead(payload: dict):
    lead = create_lead(payload)
    return {"status": "created", "lead": lead}

@router.get("/{tenant_id}")
def list_leads(tenant_id: str):
    return get_leads(tenant_id)

@router.put("/{lead_id}/score")
def score_update(lead_id: str, payload: dict):
    return update_lead_score(lead_id, payload["score"])
