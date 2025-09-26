# Healthcare SIH Integration Instructions

## Quick Start Guide

After making the changes, here's how to use the application:

### 1. Start the SIH Backend (Required)

Before clicking "Try Now" on the landing page, you need to start the Flask backend:

**Option A: Using the batch file (Windows)**
```
Double-click start_sih_backend.bat in the root directory
```

**Option B: Manual startup**
```bash
cd backend/sih
pip install -r requirements.txt
python app.py
```

The Flask server will start on `http://localhost:5000`

### 2. Start the Frontend

In a separate terminal:
```bash
cd frontend
npm install
npm start
```

The React app will start on `http://localhost:3000`

### 3. Usage

1. Visit `http://localhost:3000` to see the landing page
2. Make sure the Flask backend is running (step 1)
3. Click "Try Now" button on the landing page
4. You'll be redirected to the SIH application interface with all original functionalities

## What Changed

- **Landing Page**: "Try Now" button now redirects to `/sih/index.html` instead of React chat
- **Authentication**: Removed authentication requirement for accessing the health assistant
- **SIH Integration**: The complete SIH folder is now served as static files under `/sih/`
- **Backend Preservation**: All original SIH functionalities remain intact

## Features Preserved

- ✅ AI-powered health chatbot
- ✅ Multilingual support (English/Hindi)
- ✅ Disease information database
- ✅ Vaccination schedules
- ✅ Health tips and advice
- ✅ Emergency contact information
- ✅ Offline mode support
- ✅ Mobile-responsive design

## Troubleshooting

If "Try Now" doesn't work:
1. Ensure the Flask backend is running on port 5000
2. Check browser console for any errors
3. Verify the sih folder exists in frontend/public/
4. Try accessing `http://localhost:3000/sih/index.html` directly

## Development Notes

- The original React chat interface is completely disabled
- All routing now goes through the SIH HTML interface
- The landing page UI is preserved exactly as requested
- Backend dependencies are managed separately from frontend