import asyncio
import json
from nats.aio.client import Client as NATS

NATS_URL = "nats://app:secret@68.183.88.195:4222"
SUBJECT = "monthly.posts.qwen"


async def main():
    nc = NATS()
    await nc.connect(NATS_URL)

    print(f"👂 Listening on subject: {SUBJECT}")

    async def handler(msg):
        data = json.loads(msg.data.decode())
        print("\n📩 RESPONSE RECEIVED:")
        print(json.dumps(data, indent=2))

    await nc.subscribe(SUBJECT, cb=handler)

    # Keep the subscriber alive
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
