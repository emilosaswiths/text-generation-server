import asyncio
import json
import time

from nats.aio.client import Client as NATS
from app.config import settings


async def run_chat_nats_test():
    nc = NATS()
    await nc.connect(settings.nats_url)

    subject = settings.nats_chat_recommend_subject

    payload = {
        "request_id": "test-req-001",
        "messages": [
            "Shell we schedule a meeting for next week to discuss the project updates?",
        ]
    }

    print("\n📤 Sending chat recommendation request...")
    start_time = time.perf_counter()

    response = await nc.request(
        subject,
        json.dumps(payload).encode(),
        timeout=15
    )

    latency = round(time.perf_counter() - start_time, 3)

    result = json.loads(response.data.decode())

    print(f"\n📥 Response received in {latency} seconds\n")
    print("===== CHAT RECOMMENDATION RESULT =====\n")

    print(f"Request ID        : {result.get('request_id')}")
    print(f"Worker Latency    : {result.get('latency_sec')} sec")
    print(f"Emotion           : {result.get('result', {}).get('emotion')}")
    print(f"Intent            : {result.get('result', {}).get('intent')}")
    print(f"Situation         : {result.get('result', {}).get('situation')}")
    print(
        f"Recommended Tone  : "
        f"{result.get('result', {}).get('recommended_tone')}"
    )

    print("\nSuggested Replies:")
    for idx, reply in enumerate(
        result.get("result", {}).get("suggested_replies", []),
        start=1
    ):
        print(f"{idx}. {reply}")

    print("\n=====================================\n")

    await nc.close()


if __name__ == "__main__":
    asyncio.run(run_chat_nats_test())
