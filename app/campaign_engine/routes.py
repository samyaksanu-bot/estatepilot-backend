from fastapi import APIRouter
from app.campaign_engine.workflow import generate_full_campaign_plan

router = APIRouter(prefix="/campaign", tags=["Campaign Engine"])


@router.post("/generate")
async def generate_campaign(project_payload: dict):
    """
    MASTER ENDPOINT for EstatePilot Pillar 2.

    - Validates builder input
    - Builds Project Brief
    - Generates Strategy (GPT-4.0)
    - Generates Creative Blueprint (GPT-4.0)
    - Generates SDXL visuals
    - Builds final Meta Ads step-by-step setup
    - Prepares WhatsApp Bot context package

    SAFE: Does NOT publish ads. Builder will publish manually.
    """
    return generate_full_campaign_plan(project_payload)
