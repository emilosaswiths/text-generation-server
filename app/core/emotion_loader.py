import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from app.config import settings
from app.core.logger import get_logger

logger = get_logger("emotion_loader")

_processor = None
_model = None

# Emotion labels (VERY IMPORTANT – fixed order)
EMOTION_LABELS = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral"
]


def load_emotion_model():
    """
    Load face emotion detection model.
    Safe for CPU and GPU.
    """
    global _processor, _model

    if _processor is not None and _model is not None:
        logger.info("Emotion model already loaded — using cached instance")
        return _processor, _model

    model_name = settings.EMOTION_MODEL_NAME
    hf_cache_dir = getattr(settings, "HF_CACHE_DIR", None)

    use_cuda = torch.cuda.is_available()

    if use_cuda:
        logger.info("CUDA available — loading emotion model on GPU")
        dtype = torch.float16
    else:
        logger.warning("CUDA not available — loading emotion model on CPU")
        dtype = torch.float32

    logger.info("Loading face emotion detection model...")

    processor = ViTImageProcessor.from_pretrained(
        model_name,
        cache_dir=hf_cache_dir
    )

    model = ViTForImageClassification.from_pretrained(
        model_name,
        torch_dtype=dtype,
        cache_dir=hf_cache_dir
    )

    if not use_cuda:
        model.to("cpu")

    model.eval()

    _processor = processor
    _model = model

    logger.info("Emotion model loaded successfully")
    logger.info(f"Model: {model_name}")
    logger.info(f"Device: {'cuda' if use_cuda else 'cpu'}")

    return _processor, _model


def get_emotion_model():
    if _processor is None or _model is None:
        raise RuntimeError(
            "Emotion model not loaded. Call load_emotion_model() during startup."
        )
    return _processor, _model
