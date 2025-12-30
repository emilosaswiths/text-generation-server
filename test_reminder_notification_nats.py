import asyncio
import json
import uuid
import time

from nats.aio.client import Client as NATS
from app.config import settings


async def test_reminder_notification():
    # -----------------------------
    # Connect to NATS
    # -----------------------------
    nc = NATS()
    await nc.connect(settings.nats_url)
    print("✅ Connected to NATS")

    subject = settings.nats_reminder_notification_subject

    # -----------------------------
    # Test Payload
    # -----------------------------
    request_id = str(uuid.uuid4())

    payload = {
        "request_id": request_id,
        "title": "Dinner Reservation Reminder",
        "category": "Date Night",
        "location": "Downtown Italian Restaurant",
        "notes": "Dates back to when we first met.",
        "days_offset": 0,
        "partner_name": "Alex",
        "recent_chat_mood": "positive",
        "preferred_tone": "romantic"
    }

    print("📨 Sending reminder notification request...")
    start_time = time.perf_counter()

    # -----------------------------
    # Request → Reply
    # -----------------------------
    msg = await nc.request(
        subject,
        json.dumps(payload).encode(),
        timeout=10
    )

    latency = round(time.perf_counter() - start_time, 3)

    response = json.loads(msg.data.decode())

    print("\n📩 Response received")
    print(json.dumps(response, indent=2))
    print(f"\n⏱ Round-trip latency: {latency}s")

    # -----------------------------
    # Close connection
    # -----------------------------
    await nc.close()


if __name__ == "__main__":
    asyncio.run(test_reminder_notification())
