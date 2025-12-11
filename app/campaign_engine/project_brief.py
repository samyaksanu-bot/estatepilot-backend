def build_project_brief(project: dict) -> dict:
    """
    Minimal version. No AI. No complexity.
    Only normalizes builder input so the rest of Pillar 2 works.
    """

    brief = {
        "project_name": project.get("project_name") or project.get("name"),
        "location": project.get("location"),
        "price_min_lakh": project.get("price_min_lakh"),
        "price_max_lakh": project.get("price_max_lakh"),
        "unit_types": project.get("unit_types", []),
        "floors": project.get("floors"),
        "amenities": project.get("amenities", []),
        "images": project.get("images", []),
        "logo_url": project.get("logo_url"),
        "rera_number": project.get("rera_number"),
    }

    # find missing fields (for later validation)
    missing = [k for k, v in brief.items() if v in (None, "", [])]
    brief["missing_fields"] = missing

    return brief
