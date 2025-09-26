from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    photo_url: Optional[str] = None

class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool
    created_at: Optional[datetime] = None