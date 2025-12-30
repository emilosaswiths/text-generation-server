import json
import asyncio
from typing import List, Dict

from app.nats.base_nats_consumer import NATSConnection
from app.services.image_caption_service import generate_image_caption
from app.core.logger import get_logger

logger = get_logger("monthly_blip_consumer")

INPUT_SUBJECT = "monthly.posts.blip"
OUTPUT_SUBJECT = "monthly.posts.qwen"


def process_posts_with_blip(posts: List[Dict]) -> List[Dict]:
    """
    Generate BLIP caption for each post and build payload for Qwen.
    (CPU/GPU bound → normal function)
    """
    enriched_posts = []

    for post in posts:
        post_id = post.get("_id")
        image_path = post.get("image_path")

        if not image_path:
            logger.warning(f"Post {post_id} has no image_path, skipping")
            continue

        blip_caption = generate_image_caption(image_path)

        logger.info(f"Generated BLIP caption for post {post_id}- {blip_caption}")

        enriched_posts.append({
            "_id": post_id,
            "caption": post.get("caption"),
            "image_blip_caption": blip_caption,
            "emotion": post.get("emotion"),
            "emotionScore": post.get("emotionScore"),
            "qualityScore": post.get("qualityScore")
        })

        logger.info(f"Processed post {post_id} with BLIP caption")

    return enriched_posts


async def start_monthly_blip_consumer():
    nats = NATSConnection()
    await nats.connect()

    async def message_handler(msg):
        try:
            payload = json.loads(msg.data.decode())
            posts = payload.get("posts", [])

            logger.info(f"Received {len(posts)} posts for BLIP processing")

            # ✅ Correct usage
            enriched_posts = await asyncio.to_thread(
                process_posts_with_blip,
                posts
            )

            output_payload = {
                "month": payload.get("month"),
                "posts": enriched_posts
            }

            await nats.nc.publish(
                OUTPUT_SUBJECT,
                json.dumps(output_payload).encode()
            )

            logger.info(
                f"Published {len(enriched_posts)} posts to {OUTPUT_SUBJECT}"
            )

        except Exception as e:
            logger.error(f"BLIP processing failed: {e}")

    await nats.nc.subscribe(INPUT_SUBJECT, cb=message_handler)
    logger.info(f"Subscribed to {INPUT_SUBJECT}")
