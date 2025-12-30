from fastapi import APIRouter, HTTPException

from app.core.generation import generate_text
from app.utils.prompt_builder import build_prompt
from app.core.logger import get_logger

router = APIRouter(prefix="/caption", tags=["Text Generation"])
logger = get_logger("caption_api")


@router.post("/")
async def generate_caption(payload: dict):
    """
    Generate a caption for a business page.
    Expected payload:
    {
        "company_name": "",
        "category": "",
        "sub_category": "",
        "tone": ""
    }
    """

    try:
        prompt = build_prompt(
            "caption_prompt",
            {
                "company_name": payload.get("company_name"),
                "category": payload.get("category"),
                "sub_category": payload.get("sub_category"),
                "tone": payload.get("tone", "professional"),
            }
        )

        caption = generate_text(
            prompt=prompt,
            max_new_tokens=60
        )

        return {
            "status": "success",
            "caption": caption
        }

    except Exception as e:
        logger.exception("❌ Caption generation failed")
        raise HTTPException(status_code=500, detail=str(e))
