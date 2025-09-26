from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import logging
from datetime import datetime

from app.models.health import (
    ChatMessage, ChatResponse, DiseaseSearchResponse, 
    VaccinationSearchResponse, EmergencyInfo, HealthSearchQuery
)
from app.services.health_database import health_db
from app.services.ai_health_assistant import ai_assistant

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/health/chat", response_model=ChatResponse)
async def health_chat(message_data: ChatMessage):
    """Endpoint to handle health-related chat requests."""
    try:
        user_message = message_data.message.strip()
        language = message_data.language
        user_id = message_data.user_id or 'anonymous'
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"Received health chat message from user {user_id}: '{user_message}' in language '{language}'")
        
        # Generate AI response
        bot_response = ai_assistant.generate_response(user_message, language)
        
        # Save to chat history
        health_db.save_chat_history(user_message, bot_response, language, user_id)
        
        return ChatResponse(
            response=bot_response,
            language=language,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error in health chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/diseases", response_model=DiseaseSearchResponse)
async def get_diseases(q: str = "", lang: str = "en"):
    """Endpoint to get disease information."""
    try:
        results = health_db.search_diseases(q, lang)
        return DiseaseSearchResponse(diseases=results, total=len(results))
    except Exception as e:
        logger.error(f"Error retrieving diseases: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/vaccinations", response_model=VaccinationSearchResponse)
async def get_vaccinations(age_group: Optional[str] = None, lang: str = "en"):
    """Endpoint to get vaccination schedule."""
    try:
        results = health_db.get_vaccination_schedule(age_group, lang)
        return VaccinationSearchResponse(vaccinations=results, total=len(results))
    except Exception as e:
        logger.error(f"Error retrieving vaccinations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/emergency", response_model=EmergencyInfo)
async def get_emergency_info(lang: str = "en"):
    """Endpoint to get emergency contact information."""
    try:
        emergency_messages = {
            'en': {
                'ambulance': '108',
                'police': '100',
                'fire': '101',
                'message': 'For medical emergencies, call 108 immediately. This is a free service available 24/7 across India.',
                'language': 'en'
            },
            'hi': {
                'ambulance': '108',
                'police': '100',
                'fire': '101',
                'message': 'आपातकालीन स्थिति में तुरंत 108 पर कॉल करें। यह भारत में 24/7 उपलब्ध एक निःशुल्क सेवा है।',
                'language': 'hi'
            },
            'bn': {
                'ambulance': '108',
                'police': '100', 
                'fire': '101',
                'message': 'চিকিৎসা জরুরী অবস্থার জন্য, অবিলম্বে 108 নম্বরে কল করুন।',
                'language': 'bn'
            },
            # Add more languages as needed...
        }
        
        info = emergency_messages.get(lang, emergency_messages['en'])
        return EmergencyInfo(**info)
    except Exception as e:
        logger.error(f"Error retrieving emergency info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health/ui")
async def serve_health_ui():
    """Serve the health chatbot UI."""
    try:
        import os
        # Get the absolute path to the HTML file
        html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sih", "index.html")
        if os.path.exists(html_path):
            return FileResponse(html_path, media_type="text/html")
        else:
            raise HTTPException(status_code=404, detail="Health UI not found")
    except Exception as e:
        logger.error(f"Error serving health UI: {e}")
        raise HTTPException(status_code=404, detail="Health UI not found")

@router.get("/health/status")
async def health_service_status():
    """Health check for the health service."""
    try:
        # Test database connection
        diseases = health_db.search_diseases("test", "en")
        
        return {
            "status": "healthy",
            "service": "health-chatbot",
            "database": "connected",
            "ai_service": "available",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health service status check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "health-chatbot",
            "database": "error",
            "ai_service": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }