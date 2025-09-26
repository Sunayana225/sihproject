from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class DiseaseInfo(BaseModel):
    name: str
    symptoms: str
    prevention: str
    treatment: str
    severity: str
    language: str = 'en'

class VaccinationInfo(BaseModel):
    vaccine_name: str
    age_group: str
    schedule: str
    description: str
    side_effects: Optional[str] = None
    language: str = 'en'

class ChatMessage(BaseModel):
    message: str
    language: str = 'en'
    user_id: Optional[str] = 'anonymous'

class ChatResponse(BaseModel):
    response: str
    language: str
    timestamp: datetime

class HealthChatHistory(BaseModel):
    id: Optional[int] = None
    user_message: str
    bot_response: str
    language: str = 'en'
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = None

class EmergencyInfo(BaseModel):
    ambulance: str = '108'
    police: str = '100'
    fire: str = '101'
    message: str
    language: str = 'en'

class HealthSearchQuery(BaseModel):
    query: str
    language: str = 'en'

class DiseaseSearchResponse(BaseModel):
    diseases: List[DiseaseInfo]
    total: int

class VaccinationSearchResponse(BaseModel):
    vaccinations: List[VaccinationInfo]
    total: int