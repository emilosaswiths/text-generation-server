from typing import Dict, List
from collections import Counter

from app.core.generation import generate_text
from app.utils.prompt_builder import build_prompt
from app.core.logger import get_logger

logger = get_logger("monthly_moment_caption_service")


def generate_monthly_moment_captions(
    month: str,
    posts: List[Dict],
    tone: str = "romantic"
) -> Dict[str, str]:
    """
    Generate ONLY 3 captions (start, middle, end) for a monthly moment video
    using all images of the month.
    """

    # -------------------------
    # Build combined scene context
    # -------------------------
    scenes = [
        p.get("image_blip_caption")
        for p in posts
        if p.get("image_blip_caption")
    ]
    scenes_text = "- " + "\n- ".join(scenes[:15])  # limit for prompt safety

    # -------------------------
    # Derive overall emotion mood
    # -------------------------
    emotions = [p.get("emotion") for p in posts if p.get("emotion")]
    emotion_summary = ", ".join(
        Counter(emotions).most_common(3)[i][0]
        for i in range(min(3, len(set(emotions))))
    ) if emotions else "warm"

    logger.info(
        f"Generating monthly captions for {month} | emotions={emotion_summary}"
    )

    captions = {}

    for position in ["start", "middle", "end"]:
        prompt = build_prompt(
            "monthly_moment_prompt",
            {
                "position": position,
                "month": month,
                "scenes": scenes_text,
                "emotions": emotion_summary,
                "tone": tone
            }
        )

        text = generate_text(
            prompt=prompt,
            max_new_tokens=45
        )

        captions[position] = text.strip()

    return captions
