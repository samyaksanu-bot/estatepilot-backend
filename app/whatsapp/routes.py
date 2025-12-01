import traceback   # <-- TOP of file, once

@router.post("/webhook")
async def receive_message(request: Request):
    try:
        payload = await request.json()

        entry = payload.get("entry", [])
        if not entry:
            return {"status": "ignored"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ignored"}

        value = changes[0].get("value", {})
        if "messages" not in value:
            return {"status": "ignored"}

        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]

        state = get_state(from_number)
        reply = generate_reply(text, state)

        if reply:
            send_whatsapp_message(from_number, reply)

        return {"status": "received"}

    except Exception:
        print("❌ FULL ERROR TRACEBACK:")
        traceback.print_exc()   # <-- THIS exposes the real bug
        return {"status": "error"}

