from PIL import Image
import cv2
import numpy as np
from typing import Dict, Optional
from app.core.logger import get_logger

logger = get_logger("image_quality_service")


def analyze_image_quality(image_path: str) -> Optional[Dict]:
    """
    Analyze image quality metrics.

    Metrics:
    - brightness
    - sharpness
    - contrast
    - noise
    - overall quality score (0–1)

    Returns:
        dict | None
    """
    try:
        # Load image
        pil_image = Image.open(image_path).convert("RGB")
        image = np.array(pil_image)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # -------------------------
        # Brightness (mean intensity)
        # -------------------------
        brightness = float(np.mean(gray)) / 255.0  # normalize 0–1

        # -------------------------
        # Sharpness (Laplacian variance)
        # -------------------------
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_norm = min(sharpness / 1000.0, 1.0)

        # -------------------------
        # Contrast (standard deviation)
        # -------------------------
        contrast = float(np.std(gray)) / 128.0
        contrast = min(contrast, 1.0)

        # -------------------------
        # Noise estimation (difference from Gaussian blur)
        # -------------------------
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = float(np.mean(np.abs(gray - blur))) / 255.0
        noise = min(noise, 1.0)

        # -------------------------
        # Overall quality score
        # -------------------------
        quality_score = (
            0.35 * sharpness_norm +
            0.25 * contrast +
            0.25 * brightness +
            0.15 * (1 - noise)
        )

        quality_score = round(float(quality_score), 3)

        result = {
            "brightness": round(brightness, 3),
            "sharpness": round(sharpness_norm, 3),
            "contrast": round(contrast, 3),
            "noise": round(noise, 3),
            "quality_score": quality_score
        }

        logger.info(f"Image quality analyzed for {image_path}: {result}")

        return result

    except Exception as e:
        logger.error(f"Image quality analysis failed for {image_path}: {e}")
        return None
