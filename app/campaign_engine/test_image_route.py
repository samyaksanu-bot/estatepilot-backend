# app/campaign_engine/test_image_route.py

from fastapi import APIRouter, Response
from app.campaign_engine.image_engine import generate_sdxl_images

router = APIRouter(prefix="/campaign", tags=["Image Test"])


@router.get("/test-image")
async def test_image():
    """
    TEMPORARY ROUTE:
    Generates a test SDXL image and returns it as PNG.
    No base64. Direct browser image output.
    """

    # Minimal fake blueprint to test prompt
    fake_blueprint = {
        "sdxl_prompt": "realistic modern residential building, soft daylight, clean elevation, Patna urban setting",
        "sdxl_negative_prompt": "no luxury, no mountains, no water, no skyline, no fake elements",
        "tone_keywords": ["trust", "modern", "neutral"],
        "color_palette": ["white", "beige", "light grey"]
    }

    images = generate_sdxl_images(fake_blueprint)

    if not images or "base64" not in images[0]:
        return {"error": "Image generation failed or placeholder returned."}

    img_bytes = images[0]["base64"]

    return Response(
        content=img_bytes,
        media_type="image/png"
    )
