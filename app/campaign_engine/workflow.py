# app/campaign_engine/workflow.py

from typing import Dict, Any
from app.campaign_engine.project_brief import build_project_brief
from app.campaign_engine.strategy_engine import generate_strategy
from app.campaign_engine.creative_blueprint import generate_creative_blueprint
from app.database import supabase
from app.logger import setup_logger

logger = setup_logger(__name__)


def generate_strategy_only(project_payload: Dict[str, Any]) -> Dict[str, Any]:
    brief = build_project_brief(project_payload)
    strategy = generate_strategy(brief)
    creative_blueprint = generate_creative_blueprint(brief, strategy)

    record = {
        "project_name": brief.get("project_name"),
        "brief": brief,
        "strategy": strategy,
        "creative_blueprint": creative_blueprint,
        "image_status": "NOT_STARTED"
    }

    res = supabase.table("campaigns").insert(record).execute()
    campaign = res.data[0]

    return campaign
