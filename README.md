# Rural Health Platform

A web-based application providing accessible healthcare guidance to users in rural areas through an AI-powered chatbot interface.

## Project Structure

```
rural-health-platform/
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── utils/         # Utility functions
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript type definitions
│   └── public/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core utilities
│   │   ├── models/       # Data models
│   │   └── services/     # Business logic
│   └── tests/
└── README.md
```

## Technology Stack

- **Frontend**: React 18+ with TypeScript, Tailwind CSS
- **Backend**: Python with FastAPI framework
- **Authentication**: Firebase Authentication
- **Database**: Firebase Firestore
- **AI Service**: Google Gemini API
- **Styling**: Tailwind CSS with Inter font

## Getting Started

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Environment Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Configure Firebase project credentials
3. Add Gemini API key
4. Update CORS origins for production

## Features

- Clean, minimal white and blue design
- Firebase authentication with Google OAuth
- ChatGPT-like interface with typing indicators
- Health-focused AI responses using Gemini API
- Context filtering for health-related queries only
- Responsive design for all devices
- Accessibility compliance (WCAG 2.1 AA)