import os
from typing import Dict, Any, List
from openai import OpenAI

# -------------------------------------------------------------------
# OpenAI Client
# -------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    CLIENT = None
else:
    CLIENT = OpenAI()

# -------------------------------------------------------------------
# Placeholders
# -------------------------------------------------------------------

PLACEHOLDER_URLS = {
    "square": "https://via.placeholder.com/1080",
    "vertical": "https://via.placeholder.com/1080x1920",
    "landscape": "https://via.placeholder.com/1200x628",
}

def _placeholder_asset(format_label: str) -> Dict[str, Any]:
    return {
        "status": "placeholder",
        "format_label": format_label,
        "size": "placeholder",
        "url": PLACEHOLDER_URLS.get(format_label),
        "base64": None,
        "prompt_used": None,
        "error_message": "Placeholder used (image engine not available or failed).",
    }

# -------------------------------------------------------------------
# OpenAI Image Call (CRASH ON FAILURE — INTENTIONAL)
# -------------------------------------------------------------------

def _call_openai_image(prompt: str, size: str) -> Dict[str, Any]:
    if not CLIENT:
        raise RuntimeError("OPENAI_IMAGE_FATAL: OpenAI client not initialized")

    try:
        response = CLIENT.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
        )

        if not response or not response.data:
            raise RuntimeError("OPENAI_IMAGE_FATAL: Empty response from Images API")

        data = response.data[0]

        return {
            "url": getattr(data, "url", None),
            "base64": getattr(data, "b64_json", None),
        }

    except Exception as e:
        raise RuntimeError(f"OPENAI_IMAGE_FATAL: {str(e)}")

# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def generate_sdxl_images(creative_blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
    prompt = creative_blueprint.get("sdxl_prompt") or ""

    if not prompt:
        prompt = "A realistic residential building exterior in India."

    # ----------------------------------------------------------------
    # REALISM ANCHORS (CORRECT FOR OPENAI)
    # ----------------------------------------------------------------

    realism_prefix = (
        "Ultra-realistic architectural photography. "
        "Natural daylight with real-world lighting physics. "
        "Shot on DSLR camera using a 24mm wide-angle lens. "
        "Real construction materials, accurate textures, true-to-life colors. "
        "Looks like a real photograph, not an illustration or CGI render."
    )

    negative = creative_blueprint.get("sdxl_negative_prompt")
    avoid_clause = f" Avoid completely: {negative}." if negative else ""

    final_prompt = f"{realism_prefix} {prompt}.{avoid_clause}"

    outputs: List[Dict[str, Any]] = []

    formats = [
    ("square", "1024x1024"),
    ("vertical", "1024x1536"),
    ("landscape", "1536x1024")
]


    for label, size in formats:
        result = _call_openai_image(final_prompt, size)

        if result.get("url"):
            outputs.append({
                "status": "generated",
                "format_label": label,
                "size": size,
                "url": result["url"],
                "base64": None,
                "prompt_used": final_prompt,
                "error_message": None,
            })
        elif result.get("base64"):
            outputs.append({
                "status": "generated",
                "format_label": label,
                "size": size,
                "url": None,
                "base64": result["base64"],
                "prompt_used": final_prompt,
                "error_message": None,
            })
        else:
            outputs.append(_placeholder_asset(label))

    return outputs

