from app.campaign_engine.campaign_preview import generate_campaign_preview
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import traceback
import os

# -------------------------------
# Internal imports (CORE ENGINE)
# -------------------------------
from app.whatsapp.sender import send_whatsapp_message
from app.intent_engine import detect_intent
from app.template_engine import get_template
from app.reply_engine import ai_fallback_reply
from app.state import (
    get_state,
    update_state_with_intent,
    mark_handoff
)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


# ---------------------------------------------------
# 1️⃣ WEBHOOK VERIFICATION (META REQUIREMENT)
# ---------------------------------------------------
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    return PlainTextResponse("Verification failed", status_code=403)


# ---------------------------------------------------
# 2️⃣ INCOMING WHATSAPP MESSAGES
# ---------------------------------------------------
@router.post("/webhook")
async def receive_message(request: Request):
    try:
        payload = await request.json()

        # -------------------------------
        # Basic Meta Payload Guards
        # -------------------------------
        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored"}

        value = changes[0].get("value", {})
        messages = value.get("messages")
        if not messages:
            # delivery / read receipts
            return {"status": "ignored"}

        message = messages[0]

        # Only handle text messages
        if message.get("type") != "text":
            return {"status": "ignored"}

        from_number = message.get("from")
        user_text = message.get("text", {}).get("body", "").strip().lower()
        message_id = message.get("id")

        if not from_number or not user_text:
            return {"status": "ignored"}

        # -------------------------------
        # Load / Initialize State
        # -------------------------------
        state = get_state(from_number)

        # Deduplication (Meta retries)
        if state.get("last_message_id") == message_id:
            return {"status": "duplicate_ignored"}

        state["last_message_id"] = message_id

        # If human already took over, stop bot
        if state.get("handoff_done"):
            return {"status": "agent_handling"}

        # -------------------------------
        # STEP 1️⃣ Intent Detection
        # -------------------------------
        intent = detect_intent(user_text)

        # -------------------------------
        # STEP 2️⃣ State Update + Ranking
        # -------------------------------
        state = update_state_with_intent(from_number, intent)

        # ------------------------------------------------
        # STEP 3️⃣ HUMAN HANDOFF LOGIC (CRITICAL)
        # ------------------------------------------------
        explicit_handoff_keywords = [
            "call me", "call", "agent",
            "visit", "site visit",
            "baat karao", "contact"
        ]

        if (
            state["rank"] == "hot"
            or intent == "site_visit"
            or any(k in user_text for k in explicit_handoff_keywords)
        ):
            if not state.get("handoff_done"):
                send_whatsapp_message(
                    from_number,
                    "Perfect 👍 I’ll have our advisor call you shortly to confirm the details."
                )
                mark_handoff(from_number)

            return {"status": "handoff"}

        # ----------------------------------------
        # STEP 4️⃣ TEMPLATE RESPONSE
        # ----------------------------------------
        reply_text = get_template(intent, state)

        # ----------------------------------------
        # STEP 5️⃣ AI FALLBACK (ONLY IF NEEDED)
        # ----------------------------------------
        if not reply_text:
            reply_text = ai_fallback_reply(user_text)

        # ----------------------------------------
        # STEP 6️⃣ SEND FINAL MESSAGE
        # ----------------------------------------
        if reply_text:
            send_whatsapp_message(from_number, reply_text)

        return {"status": "received"}

    except Exception:
        print("❌ WhatsApp webhook error")
        traceback.print_exc()
        return {"status": "error"}
        
@router.post("/debug/campaign-preview")
async def debug_campaign_preview(project: dict):
    """
    DEBUG: Live Campaign Preview UI
    Returns a human-readable ad preview for builders.
    """

   # SAFE IMPORTS — ONLY EXISTING FILES
from app.campaign_engine.campaign_preview_ui import build_campaign_preview_ui
from app.campaign_engine.template_selector import select_visual_template
from app.campaign_engine.static_image_generator import generate_static_image_spec
from app.campaign_engine.template_renderer import render_static_template


    print("✅ Live Campaign Preview UI Triggered")

    # --- 1. campaign brain ---
    strategy = decide_campaign_strategy(project)
    intent_profile = build_buyer_intent_profile(project, strategy)
    creative_brief = generate_creative_brief(project, intent_profile)

    # --- 2. builder overrides (empty for now) ---
    builder_overrides = {}

    # --- 3. graphic decision ---
    graphic_formula = build_graphic_formula(
        creative_brief=creative_brief,
        intent_profile=intent_profile,
        builder_overrides=builder_overrides
    )

    # --- 4. template selection ---
    template_selection = select_visual_template(graphic_formula)

    # --- 5. static image spec ---
    image_spec = generate_static_image_spec(
        graphic_formula=graphic_formula,
        template_selection=template_selection,
        project=project
    )

    # --- 6. render payload (no AI, template only) ---
    render_payload = render_static_template(
        image_spec=image_spec,
        template_selection=template_selection,
        project_assets={}
    )

    # --- 7. final HUMAN-READABLE PREVIEW ---
    preview_ui = build_campaign_preview_ui(
        project=project,
        graphic_formula=graphic_formula,
        template_selection=template_selection,
        render_payload=render_payload
    )

    return preview_ui
