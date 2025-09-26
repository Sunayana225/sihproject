from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    content: str
    role: MessageRole = MessageRole.USER
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    message_id: str
    session_id: str
    timestamp: datetime

class Message(BaseModel):
    id: str
    content: str
    role: MessageRole
    timestamp: datetime
    session_id: str
    user_id: str

class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class HealthQuery(BaseModel):
    content: str
    user_id: str
    session_id: str
    timestamp: datetime
    is_health_related: bool
    response_generated: bool = False