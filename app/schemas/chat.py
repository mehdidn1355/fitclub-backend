from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FAQResponse(BaseModel):
    id: int
    category: str
    question: str
    answer: str

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str
    session_token: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    session_token: str
    user_message: ChatMessageResponse
    bot_message: ChatMessageResponse


class ChatHistoryResponse(BaseModel):
    session_token: str
    messages: List[ChatMessageResponse]