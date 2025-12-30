from PIL import Image
import torch
from typing import Optional
from app.core.blip_loader import load_blip
from app.core.logger import get_logger

logger = get_logger("image_caption_service")


def generate_image_caption(
    image_path: str,
    max_new_tokens: int = 30
) -> Optional[str]:
    """
    Generate a neutral scene description from an image using BLIP.

    Args:
        image_path (str): Local path to image
        max_new_tokens (int): Max tokens for caption generation

    Returns:
        str | None: Generated caption or None if failed
    """
    try:
        processor, model = load_blip()

        image = Image.open(image_path).convert("RGB")

        inputs = processor(
            images=image,
            return_tensors="pt"
        ).to(model.device)

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens
            )

        caption = processor.decode(
            output[0],
            skip_special_tokens=True
        )

        caption = caption.strip().lower()

        logger.info(
            f"BLIP caption generated for {image_path}: {caption}"
        )

        return caption

    except Exception as e:
        logger.error(
            f"Failed to generate BLIP caption for {image_path}: {e}"
        )
        return None
