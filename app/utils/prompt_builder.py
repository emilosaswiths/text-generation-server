from pathlib import Path
from typing import Dict

from app.core.logger import get_logger

logger = get_logger("prompt_builder")

# Base directory: app/prompts/
PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.

    Args:
        prompt_name (str): filename without extension (e.g. 'caption_prompt')

    Returns:
        str: prompt template text
    """
    prompt_path = PROMPT_DIR / f"{prompt_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    logger.debug(f"Loading prompt: {prompt_path.name}")

    return prompt_path.read_text(encoding="utf-8")


def build_prompt(prompt_name: str, variables: Dict[str, str]) -> str:
    """
    Load a prompt template and substitute variables.

    Args:
        prompt_name (str): prompt file name (without .txt)
        variables (dict): key-value pairs to format into prompt

    Returns:
        str: final formatted prompt
    """
    template = load_prompt(prompt_name)

    try:

        prompt = template.format(**variables)

    except KeyError as e:
        raise ValueError(f"Missing prompt variable: {e}")

    logger.debug("🧩 Prompt built successfully")
    return prompt
