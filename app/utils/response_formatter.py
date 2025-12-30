import json
import re
from app.core.logger import get_logger

logger = get_logger("response_formatter")


def strip_markdown(text: str) -> str:
    """Remove markdown code fences."""
    return re.sub(r"```(?:json)?|```", "", text, flags=re.IGNORECASE).strip()


def extract_first_json(text: str) -> dict | None:
    """
    Extract and parse the FIRST valid JSON object from text.
    Handles:
    - Extra text before/after JSON
    - Multiple JSON blocks
    - Model explanations
    """
    if not text:
        return None

    text = strip_markdown(text)

    decoder = json.JSONDecoder()
    idx = 0
    length = len(text)

    while idx < length:
        try:
            obj, end = decoder.raw_decode(text[idx:])
            return obj
        except json.JSONDecodeError:
            idx += 1

    return None


def safe_json_parse(text: str) -> dict:
    if not text or not isinstance(text, str):
        return {}

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return {}

    try:
        parsed = json.loads(text[start:end + 1])
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
