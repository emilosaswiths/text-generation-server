import torch
from typing import Optional, List
from transformers import GenerationConfig

from app.core.model_loader import get_model
from app.core.logger import get_logger

logger = get_logger("generation")

# -------------------------------------------------
# Global safe defaults (work across use-cases)
# -------------------------------------------------
DEFAULT_MAX_NEW_TOKENS = 200
DEFAULT_MIN_NEW_TOKENS = 20
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_REPETITION_PENALTY = 1.05


def generate_text(
    prompt: str,
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
    min_new_tokens: int = DEFAULT_MIN_NEW_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    repetition_penalty: float = DEFAULT_REPETITION_PENALTY,
    stop_sequences: Optional[List[str]] = None,
    do_sample: bool = True,
) -> str:
    """
    Generic text generation function (Qwen-safe, reusable).

    This function is designed to be used across:
    - chat suggestions
    - captions
    - summaries
    - recommendations
    - moderation explanations

    It includes fallback & exception handling to avoid crashes.
    """

    if not prompt or not isinstance(prompt, str):
        logger.error("Invalid prompt passed to generate_text")
        return ""

    try:
        tokenizer, model = get_model()

        logger.debug("⚡ Running text generation")
        logger.debug(f"Prompt length: {len(prompt)} characters")

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True
        ).to(model.device)

        generation_config = GenerationConfig(
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

        with torch.no_grad():
            output_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs.get("attention_mask"),
                generation_config=generation_config
            )

        generated_text = tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )

        # -------------------------------------------------
        # Post-processing
        # -------------------------------------------------

        # Remove echoed prompt (common with Qwen)
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()

        # Apply stop sequences
        if stop_sequences:
            for seq in stop_sequences:
                if seq in generated_text:
                    generated_text = generated_text.split(seq)[0].strip()

        logger.debug("✅ Text generation completed")

        return generated_text.strip()

    except torch.cuda.OutOfMemoryError:
        logger.exception("🔥 CUDA OOM during generation")
        return ""

    except RuntimeError as e:
        logger.exception(f"🔥 Runtime error during generation: {e}")
        return ""

    except Exception as e:
        logger.exception(f"🔥 Unexpected error during generation: {e}")
        return ""
