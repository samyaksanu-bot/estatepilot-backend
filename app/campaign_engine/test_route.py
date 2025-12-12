# app/campaign_engine/test_route.py
from fastapi import APIRouter
from app.campaign_engine.image_engine import generate_sdxl_images

router = APIRouter(prefix="/campaign-test", tags=["Temp Test"])

@router.get("/image")
def test_img():
    spec = {
        "sdxl_prompt": "simple flat illustration of a house",
        "sdxl_negative_prompt": "no people, no text",
        "layout": "simple"
    }
    return generate_sdxl_images(spec)
