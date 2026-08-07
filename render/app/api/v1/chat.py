from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
from app.core.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(body: ChatRequest, user: Optional[dict] = Depends(get_current_user)):
    result = await chat_service.process_message(body.message)
    return ChatResponse(**result)
