# app/campaign_engine/image_engine.py
"""
Production-ready image engine for EstatePilot Pillar-2.

Function:
    generate_sdxl_images(image_spec: dict) -> List[dict]

Behavior:
- Uses OpenAI Images API (model "gpt-image-1") to generate images in three sizes:
    - 1080x1080 (square)      -> "square"
    - 1080x1920 (vertical)    -> "vertical"
    - 1200x628 (landscape)    -> "landscape"
- If OPENAI_API_KEY is missing or generation fails, returns placeholder images
  (keeps pipeline functional during testing).
- Each returned dict contains:
    - status: "success"|"failed"|"error"
    - format_label: "square"|"vertical"|"landscape"
    - size: "<WxH>"
    - url: public URL (or None)
    - prompt_used: final prompt sent
    - error_message: optional
"""

import os
import time
from typing import Dict, Any, List

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Optional override: set IMAGE_ENGINE_MODE="stub" to ALWAYS return placeholders
IMAGE_ENGINE_MODE = os.getenv("IMAGE_ENGINE_MODE", "").lower()  # "stub" to force placeholders

# Placeholder generator (keeps API-independent pipeline running)
def _placeholder_asset(format_label: str, size: str) -> Dict[str, Any]:
    # Use via.placeholder.com for quick placeholders
    dims = size.split("x")
    width = dims[0]
    return {
        "status": "placeholder",
        "format_label": format_label,
        "size": size,
        "url": f"https://via.placeholder.com/{width}",
        "prompt_used": None,
        "error_message": "Placeholder used (no image engine available)."
    }


# Internal single-image generator wrapper
def _call_openai_image(prompt: str, negative_prompt: str, size: str, model: str = "gpt-image-1") -> Dict[str, Any]:
    """
    Calls OpenAI images.generate and returns a minimal dict.
    If OpenAI client is not available or fails, raises Exception.
    """
    if not OPENAI_API_KEY or OpenAI is None:
        raise RuntimeError("OpenAI Images API not configured in this environment.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build the combined prompt with negative guidance
    full_prompt = (
        f"{prompt}\n\nNEGATIVE GUIDANCE: {negative_prompt}\n"
        "Strict: Do NOT invent facts or features. No celebrity models. No mountains/beaches/malls. "
        "Keep composition realistic for real-estate ad use. Place a small readable price overlay if provided."
    )

    # tolerant retry wrapper (2 tries)
    for attempt in (1, 2):
        try:
            resp = client.images.generate(
                model=model,
                prompt=full_prompt,
                size=size,
                n=1
            )
            # Expect resp.data[0].url (or handle base64 in future)
            image_url = None
            try:
                image_url = resp.data[0].url  # typical SDK response
            except Exception:
                # Attempt alternative shapes (some SDKs return b64)
                image_url = None

            return {
                "status": "success" if image_url else "failed",
                "size": size,
                "url": image_url,
                "prompt_used": full_prompt,
                "error_message": None if image_url else "No url returned by image API"
            }
        except Exception as e:
            # short backoff before retry
            if attempt == 1:
                time.sleep(0.8)
                continue
            # final failure
            raise e


def generate_sdxl_images(image_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Public function called by workflow.py.

    Input: image_spec produced by static_image_generator (dict).
    Output: list of image asset dicts (one per format).
    """

    # If user explicitly force-stub mode, return placeholders
    if IMAGE_ENGINE_MODE == "stub":
        return [
            _placeholder_asset("square", "1080x1080"),
            _placeholder_asset("vertical", "1080x1920"),
            _placeholder_asset("landscape", "1200x628")
        ]

    # Validate input
    if not isinstance(image_spec, dict):
        return [
            _placeholder_asset("square", "1080x1080")
        ]

    prompt = image_spec.get("sdxl_prompt") or ""
    negative = image_spec.get("sdxl_negative_prompt") or ""

    # If no prompt present, return placeholders so pipeline doesn't break
    if not prompt:
        return [
            _placeholder_asset("square", "1080x1080")
        ]

    formats = [
        ("square", "1080x1080"),
        ("vertical", "1080x1920"),
        ("landscape", "1200x628")
    ]

    results: List[Dict[str, Any]] = []

    # If no OpenAI key, fallback to placeholders
    if not OPENAI_API_KEY or OpenAI is None:
        for fmt, size in formats:
            results.append(_placeholder_asset(fmt, size))
        return results

    # Attempt to generate each image
    for fmt, size in formats:
        try:
            resp = _call_openai_image(prompt=prompt + f" Aspect ratio: {size}. Use layout: {image_spec.get('layout','safe')}.",
                                      negative_prompt=negative,
                                      size=size)
            # Normalize response
            results.append({
                "status": resp.get("status", "failed"),
                "format_label": fmt,
                "size": size,
                "url": resp.get("url"),
                "prompt_used": resp.get("prompt_used"),
                "error_message": resp.get("error_message")
            })
        except Exception as exc:
            # Logable error detail returned but do not raise — pipeline must continue
            results.append({
                "status": "error",
                "format_label": fmt,
                "size": size,
                "url": None,
                "prompt_used": prompt,
                "error_message": str(exc)
            })

    # If all failed, ensure at least placeholders
    all_failed = all(r.get("status") != "success" for r in results)
    if all_failed:
        return [
            _placeholder_asset("square", "1080x1080"),
            _placeholder_asset("vertical", "1080x1920"),
            _placeholder_asset("landscape", "1200x628")
        ]

    return results

