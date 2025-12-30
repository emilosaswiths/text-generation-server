from app.core.generation import generate_text
from app.utils.prompt_builder import build_prompt
from app.utils.response_formatter import safe_json_parse
from app.utils.text_cleaner import clean_text
from app.core.logger import get_logger

logger = get_logger("chat_recommendation_service")


def generate_chat_recommendation_service(
    chat_messages: list[str],
) -> dict:
    """
    Generate ONLY 3 human-like chat reply suggestions.
    """

    if not chat_messages:
        return empty_response()

    logger.debug("Cleaning chat messages")

    # Keep recent messages only (LLM-friendly)
    trimmed_messages = chat_messages[-5:]

    cleaned_messages = [
        clean_text(msg, max_length=300)
        for msg in trimmed_messages
        if isinstance(msg, str) and msg.strip()
    ]

    if not cleaned_messages:
        return empty_response()

    chat_context = "\n".join(cleaned_messages)
    logger.info(f"Chat context:\n{chat_context}")

    logger.info("Building chat recommendation prompt")

    prompt = build_prompt(
        "chat_recommendation_prompt",
        {"chat_context": chat_context}
    )

    logger.info("Prompt built successfully")
    logger.info(f"{prompt}")

    logger.info("Generating chat recommendation text")

    raw_output = generate_text(
       prompt=prompt,
        temperature=0.2,
        top_p=0.7,
        max_new_tokens=50,
        min_new_tokens=15,
        do_sample=False,
        stop_sequences=[
            "}\n",
            "\n\n",
            "DO NOT",
            "CHAT:",
            "RULES",
            "IMPORTANT"
        ]
    )
    logger.info("Raw chat recommendation output generated")
    logger.info(f"Raw output: {raw_output}")

    parsed = safe_json_parse(raw_output) or {}

    if not isinstance(parsed, dict):
        logger.warning("Model did not return valid JSON object")
        return fallback_response(cleaned_messages[-1])

    replies = parsed.get("suggested_replies")

    if not isinstance(replies, list) or len(replies) != 3:
        logger.warning("Invalid or missing suggested_replies")
        return fallback_response(cleaned_messages[-1])

    return {"suggested_replies": replies}



# -------------------------------------------------
# Helpers
# -------------------------------------------------

def empty_response():
    return {
        "suggested_replies": []
    }


def fallback_response(last_message: str):
    """
    Rule-based fallback to avoid empty UI.
    """
    text = last_message.lower()

    if any(word in text for word in ["thank", "thanks", "appreciate"]):
        return {
            "suggested_replies": [
                "Anytime!",
                "Glad it helped!",
                "No problem at all "
            ]
        }

    if any(word in text for word in ["stress", "tired", "busy", "deadline"]):
        return {
            "suggested_replies": [
                "That sounds really exhausting",
                "Yeah, that can be stressful",
                "Want to talk about it?"
            ]
        }

    if any(word in text for word in ["hi", "hello", "hey", "morning"]):
        return {
            "suggested_replies": [
                "Hey!",
                "Hi there!",
                "How’s it going?"
            ]
        }

    # Generic safe fallback
    return {
        "suggested_replies": [
            "Yeah",
            "I get that",
            "Tell me more"
        ]
    }
