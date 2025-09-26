from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import json
import re
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

class HealthDatabase:
    """Manages the health database and AI interactions"""
    
    def __init__(self):
        self.init_database()
        self.load_health_data()
    
    def init_database(self):
        """Initialize SQLite database for health data"""
        self.conn = sqlite3.connect('health_data.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                prevention TEXT NOT NULL,
                treatment TEXT NOT NULL,
                severity TEXT NOT NULL,
                language TEXT DEFAULT 'en'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vaccinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vaccine_name TEXT NOT NULL,
                age_group TEXT NOT NULL,
                schedule TEXT NOT NULL,
                description TEXT NOT NULL,
                side_effects TEXT,
                language TEXT DEFAULT 'en'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_tips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                tip TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info("Database initialized successfully")
    
    def load_health_data(self):
        """Load initial health data into the database"""
        
        diseases_data = [
            ('Common Cold', 'Runny nose, sneezing, cough, mild fever, sore throat', 
             'Wash hands frequently, avoid close contact with sick people, maintain good hygiene',
             'Rest, stay hydrated, use saline nasal drops, consult doctor if symptoms persist',
             'Mild', 'en'),
            
            ('Diabetes Type 2', 'Increased thirst, frequent urination, blurred vision, fatigue, slow healing wounds',
             'Maintain healthy weight, regular exercise, balanced diet, limit sugar intake',
             'Medication as prescribed, blood sugar monitoring, lifestyle changes',
             'Chronic', 'en'),
            
            ('Hypertension', 'Often no symptoms, sometimes headache, dizziness, chest pain',
             'Regular exercise, reduce sodium intake, maintain healthy weight, limit alcohol',
             'Medication, lifestyle changes, regular monitoring',
             'Chronic', 'en'),
            ('सामान्य सर्दी', 'बहती नाक, छींक, खांसी, हल्का बुखार, गले में खराश',
             'हाथ बार-बार धोएं, बीमार लोगों से दूरी बनाए रखें, अच्छी स्वच्छता बनाए रखें',
             'आराम करें, पानी पिएं, नमकीन पानी की बूंदें उपयोग करें, लक्षण बने रहने पर डॉक्टर से मिलें',
             'हल्का', 'hi'),
            
            ('मधुमेह टाइप 2', 'अधिक प्यास, बार-बार पेशाब, धुंधली दृष्टि, थकान, घाव धीरे भरना',
             'स्वस्थ वजन बनाए रखें, नियमित व्यायाम, संतुलित आहार, चीनी का सेवन सीमित करें',
             'निर्धारित दवा, रक्त शर्करा की निगरानी, जीवनशैली में बदलाव',
             'दीर्घकालिक', 'hi'),
            
            ('उच्च रक्तचाप', 'अक्सर कोई लक्षण नहीं, कभी-कभी सिरदर्द, चक्कर आना, सीने में दर्द',
             'नियमित व्यायाम, नमक कम करें, स्वस्थ वजन बनाए रखें, शराब सीमित करें',
             'दवा, जीवनशैली में बदलाव, नियमित निगरानी',
             'दीर्घकालिक', 'hi'),
        ]
        
        vaccination_data = [
            ('BCG', 'Newborn (at birth)', 'Single dose at birth',
             'Protects against tuberculosis', 'Mild fever, swelling at injection site', 'en'),
            
            ('DPT', 'Infants', '6, 10, 14 weeks; boosters at 18 months, 5-6 years',
             'Protects against Diphtheria, Pertussis (Whooping cough), Tetanus',
             'Fever, soreness, swelling at injection site', 'en'),
            
            ('Polio (OPV)', 'Infants', '6, 10, 14 weeks; boosters at 18 months, 5-6 years',
             'Protects against Poliomyelitis', 'Very rare allergic reactions', 'en'),
            
            ('MMR', 'Children', '12-15 months and 4-6 years',
             'Protects against Measles, Mumps, Rubella', 'Mild fever, rash', 'en'),
            ('BCG', 'नवजात (जन्म के समय)', 'जन्म के समय एक खुराक',
             'तपेदिक से सुरक्षा प्रदान करता है', 'हल्का बुखार, इंजेक्शन की जगह सूजन', 'hi'),
            
            ('DPT', 'शिशु', '6, 10, 14 सप्ताह; बूस्टर 18 महीने, 5-6 साल',
             'डिप्थीरिया, कुकुर खांसी, टिटनेस से सुरक्षा',
             'बुखार, दर्द, इंजेक्शन की जगह सूजन', 'hi'),
            
            ('पोलियो (OPV)', 'शिशु', '6, 10, 14 सप्ताह; बूस्टर 18 महीने, 5-6 साल',
             'पोलियोमाइलाइटिस से सुरक्षा', 'बहुत दुर्लभ एलर्जी प्रतिक्रियाएं', 'hi'),
            
            ('MMR', 'बच्चे', '12-15 महीने और 4-6 साल',
             'खसरा, कंठमाला, रूबेला से सुरक्षा', 'हल्का बुखार, दाने', 'hi'),
        ]
        
        self.cursor.execute('SELECT COUNT(*) FROM diseases')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                'INSERT INTO diseases (name, symptoms, prevention, treatment, severity, language) VALUES (?, ?, ?, ?, ?, ?)',
                diseases_data
            )
            logger.info("Diseases data loaded")
        
        self.cursor.execute('SELECT COUNT(*) FROM vaccinations')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                'INSERT INTO vaccinations (vaccine_name, age_group, schedule, description, side_effects, language) VALUES (?, ?, ?, ?, ?, ?)',
                vaccination_data
            )
            logger.info("Vaccination data loaded")
        
        self.conn.commit()
    
    def search_diseases(self, query: str, language: str = 'en') -> List[Dict]:
        """Search for diseases based on symptoms or name"""
        query = query.lower()
        self.cursor.execute('''
            SELECT name, symptoms, prevention, treatment, severity 
            FROM diseases 
            WHERE language = ? AND (
                LOWER(name) LIKE ? OR 
                LOWER(symptoms) LIKE ? OR 
                LOWER(prevention) LIKE ?
            )
        ''', (language, f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = []
        for row in self.cursor.fetchall():
            results.append({
                'name': row[0],
                'symptoms': row[1],
                'prevention': row[2],
                'treatment': row[3],
                'severity': row[4]
            })
        return results
    
    def get_vaccination_schedule(self, age_group: str = None, language: str = 'en') -> List[Dict]:
        """Get vaccination schedule"""
        if age_group:
            self.cursor.execute('''
                SELECT vaccine_name, age_group, schedule, description, side_effects
                FROM vaccinations 
                WHERE language = ? AND LOWER(age_group) LIKE ?
            ''', (language, f'%{age_group.lower()}%'))
        else:
            self.cursor.execute('''
                SELECT vaccine_name, age_group, schedule, description, side_effects
                FROM vaccinations 
                WHERE language = ?
            ''', (language,))
        
        results = []
        for row in self.cursor.fetchall():
            results.append({
                'vaccine_name': row[0],
                'age_group': row[1],
                'schedule': row[2],
                'description': row[3],
                'side_effects': row[4]
            })
        return results
    
    def save_chat_history(self, user_message: str, bot_response: str, language: str, user_id: str = None):
        """Save chat interaction to database"""
        self.cursor.execute('''
            INSERT INTO chat_history (user_message, bot_response, language, user_id)
            VALUES (?, ?, ?, ?)
        ''', (user_message, bot_response, language, user_id))
        self.conn.commit()

class AIHealthAssistant:
    """AI-powered health assistant using Gemini"""
    
    def __init__(self, health_db: HealthDatabase):
        self.health_db = health_db
        self.system_prompt = {
            'en': """You are a healthcare education assistant for rural and semi-urban populations. 
            Provide accurate, simple, and culturally appropriate health information. 
            Always emphasize consulting healthcare professionals for serious conditions.
            
            IMPORTANT FORMATTING RULES:
            - Format your responses using clear bullet points for easy readability
            - Use "•" for main points and "-" for sub-points
            - Break down advice into actionable steps
            - Start each major section with a clear heading
            - Keep each bullet point concise (1-2 sentences max)
            
            RESPONSE STRUCTURE:
            1. Brief greeting or acknowledgment
            2. Main advice in bullet point format
            3. Emergency contact info if relevant
            4. Reminder to consult healthcare professionals
            
            Include emergency contact (108) when appropriate.""",
            
            'hi': """आप ग्रामीण और अर्ध-शहरी आबादी के लिए एक स्वास्थ्य शिक्षा सहायक हैं।
            सटीक, सरल और सांस्कृतिक रूप से उपयुक्त स्वास्थ्य जानकारी प्रदान करें।
            हमेशा गंभीर स्थितियों के लिए स्वास्थ्य पेशेवरों से सलाह लेने पर जोर दें।
            जवाब संक्षिप्त और समझने में आसान रखें।
            उपयुक्त होने पर आपातकालीन संपर्क (108) शामिल करें।"""
        }
    
    def generate_response(self, user_message: str, language: str = 'en') -> str:
        """Generate AI response using Gemini and health database"""
        try:
            db_results = self.search_health_database(user_message, language)
            
            context = self.system_prompt[language]
            if db_results:
                context += f"\n\nRelevant health information from database:\n{db_results}"
            
            prompt = f"""{context}

User question: {user_message}

IMPORTANT: Format your response using this structure:
1. Start with a friendly greeting (like "Namaste! That's a very good question.")
2. Provide main advice in clear bullet points using "•" symbol
3. Each bullet should be actionable and specific
4. End with encouragement and reminder about professional consultation

Example format for health advice:
• Eat Healthy: Include specific foods and what to avoid
• Stay Active: Mention specific activities and duration  
• Maintain Health: Give specific tips for monitoring
• Regular Check-ups: Explain when and why to see healthcare providers

Keep each bullet point concise but informative.
Please provide a helpful response in {'Hindi' if language == 'hi' else 'English'}:"""
            
            response = model.generate_content(prompt)
            
            if response.text:
                return self.format_response(response.text, language)
            else:
                return self.get_fallback_response(language)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self.get_fallback_response(language)
    
    def search_health_database(self, query: str, language: str) -> str:
        """Search health database for relevant information"""
        results = []
        
        diseases = self.health_db.search_diseases(query, language)
        if diseases:
            results.append("Disease Information:")
            for disease in diseases[:2]: 
                results.append(f"- {disease['name']}: {disease['symptoms']}")
        
        if any(keyword in query.lower() for keyword in ['vaccine', 'vaccination', 'immunization', 'टीका', 'टीकाकरण']):
            vaccines = self.health_db.get_vaccination_schedule(language=language)
            if vaccines:
                results.append("\nVaccination Information:")
                for vaccine in vaccines[:3]: 
                    results.append(f"- {vaccine['vaccine_name']}: {vaccine['schedule']}")
        
        return "\n".join(results) if results else ""
    
    def format_response(self, response: str, language: str) -> str:
        """Format and validate AI response"""
        response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)
        response = re.sub(r'\*([^*]+)\*', r'\1', response)
        
        serious_keywords = {
            'en': ['chest pain', 'difficulty breathing', 'severe', 'emergency', 'blood', 'unconscious'],
            'hi': ['सीने में दर्द', 'सांस लेने में कठिनाई', 'गंभीर', 'आपातकाल', 'खून', 'बेहोश']
        }
        
        if any(keyword in response.lower() for keyword in serious_keywords[language]):
            emergency_note = {
                'en': "\n⚠️ For medical emergencies, call 108 immediately.",
                'hi': "\n⚠️ आपातकालीन स्थिति में तुरंत 108 पर कॉल करें।"
            }
            if emergency_note[language] not in response:
                response += emergency_note[language]
        
        return response
    
    def get_fallback_response(self, language: str) -> str:
        """Provide fallback response when AI fails"""
        fallback = {
            'en': "I'm sorry, I couldn't process your request right now. Please try rephrasing your question or contact a healthcare professional for urgent matters. For emergencies, call 108.",
            'hi': "मुझे खेद है, मैं अभी आपके अनुरोध को संसाधित नहीं कर सका। कृपया अपने प्रश्न को दोबारा पूछें या तत्काल मामलों के लिए एक स्वास्थ्य पेशेवर से संपर्क करें। आपातकाल के लिए 108 पर कॉल करें।"
        }
        return fallback[language]

health_db = HealthDatabase()
ai_assistant = AIHealthAssistant(health_db)

@app.route('/')
def index():
    """Serve the main chatbot interface"""
    return "Healthcare Chatbot Backend is running! Use /api/chat endpoint for interactions."

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        bot_response = ai_assistant.generate_response(user_message, language)
        
        health_db.save_chat_history(user_message, bot_response, language, user_id)
        
        return jsonify({
            'response': bot_response,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Get disease information"""
    query = request.args.get('q', '')
    language = request.args.get('lang', 'en')
    
    results = health_db.search_diseases(query, language)
    return jsonify({
        'diseases': results,
        'total': len(results)
    })

@app.route('/api/vaccinations', methods=['GET'])
def get_vaccinations():
    """Get vaccination schedule"""
    age_group = request.args.get('age_group')
    language = request.args.get('lang', 'en')
    
    results = health_db.get_vaccination_schedule(age_group, language)
    return jsonify({
        'vaccinations': results,
        'total': len(results)
    })

@app.route('/api/health-tips', methods=['GET'])
def get_health_tips():
    """Get health tips"""
    category = request.args.get('category', '')
    language = request.args.get('lang', 'en')
    tips = {
        'en': [
            "Drink at least 8 glasses of water daily",
            "Exercise for 30 minutes daily",
            "Wash hands frequently to prevent infections",
            "Get adequate sleep (7-9 hours)",
            "Eat a balanced diet with fruits and vegetables"
        ],
        'hi': [
            "दिन में कम से कम 8 गिलास पानी पिएं",
            "दैनिक 30 मिनट व्यायाम करें",
            "संक्रमण से बचने के लिए हाथ बार-बार धोएं",
            "पर्याप्त नींद लें (7-9 घंटे)",
            "फल और सब्जियों के साथ संतुलित आहार लें"
        ]
    }
    
    return jsonify({
        'tips': tips[language],
        'language': language
    })

@app.route('/api/emergency', methods=['GET'])
def emergency_info():
    """Get emergency contact information"""
    language = request.args.get('lang', 'en')
    
    emergency_info = {
        'en': {
            'ambulance': '108',
            'police': '100',
            'fire': '101',
            'message': 'For medical emergencies, call 108 immediately. This is a free service available 24/7 across India.'
        },
        'hi': {
            'ambulance': '108',
            'police': '100',
            'fire': '101',
            'message': 'आपातकालीन स्थिति में तुरंत 108 पर कॉल करें। यह भारत में 24/7 उपलब्ध एक निःशुल्क सेवा है।'
        }
    }
    
    return jsonify(emergency_info[language])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)