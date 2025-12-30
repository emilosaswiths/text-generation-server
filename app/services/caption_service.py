from app.core.generation import generate_text
from app.utils.prompt_builder import build_prompt
from app.core.logger import get_logger

logger = get_logger("caption_service")


def generate_caption_service(
    company_name: str,
    category: str,
    sub_category: str,
    tone: str = "professional",
) -> str:
    """
    Business logic for caption generation.
    """

    logger.debug("Building caption prompt")

    prompt = build_prompt(
        "caption_prompt",
        {
            "company_name": company_name,
            "category": category,
            "sub_category": sub_category,
            "tone": tone,
        }
    )

    logger.debug("Generating caption text")

    caption = generate_text(
        prompt=prompt,
        max_new_tokens=60
    )

    return caption

