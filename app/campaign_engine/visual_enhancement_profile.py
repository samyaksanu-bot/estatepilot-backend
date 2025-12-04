# app/campaign_engine/visual_enhancement_profile.py

def build_visual_enhancement_profile(
    intent_profile: dict,
    graphic_formula: dict,
    template_selection: dict
) -> dict:
    """
    Defines what AI is ALLOWED to enhance and what is FORBIDDEN.
    AI decorates facts. AI never invents facts.
    """

    intent_level = intent_profile["intent_level"]
    property_type = intent_profile["property_type"]

    # -----------------------------
    # 1. ALLOWED AI ENHANCEMENTS
    # -----------------------------
    allowed = {
        "background_environment": True,
        "sky_and_lighting": True,
        "color_grading": True,
        "atmosphere_mood": True,
        "generic_lifestyle_elements": intent_level != "high"
    }

    # -----------------------------
    # 2. FORBIDDEN AI GENERATION
    # -----------------------------
    forbidden = [
        "project_building_creation",
        "site_layout_generation",
        "floor_plan_generation",
        "exact_location_map",
        "amenities_not_confirmed",
        "luxury_claims_not_provided",
        "people_faces_or_celebrities"
    ]

    # -----------------------------
    # 3. STYLE GUIDANCE (NOT FACTUAL)
    # -----------------------------
    if property_type == "plot":
        style_guidance = {
            "visual_style": "open_landscape",
            "mood": "trustworthy, calm, clear",
            "lighting": "natural daylight",
            "environment": "roads, greenery, open sky (generic)"
        }
    else:
        style_guidance = {
            "visual_style": "modern_residential",
            "mood": "comfortable, aspirational but realistic",
            "lighting": "soft daylight",
            "environment": "clean surroundings, greenery (non-specific)"
        }

    # -----------------------------
    # 4. STRICT AI INSTRUCTION (FINAL)
    # -----------------------------
    ai_instruction = (
        "Enhance only the visual presentation without inventing buildings, "
        "layouts, locations, or amenities. Use non-specific, generic "
        "real-estate visuals purely for aesthetic support."
    )

    return {
        "allowed_ai_enhancements": allowed,
        "forbidden_ai_generation": forbidden,
        "style_guidance": style_guidance,
        "ai_instruction": ai_instruction,
        "engine_note": (
            "AI is restricted to aesthetic enhancement only. "
            "All factual elements remain engine-controlled."
        )
    }
