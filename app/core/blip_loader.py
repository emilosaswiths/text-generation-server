import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from app.config import settings
from app.core.logger import get_logger

logger = get_logger("blip_loader")

_processor = None
_model = None


def load_blip():
    """
    Load BLIP-2 model & processor.
    Safe for CPU and GPU.
    """
    global _processor, _model

    if _model is not None and _processor is not None:
        logger.info("BLIP-2 already loaded — using cached instance")
        return _processor, _model

    model_name = settings.BLIP_MODEL_NAME
    hf_cache_dir = getattr(settings, "HF_CACHE_DIR", None)

    use_cuda = torch.cuda.is_available()

    if use_cuda:
        logger.info("CUDA available — loading BLIP-2 on GPU")
        device_map = "auto"
        dtype = torch.float16
    else:
        logger.warning("CUDA not available — loading BLIP-2 fully on CPU")
        device_map = None
        dtype = torch.float32

    logger.info("Loading BLIP-2 model...")

    processor = BlipProcessor.from_pretrained(
        model_name,
        cache_dir=hf_cache_dir
    )

    model = BlipForConditionalGeneration.from_pretrained(
        model_name,
        device_map=device_map,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        cache_dir=hf_cache_dir
    )

    if not use_cuda:
        model.to("cpu")

    model.eval()

    _processor = processor
    _model = model

    logger.info("BLIP-2 model loaded successfully")
    logger.info(f"Model: {model_name}")
    logger.info(f"Device: {'cuda' if use_cuda else 'cpu'}")
    logger.info(f"Dtype: {dtype}")

    return _processor, _model


def get_blip():
    if _model is None or _processor is None:
        raise RuntimeError(
            "BLIP-2 not loaded. Call load_blip() during server startup."
        )
    return _processor, _model
