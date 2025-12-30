# app/nats/reminder_notification_consumer.py

import asyncio
import json
import time

from app.core.logger import get_logger
from app.nats.base_nats_consumer import NATSConnection
from app.services.reminder_notification_service import (
    generate_reminder_notification_service
)
from app.core.model_loader import load_model
from app.config import settings

logger = get_logger("nats_reminder_notification_consumer")


# ---------------------------------------------------------
# PROCESS REMINDER NOTIFICATION MESSAGE (REQUEST–REPLY)
# ---------------------------------------------------------
async def process_reminder_message(msg):
    """
    Expected request payload:
    {
        "request_id": "uuid-optional",
        "title": "First Meet",
        "category": "anniversary",
        "location": "Cafe Coffee Day, Bangalore",
        "notes": "We talked for hours and felt special",
        "days_offset": 0,
        "partner_name": "Riya",
        "recent_chat_mood": "positive",
        "preferred_tone": "romantic"
    }
    """
    try:
        payload = json.loads(msg.data.decode())
    except json.JSONDecodeError:
        logger.warning("Invalid JSON received")
        await msg.respond(
            json.dumps({"error": "invalid_json"}).encode()
        )
        return

    request_id = payload.get("request_id")

    title = payload.get("title")
    category = payload.get("category")
    location = payload.get("location", "")
    notes = payload.get("notes", "")
    days_offset = payload.get("days_offset")
    partner_name = payload.get("partner_name")

    recent_chat_mood = payload.get("recent_chat_mood", "neutral")
    preferred_tone = payload.get("preferred_tone", "romantic")

    # -----------------------------
    # Basic validation
    # -----------------------------
    if not title or not category or partner_name is None or days_offset is None:
        await msg.respond(
            json.dumps({"error": "missing_required_fields"}).encode()
        )
        return

    logger.info(
        f"Processing reminder notification | "
        f"title={title} | days_offset={days_offset} | request_id={request_id}"
    )

    try:
        start_time = time.perf_counter()

        result = generate_reminder_notification_service(
            title=title,
            category=category,
            location=location,
            notes=notes,
            days_offset=days_offset,
            partner_name=partner_name,
            recent_chat_mood=recent_chat_mood,
            preferred_tone=preferred_tone,
        )

        latency = round(time.perf_counter() - start_time, 3)

        response = {
            "request_id": request_id,
            "latency_sec": latency,
            "notification_text": result
        }

        logger.info(f"Generated reminder notification: {result}")

        logger.info(
            f"Reminder notification generated "
            f"(latency={latency}s) "
            f"for request_id={request_id}"
        )

        # 🔑 REQUEST–REPLY RESPONSE
        await msg.respond(json.dumps(response).encode())

        logger.info(
            f"Reminder notification responded "
            f"(latency={latency}s)"
        )

    except Exception:
        logger.exception("Reminder notification generation failed")

        await msg.respond(
            json.dumps({"error": "internal_error"}).encode()
        )


# ---------------------------------------------------------
# START CORE NATS CONSUMER (REQUEST–REPLY)
# ---------------------------------------------------------
async def start_reminder_notification_consumer():
    logger.info("Starting Reminder Notification NATS Worker")

    # 🔑 Load model ONCE per worker
    load_model()

    nats = NATSConnection([settings.nats_url])
    await nats.connect()

    subject = settings.nats_reminder_notification_subject

    # 👉 Core NATS request–reply
    await nats.subscribe_core(
        subject=subject,
        callback=process_reminder_message
    )

    logger.info(
        f"Reminder Notification worker listening on subject: {subject}"
    )

    while True:
        await asyncio.sleep(1)
