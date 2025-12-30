import asyncio
import json
from nats.aio.client import Client as NATS

NATS_URL = "nats://app:secret@68.183.88.195:4222"
SUBJECT = "monthly.posts.blip"


async def main():
    nc = NATS()
    await nc.connect(NATS_URL)

    
    payload = {
  "month": "March",
  "posts": [
    {
      "_id": 101,
      "caption": "Mountain trip together",
      "image_path": "D:\\emilo-project\\text-generation-server\\Alaska-Mountains-and-Wildflowers-Brad-Josephs-1.jpeg",
      "emotion": "Happy",
      "emotionScore": 0.87,
      "qualityScore": 0.74
    },
    {
      "_id": 102,
      "caption": "Evening walk",
      "image_path": "D:\\emilo-project\\text-generation-server\\what-is-better-morning-or-evening-walk.webp",
      "emotion": "Calm",
      "emotionScore": 0.65,
      "qualityScore": 0.68
    },
    {
      "_id": 103,
      "caption": "Coffee date",
      "image_path": "D:\\emilo-project\\text-generation-server\\valentines-hands-coffee-and-love.jpg",
      "emotion": "Happy",
      "emotionScore": 0.79,
      "qualityScore": 0.71
    },
    {
      "_id": 104,
      "caption": "Sunset view",
      "image_path": "D:\\emilo-project\\text-generation-server\\gettyimages-1744906692-612x612.jpg",
      "emotion": "Romantic",
      "emotionScore": 0.83,
      "qualityScore": 0.76
    }
  ]
}


    await nc.publish(
        SUBJECT,
        json.dumps(payload).encode()
    )

    print("✅ Test payload published to NATS")

    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
