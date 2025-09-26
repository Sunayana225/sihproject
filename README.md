# 🏥 SIH Healthcare AI Assistant

## 📋 Project Overview
A comprehensive healthcare AI assistant designed for rural and semi-urban populations in India. This multilingual platform provides medical education, vaccination reminders, and health guidance with AI-powered responses.

## 🌟 Features

### 🤖 AI-Powered Health Assistant
- **Multi-language Support**: English, Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Odia, Assamese
- **Bullet-formatted Responses**: Clear, structured health advice in bullet points
- **Emergency Detection**: Automatic 108 emergency number recommendations for serious symptoms
- **Cultural Sensitivity**: Responses tailored to Indian healthcare context

### 💉 Vaccination System
- **Drive Notifications**: Real-time vaccination drive alerts in navbar
- **Multi-language Notifications**: Vaccination alerts in user's preferred language
- **Badge System**: Unread notification counter with visual indicators
- **Health Categories**: Organized health topics by body parts/systems

### 🎨 User Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Health Category Dropdown**: Quick access to common health topics
- **Modern UI**: Clean, healthcare-themed interface
- **Toast Notifications**: User-friendly feedback system

### 🔧 Technical Stack
- **Backend**: Flask with Google Gemini AI integration
- **Frontend**: HTML/CSS/JavaScript with modern responsive design
- **Database**: SQLite for health data storage
- **AI**: Google Gemini 2.5 Flash model
- **Languages**: Python, JavaScript, HTML, CSS

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Git
- Google Gemini API Key

### Backend Setup
```bash
cd backend/sih
pip install -r requirements.txt
python app.py
```

### Frontend Setup (React)
```bash
cd frontend
npm install
npm start
```

### Environment Configuration
1. Copy `.env.example` to `.env`
2. Add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## 📱 Usage

### Health Consultation
1. Select your preferred language
2. Type health-related questions
3. Receive AI-generated advice in bullet-point format
4. Get emergency contact info for serious conditions

### Vaccination Notifications
1. Click the notification bell in navbar
2. View upcoming vaccination drives
3. Mark notifications as read
4. Access multilingual vaccination information

### Health Categories
1. Use the health dropdown menu
2. Select category by body part (Heart, Brain, etc.)
3. Get quick access to relevant health topics

## 🌍 Multilingual Support

### Supported Languages
- 🇬🇧 English
- 🇮🇳 हिन्दी (Hindi)
- 🇮🇳 বাংলা (Bengali)
- 🇮🇳 தமிழ் (Tamil)
- 🇮🇳 తెలుగు (Telugu)
- 🇮🇳 मराठी (Marathi)
- 🇮🇳 ગુજરાતી (Gujarati)
- 🇮🇳 ಕನ್ನಡ (Kannada)
- 🇮🇳 മലയാളം (Malayalam)
- 🇮🇳 ਪੰਜਾਬੀ (Punjabi)
- 🇮🇳 ଓଡିଆ (Odia)
- 🇮🇳 অসমীয়া (Assamese)

## 🛠️ API Endpoints

### Chat API
- **POST** `/api/chat`
- **Body**: `{"message": "health question", "language": "en", "user_id": "user123"}`
- **Response**: Structured health advice with bullet formatting

### Health Data
- **GET** `/api/health/diseases` - Get disease information
- **GET** `/api/health/vaccinations` - Get vaccination schedules

## 🔒 Security Features
- Input validation and sanitization
- Emergency keyword detection
- Professional medical disclaimer
- Safe health information sourcing

## 🎯 Project Goals
- Improve healthcare accessibility in rural India
- Provide multilingual health education
- Enable quick emergency assistance
- Promote vaccination awareness
- Bridge healthcare information gaps

## 👥 Team
- **Developer**: Sunayana Yakkala
- **Email**: yakkalasunayana1605@gmail.com
- **Project**: SIH (Smart India Hackathon) Healthcare Solution

## 📄 License
This project is developed for Smart India Hackathon 2024.

## 🤝 Contributing
Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support
For support and queries:
- Email: yakkalasunayana1605@gmail.com
- GitHub Issues: [Report bugs/requests](https://github.com/Sunayana225/sihproject/issues)

---
*Built with ❤️ for improving rural healthcare in India*

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