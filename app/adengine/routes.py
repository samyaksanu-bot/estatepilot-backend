from fastapi import APIRouter
from app.adengine.manifest import create_campaign_manifest

router = APIRouter(prefix="/adengine")

@router.post("/generate")
def generate_campaign(payload: dict):
    manifest = create_campaign_manifest(payload)
    return {"status": "success", "manifest": manifest}
