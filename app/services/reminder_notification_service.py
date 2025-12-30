from app.core.generation import generate_text
from app.utils.prompt_builder import build_prompt
from app.core.logger import get_logger

logger = get_logger("reminder_notification_service")


def generate_reminder_notification_service(
    title: str,
    category: str,
    location: str,
    notes: str,
    days_offset: int,
    partner_name: str,
    recent_chat_mood: str = "neutral",
    preferred_tone: str = "romantic",
) -> str:
    """
    Business logic for special day reminder notification generation.
    """

    logger.debug("Building reminder notification prompt")

    prompt = build_prompt(
        "reminder_notification",
        {
            "title": title,
            "category": category,
            "location": location,
            "notes": notes,
            "days_offset": days_offset,
            "partner_name": partner_name,
            "recent_chat_mood": recent_chat_mood,
            "preferred_tone": preferred_tone,
        }
    )

    logger.debug("Generating reminder notification text")
    logger.info(f"Reminder Prompt: {prompt}")

    reminder_text = generate_text(
        prompt=prompt,
        max_new_tokens=20,
        temperature=0.7,
    )

    return reminder_text
