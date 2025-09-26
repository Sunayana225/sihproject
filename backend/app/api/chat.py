from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.auth import get_current_user
from ..models.chat import ChatMessage, ChatResponse, Message, MessageRole
from ..services.health_filter import HealthContextFilter
from ..services.gemini_service import GeminiHealthBot

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize services
health_filter = HealthContextFilter()
gemini_bot = None

def get_gemini_bot():
    """Lazy initialization of Gemini bot"""
    global gemini_bot
    if gemini_bot is None:
        gemini_bot = GeminiHealthBot()
    return gemini_bot

@router.post("/message", response_model=ChatResponse)
async def send_message(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to the health chatbot
    """
    try:
        # Validate and filter the message
        filter_result = health_filter.is_health_related(message.content)
        
        if not filter_result.is_health_related:
            # Return rejection message for non-health queries
            rejection_message = health_filter.get_rejection_message(message.content)
            
            return ChatResponse(
                message=rejection_message,
                message_id=str(uuid.uuid4()),
                session_id=message.session_id or str(uuid.uuid4()),
                timestamp=datetime.utcnow()
            )
        
        # Sanitize the health query
        sanitized_query = health_filter.sanitize_health_query(message.content)
        
        # Check for sensitive content
        if sanitized_query.startswith("[SENSITIVE_CONTENT]"):
            sensitive_response = (
                "I understand you may be going through a difficult time. If you're having thoughts of self-harm "
                "or suicide, please reach out for help immediately:\n\n"
                "• National Suicide Prevention Lifeline: 988\n"
                "• Crisis Text Line: Text HOME to 741741\n"
                "• Emergency Services: 911\n\n"
                "For other health concerns, I'm here to provide general health information and guidance. "
                "Please feel free to ask about symptoms, wellness, or when to seek medical care.\n\n"
                "⚠️ **Important:** If this is a medical emergency, please call 911 immediately."
            )
            
            return ChatResponse(
                message=sensitive_response,
                message_id=str(uuid.uuid4()),
                session_id=message.session_id or str(uuid.uuid4()),
                timestamp=datetime.utcnow()
            )
        
        # Generate response using Gemini API
        # For now, we'll use a placeholder context - in a full implementation,
        # you would retrieve conversation history from the database
        context = []  # This would be populated with previous messages
        
        bot = get_gemini_bot()
        ai_response = await bot.get_health_response(sanitized_query, context)
        
        return ChatResponse(
            message=ai_response,
            message_id=str(uuid.uuid4()),
            session_id=message.session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Chat API error: {str(e)}")
        
        # Return a generic error response
        error_response = (
            "I apologize, but I'm experiencing technical difficulties right now. "
            "For health-related questions, please consider contacting your healthcare provider "
            "or calling a medical helpline in your area.\n\n"
            "⚠️ **For emergencies, call 911 immediately.**"
        )
        
        return ChatResponse(
            message=error_response,
            message_id=str(uuid.uuid4()),
            session_id=message.session_id or str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )

@router.post("/validate-query")
async def validate_health_query(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate if a query is health-related without generating a response
    """
    try:
        filter_result = health_filter.is_health_related(message.content)
        
        return {
            "is_health_related": filter_result.is_health_related,
            "confidence": filter_result.confidence,
            "reason": filter_result.reason,
            "rejection_message": health_filter.get_rejection_message(message.content) if not filter_result.is_health_related else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )

@router.get("/health-check")
async def chat_health_check():
    """
    Health check endpoint for chat service
    """
    try:
        # Test Gemini API connection
        bot = get_gemini_bot()
        test_response = await bot.get_health_response("test connection")
        
        return {
            "status": "healthy",
            "services": {
                "health_filter": "operational",
                "gemini_api": "operational" if test_response else "degraded"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "services": {
                "health_filter": "operational",
                "gemini_api": "error"
            }
        }