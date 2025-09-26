from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

# Import routers
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.firebase import firebase_service

app = FastAPI(
    title="Rural Health Platform API",
    description="Backend API for rural health assistance platform with AI-powered health chatbot",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5000",  # Flask dev server (for health UI)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    firebase_service.initialize()

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Rural Health Platform API is running",
        "features": [
            "Authentication & User Management",
            "AI-Powered Health Chat Assistant",
            "Disease Information Database",
            "Vaccination Schedules",
            "Emergency Contact Information",
            "Multi-language Support"
        ],
        "endpoints": {
            "auth": "/api/auth/*",
            "chat": "/api/chat/*",
            "health": "/api/health/*",
            "health_ui": "/api/health/ui"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rural-health-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)