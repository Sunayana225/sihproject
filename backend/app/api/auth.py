from fastapi import APIRouter, Depends, HTTPException, status
from ..core.auth import get_current_user, get_current_user_optional
from ..models.user import UserResponse
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return UserResponse(
        uid=current_user["uid"],
        email=current_user["email"],
        display_name=current_user.get("name"),
        photo_url=current_user.get("picture"),
        email_verified=current_user.get("email_verified", False)
    )

@router.post("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    """
    return {
        "valid": True,
        "uid": current_user["uid"],
        "email": current_user["email"]
    }

@router.get("/status")
async def auth_status(current_user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Check authentication status without requiring authentication
    """
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "uid": current_user["uid"],
                "email": current_user["email"]
            }
        }
    else:
        return {"authenticated": False}