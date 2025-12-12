# app/campaign_engine/image_engine.py

import os
from typing import Dict, Any, List
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing in environment variables")

client = OpenAI(api_key=OPENAI_API_KEY)


def _generate_single_image(prompt: str, negative_prompt: str, size: str) -> Dict[str, Any]:
    """
    Calls GPT-Image-1 to generate a single image.
    Enforces negative prompts to prevent hallucinated luxury or false scenery.
    """

    full_prompt = (
        f"{prompt}\n\n"
        f"STRICT NEGATIVE LOGIC:\nDo NOT include: {negative_prompt}\n"
        "No luxury exaggeration. No invented mountain views. No beaches. "
        "No malls. No celebrity models. Only realistic neutral real-estate visuals."
    )

    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=full_prompt,
            size=size,
            n=1
        )

        image_url = response.data[0].url if response and response.data else None

        return {
            "status": "success" if image_url else "failed",
            "prompt_used": full_prompt,
            "size": size,
            "url": image_url
        }

    except Exception as e:
        return {
            "status": "error",
            "size": size,
            "url": None,
            "error_message": str(e),
            "prompt_used": full_prompt
        }


def generate_sdxl_images(creative_blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates multiple SDXL-like images using GPT-Image-1 based on creative blueprint.
    Output used by workflow orchestrator.
    """

    prompt = creative_blueprint.get("sdxl_prompt", "")
    negative = creative_blueprint.get("sdxl_negative_prompt", "")

    if not prompt:
        return [{
            "status": "error",
            "error_message": "Creative blueprint missing 'sdxl_prompt'.",
            "url": None
        }]

    # Meta Ad Formats
    formats = [
        ("1080x1080", "1080x1080"),   # Square Feed
        ("1080x1920", "1080x1920"),   # Stories/Reels
        ("1200x628", "1200x628")      # Landscape Ads
    ]

    results = []

    for label, size in formats:
        img = _generate_single_image(
            prompt=prompt,
            negative_prompt=negative,
            size=size
        )
        img["format_label"] = label
        results.append(img)

    return results
