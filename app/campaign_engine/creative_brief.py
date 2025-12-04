# app/campaign_engine/graphic_formula.py

def build_graphic_formula(
    creative_brief: dict,
    intent_profile: dict,
    builder_overrides: dict | None = None
) -> dict:
    """
    Final decision layer before any graphic is created.
    Engine recommends.
    Builder can override.
    System warns but never blocks.
    """

    if builder_overrides is None:
        builder_overrides = {}

    # -----------------------------
    # 1. ENGINE RECOMMENDED DEFAULTS
    # -----------------------------
    engine_recommendation = {
        "format": "static",
        "canvas": "1080x1080",
        "primary_visual": creative_brief["visual_layout"],
        "design_tone": creative_brief["design_tone"],
        "color_palette": creative_brief["color_palette"],
        "show_price": True,
        "use_brochure_images": False,
        "cta": "Check availability on WhatsApp"
    }

    # -----------------------------
    # 2. APPLY BUILDER OVERRIDES
    # -----------------------------
    final_recipe = engine_recommendation.copy()
    overrides_used = []
    risk_flags = []

    for key, value in builder_overrides.items():
        if key in final_recipe:
            final_recipe[key] = value
            overrides_used.append(f"{key} overridden to {value}")

    # -----------------------------
    # 3. RISK WARNINGS (NO BLOCKING)
    # -----------------------------

    # Price hidden risk
    if final_recipe.get("show_price") is False:
        risk_flags.append(
            "Hiding price may increase low-intent enquiries and waste sales time."
        )

    # Video-first risk
    if final_recipe.get("format") == "video" and intent_profile["intent_level"] == "high":
        risk_flags.append(
            "High-intent buyers often respond better to clear static visuals than video."
        )

    # Brochure creatives risk
    if final_recipe.get("use_brochure_images") is True:
        risk_flags.append(
            "Brochure visuals are often aspirational and may reduce ad credibility."
        )

    # -----------------------------
    # 4. FINAL OUTPUT OBJECT
    # -----------------------------
    return {
        "engine_recommended": engine_recommendation,
        "builder_overrides_applied": overrides_used,
        "final_visual_recipe": final_recipe,
        "risk_warnings": risk_flags,
        "note": (
            "Builder choices are respected. Suggestions are advisory only "
            "and will improve over time based on performance."
        )
    }
