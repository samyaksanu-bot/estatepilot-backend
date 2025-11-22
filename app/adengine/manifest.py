from app.adengine.generator import generate_ad_copy, generate_creative_instructions
from app.adengine.targeting import build_targeting

def create_campaign_manifest(project):
    ad_copy = generate_ad_copy(project)
    creative = generate_creative_instructions(project)
    targeting = build_targeting(project)

    return {
        "project": project,
        "ad_copy": ad_copy,
        "creative_plan": creative,
        "targeting": targeting,
        "objective": "LEAD_GENERATION",
        "budget_per_day": 500,
        "placements": ["facebook_feeds", "instagram_feeds", "stories"]
    }
