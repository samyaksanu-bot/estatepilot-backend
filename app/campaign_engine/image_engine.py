# app/campaign_engine/image_engine.py

import os
import base64
from typing import Dict, Any, List

# OpenAI client (your project uses openai.OpenAI)
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # will fall back to placeholder mode
    CLIENT = None
else:
    CLIENT = OpenAI()

PLACEHOLDER_URLS = {
    "square": "https://via.placeholder.com/1080",
    "vertical": "https://via.placeholder.com/1080x1920",
    "landscape": "https://via.placeholder.com/1200x628"
}

def _safe_str(v):
    return "" if v is None else str(v)

def _to_base64_from_openai_result(item: Dict[str, Any]) -> str:
    # New OpenAI images.generate returns b64_json in many SDKs
    b64 = item.get("b64_json") or item.get("b64") or item.get("b64_string")
    if b64:
        return b64
    # older clients may return url only
    return None

def _placeholder_asset(format_label: str):
    return {
        "status": "placeholder",
        "format_label": format_label,
        "size": "placeholder",
        "url": PLACEHOLDER_URLS.get(format_label, "https://via.placeholder.com/1080"),
        "base64": None,
        "prompt_used": None,
        "error_message": "Placeholder used (image engine not available or failed)."
    }

def _call_openai_image(prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
    """
    Calls OpenAI image generation. Returns dict with possible keys:
    - 'base64' (str) : base64 encoded PNG
    - 'url' (str) : publicly accessible url (if returned by provider)
    - 'error' (str) : error message
    """
    if not CLIENT:
        return {"error": "OPENAI API key missing; client not initialized."}

    try:
        # using OpenAI python client images.generate
        resp = CLIENT.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size
        )
        # resp.data is list-like
        data0 = resp.data[0] if resp and getattr(resp, "data", None) else (resp["data"][0] if isinstance(resp, dict) and "data" in resp else None)
        if not data0:
            return {"error": "empty response from OpenAI images.generate", "raw": resp}

        # try to extract base64
        b64 = None
        # some SDKs store b64_json in data
        if isinstance(data0, dict):
            b64 = _to_base64_from_openai_result(data0)
            url = data0.get("url")
        else:
            # dataclass-like object
            # try attributes
            b64 = getattr(data0, "b64_json", None) or getattr(data0, "b64", None) or getattr(data0, "url", None)
            url = getattr(data0, "url", None) if hasattr(data0, "url") else None

        return {"base64": b64, "url": url}
    except Exception as e:
        return {"error": str(e)}

def generate_sdxl_images(creative_blueprint: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns list of image assets for square, vertical, landscape.
    Each item: {status, format_label, size, url, base64, prompt_used, error_message}
    """
    prompt = _safe_str(creative_blueprint.get("sdxl_prompt") or creative_blueprint.get("prompt") or "")
    negative = _safe_str(creative_blueprint.get("sdxl_negative_prompt") or creative_blueprint.get("negative_prompt") or "")

    # defensive default prompts
    if not prompt:
        prompt = "realistic architectural visual of a residential building, neutral daylight, no luxury, no invented amenities."

    # Build final prompt; keep negative separate for engines that accept negative
    # ---- REALISM ANCHORS (GLOBAL) ----
     realism_prefix = (
    "Ultra-realistic architectural photography. "
    "Natural daylight with real-world lighting physics. "
    "Shot on DSLR camera, 24mm wide-angle lens. "
    "Real construction materials, accurate textures, true-to-life colors. "
    "Looks like a real photograph, not an illustration or CGI render."
)

# ---- NEGATIVE ELEMENTS (PLAIN ENGLISH) ----
avoid_clause = ""
if negative:
    avoid_clause = f" Avoid the following elements completely: {negative}."

# ---- FINAL PROMPT (OPENAI-COMPATIBLE) ----
final_prompt = f"{realism_prefix} {prompt}.{avoid_clause}"

    outputs = []

    # sizes mapping
    formats = [
        ("square", "1024x1024"),
        ("vertical", "1024x1792"),
        ("landscape", "1792x1024")
    ]

    for label, size in formats:
        result = _call_openai_image(final_prompt, size=size)
        if result.get("error"):
            outputs.append(_placeholder_asset(label))
            continue

        b64 = result.get("base64")
        url = result.get("url")
        if b64:
            # return base64 string (not decoded) so higher layer can decode if needed
            outputs.append({
                "status": "generated",
                "format_label": label,
                "size": size,
                "url": None,
                "base64": b64,
                "prompt_used": final_prompt,
                "error_message": None
            })
        elif url:
            outputs.append({
                "status": "generated",
                "format_label": label,
                "size": size,
                "url": url,
                "base64": None,
                "prompt_used": final_prompt,
                "error_message": None
            })
        else:
            outputs.append(_placeholder_asset(label))

    return outputs

