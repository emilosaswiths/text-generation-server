import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from app.config import settings
from app.core.logger import get_logger

logger = get_logger("model_loader")

_tokenizer = None
_model = None


def load_model():
    """
    Load Qwen-2.5 model & tokenizer.
    Safe for CPU and GPU.
    """
    global _tokenizer, _model

    if _model is not None and _tokenizer is not None:
        logger.info("Model already loaded — using cached instance")
        return _tokenizer, _model

    model_name = settings.QWEN_MODEL_NAME
    hf_cache_dir = getattr(settings, "HF_CACHE_DIR", None)

    use_cuda = torch.cuda.is_available()

    if use_cuda:
        logger.info("CUDA available — loading model on GPU")
        device_map = "auto"
        dtype = torch.float16
    else:
        logger.warning("CUDA not available — loading model fully on CPU")
        device_map = None
        dtype = torch.float32

    logger.info("Loading Qwen-2.5 model...")

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        cache_dir=hf_cache_dir
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        device_map=device_map,
        dtype=dtype,      # ✅ correct
        low_cpu_mem_usage=True,
        cache_dir=hf_cache_dir
    )

    if not use_cuda:
        model.to("cpu")

    model.eval()

    _tokenizer = tokenizer
    _model = model

    logger.info("Qwen-2.5 model loaded successfully")
    logger.info(f"Model: {model_name}")
    logger.info(f"Device: {'cuda' if use_cuda else 'cpu'}")
    logger.info(f"Dtype: {dtype}")

    return _tokenizer, _model


def get_model():
    if _model is None or _tokenizer is None:
        raise RuntimeError(
            "Model not loaded. Call load_model() during server startup."
        )
    return _tokenizer, _model
