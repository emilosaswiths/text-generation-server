from fastapi import APIRouter, HTTPException
from app.services.chat_recommendation_service import (
    generate_chat_recommendation_service
)

router = APIRouter()


@router.post("/chat/recommend")
def recommend_chat(payload: dict):
    """
    payload = {
        "messages": ["msg1", "msg2", ...]
    }
    """

    messages = payload.get("messages")

    if not messages or not isinstance(messages, list):
        raise HTTPException(
            status_code=400,
            detail="`messages` must be a non-empty list of strings"
        )

    return generate_chat_recommendation_service(messages)
