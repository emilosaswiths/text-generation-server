# app/nats/chat_recommendation_consumer.py

import asyncio
import json
import time

from app.core.logger import get_logger
from app.nats.base_nats_consumer import NATSConnection
from app.services.chat_recommendation_service import (
    generate_chat_recommendation_service
)
from app.core.model_loader import load_model
from app.config import settings

logger = get_logger("nats_chat_recommendation_consumer")


# ---------------------------------------------------------
# PROCESS CHAT RECOMMENDATION MESSAGE (REQUEST–REPLY)
# ---------------------------------------------------------
async def process_chat_message(msg):
    """
    Expected request payload:
    {
        "request_id": "uuid-optional",
        "messages": ["msg1", "msg2", ...]
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

    messages = payload.get("messages")
    request_id = payload.get("request_id")

    if not messages or not isinstance(messages, list):
        await msg.respond(
            json.dumps({"error": "`messages` must be a list"}).encode()
        )
        return

    logger.info(
        f"Processing chat recommendation | "
        f"messages={len(messages)} | request_id={request_id}"
    )

    try:
        start_time = time.perf_counter()

        result = generate_chat_recommendation_service(messages)

        latency = round(time.perf_counter() - start_time, 3)

        response = {
            "request_id": request_id,
            "latency_sec": latency,
            "result": result
        }

        logger.info(
            f"Chat recommendation generated "
            f"(latency={latency}s)"
            f" for request_id={request_id}"
            f"{result}"
        )

        # 🔑 THIS IS THE "RETURN"
        await msg.respond(json.dumps(response).encode())

        logger.info(
            f"Chat recommendation responded "
            f"(latency={latency}s)"
        )

    except Exception as e:
        logger.exception("Chat recommendation failed")
        await msg.respond(
            json.dumps({"error": "internal_error"}).encode()
        )


# ---------------------------------------------------------
# START CORE NATS CONSUMER (REQUEST–REPLY)
# ---------------------------------------------------------
async def start_chat_recommendation_consumer():
    logger.info("Starting Chat Recommendation NATS Worker")

    # 🔑 Load model ONCE for this worker process
    load_model()

    nats = NATSConnection([settings.nats_url])
    await nats.connect()

    subject = settings.nats_chat_recommend_subject

    # 👉 Core NATS (NOT JetStream) for request–reply
    await nats.subscribe_core(
        subject=subject,
        callback=process_chat_message
    )

    logger.info(
        f"Chat Recommendation worker listening on subject: {subject}"
    )

    while True:
        await asyncio.sleep(1)
