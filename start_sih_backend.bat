@echo off
echo Starting Healthcare SIH Backend...
cd /d "d:\VIT\Projects\SIH 2025 (2)\healthcare\backend\sih"

echo Installing requirements...
python -m pip install -r requirements.txt

echo Starting Flask application...
python app.py

pause