from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import json
import re
from datetime import datetime
import logging
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY") ) 
model = genai.GenerativeModel('gemini-2.5-flash')

class HealthDatabase:
    """Manages the health database and AI interactions."""
    
    def __init__(self):
        """Initializes the database connection and loads initial data."""
        self.conn = sqlite3.connect('health_data.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_database()
        self.load_health_data()

    def init_database(self):
        """Creates tables if they don't exist."""
        try:
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
            logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")

    def load_health_data(self):
        """Loads sample health data into the database if it's empty."""
        diseases_data = [
            # English
            ('Common Cold', 'Runny nose, sneezing, cough, mild fever, sore throat', 'Wash hands frequently, avoid close contact with sick people, maintain good hygiene', 'Rest, stay hydrated, use saline nasal drops, consult doctor if symptoms persist', 'Mild', 'en'),
            ('Diabetes Type 2', 'Increased thirst, frequent urination, blurred vision, fatigue, slow healing wounds', 'Maintain healthy weight, regular exercise, balanced diet, limit sugar intake', 'Medication as prescribed, blood sugar monitoring, lifestyle changes', 'Chronic', 'en'),
            ('Hypertension', 'Often no symptoms, sometimes headache, dizziness, chest pain', 'Regular exercise, reduce sodium intake, maintain healthy weight, limit alcohol', 'Medication, lifestyle changes, regular monitoring', 'Chronic', 'en'),
            # Hindi
            ('सामान्य सर्दी', 'बहती नाक, छींक, खांसी, हल्का बुखार, गले में खराश', 'हाथ बार-बार धोएं, बीमार लोगों से दूरी बनाए रखें, अच्छी स्वच्छता बनाए रखें', 'आराम करें, पानी पिएं, नमकीन पानी की बूंदें उपयोग करें, लक्षण बने रहने पर डॉक्टर से मिलें', 'हल्का', 'hi'),
            ('मधुमेह टाइप 2', 'अधिक प्यास, बार-बार पेशाब, धुंधली दृष्टि, थकान, घाव धीरे भरना', 'स्वस्थ वजन बनाए रखें, नियमित व्यायाम, संतुलित आहार, चीनी का सेवन सीमित करें', 'निर्धारित दवा, रक्त शर्करा की निगरानी, जीवनशैली में बदलाव', 'दीर्घकालिक', 'hi'),
            ('उच्च रक्तचाप', 'अक्सर कोई लक्षण नहीं, कभी-कभी सिरदर्द, चक्कर आना, सीने में दर्द', 'नियमित व्यायाम, नमक कम करें, स्वस्थ वजन बनाए रखें, शराब सीमित करें', 'दवा, जीवनशैली में बदलाव, नियमित निगरानी', 'दीर्घकालिक', 'hi'),
            # Bengali
            ('সাধারণ সর্দি', 'নাক দিয়ে পানি পড়া, হাঁচি, কাশি, হালকা জ্বর, গলা ব্যথা', 'হাত ঘন ঘন ধোবেন, অসুস্থ মানুষের কাছ থেকে দূরে থাকবেন, ভালো স্বাস্থ্যবিধি বজায় রাখবেন', 'বিশ্রাম নিন, জল পান করুন, স্যালাইন নাকে ড্রপ ব্যবহার করুন, উপসর্গ বজায় থাকলে ডাক্তারের সাথে পরামর্শ করুন', 'হালকা', 'bn'),
            # Tamil
            ('சாதாரண சளி', 'மூக்கு ஒழுகுதல், தும்மல், இருமல், லேசான காய்ச்சல், தொண்டை புண்', 'கைகளை அடிக்கடி கழுவவும், நோய்வாய்ப்பட்டவர்களுடன் நெருங்கிய தொடர்பைத் தவிர்க்கவும், நல்ல சுகாதாரத்தைப் பராமரிக்கவும்', 'ஓய்வு எடுக்கவும், நீரேற்றமாக இருக்கவும், சலைன் மூக்கு சொட்டுகளை பயன்படுத்தவும், அறிகுறிகள் தொடர்ந்தால் மருத்துவரை அணுகவும்', 'லேசானது', 'ta'),
            # Telugu
            ('సాధారణ జలుబు', 'ముక్కు కారడం, తుమ్ములు, దగ్గు, తేలికపాటి జ్వరం, గొంతు నొప్పి', 'చేతులు తరచుగా కడగాలి, అనారోగ్యంతో ఉన్న వారితో దగ్గరి సంబంధం నివారించండి, మంచి పరిశుభ్రత పాటించండి', 'విశ్రాంతి తీసుకోండి, నీరు తాగండి, సెలైన్ నాసల్ డ్రాప్స్ వాడండి, లక్షణాలు కొనసాగితే వైద్యుడిని సంప్రదించండి', 'తేలికపాటి', 'te'),
            # Marathi
            ('सामान्य सर्दी', 'नाक वाहणे, शिंका येणे, खोकला, सौम्य ताप, घसा खवखवणे', 'वारंवार हात धुवा, आजारी लोकांपासून दूर रहा, चांगली स्वच्छता राखा', 'विश्रांती घ्या, हायड्रेटेड रहा, सलाईन नाकातले थेंब वापरा, लक्षणे कायम राहिल्यास डॉक्टरांचा सल्ला घ्या', 'सौम्य', 'mr'),
            # Gujarati
            ('સામાન્ય શરદી', 'નાક વહેવું, છીંક, ખાંસી, હળવો તાવ, ગળામાં દુખાવો', 'હાથ વારંવાર ધોવા, માંદા લોકોના સંપર્કમાં આવવાનું ટાળો, સારી સ્વચ્છતા જાળવો', 'આરામ કરો, હાઇડ્રેટેડ રહો, સેલાઇન નાકના ટીપાંનો ઉપયોગ કરો, લક્ષણો ચાલુ રહે તો ડૉક્ટરની સલાહ લો', 'હળવી', 'gu'),
            # Kannada
            ('ಸಾಮಾನ್ಯ ಶೀತ', 'ಮೂಗಿನಿಂದ ನೀರು ಸೋರುವುದು, ಸೀನುವುದು, ಕೆಮ್ಮು, ಸಣ್ಣ ಜ್ವರ, ಗಂಟಲು ನೋವು', 'ಕೈಗಳನ್ನು ಆಗಾಗ್ಗೆ ತೊಳೆಯಿರಿ, ಅನಾರೋಗ್ಯ ಪೀಡಿತರೊಂದಿಗೆ ನಿಕಟ ಸಂಪರ್ಕವನ್ನು ತಪ್ಪಿಸಿ, ಉತ್ತಮ ನೈರ್ಮಲ್ಯವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ', 'ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ, ಜಲಸಮೃದ್ಧಿಯಾಗಿರಿ, ಲವಣಯುಕ್ತ ಮೂಗಿನ ಹನಿಗಳನ್ನು ಬಳಸಿ, ಲಕ್ಷಣಗಳು ಮುಂದುವರಿದರೆ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ', 'ಸಾಮಾನ್ಯ', 'kn'),
            # Malayalam
            ('സാധാരണ ജലദോഷം', 'മൂക്കൊലിപ്പ്, തുമ്മൽ, ചുമ, നേരിയ പനി, തൊണ്ടവേദന', 'കൈകൾ ഇടയ്ക്കിടെ കഴുകുക, രോഗികളുമായി അടുത്ത സമ്പർക്കം ഒഴിവാക്കുക, നല്ല ശുചിത്വം പാലിക്കുക', 'വിശ്രമിക്കുക, ജലാംശം നിലനിർത്തുക, സലൈൻ നാസൽ തുള്ളികൾ ഉപയോഗിക്കുക, ലക്ഷണങ്ങൾ തുടർന്നാൽ ഡോക്ടറെ സമീപിക്കുക', 'ചെറിയ', 'ml'),
            # Punjabi
            ('ਆਮ ਜ਼ੁਕਾਮ', 'ਨੱਕ ਵਗਣਾ, ਛਿੱਕਾਂ, ਖੰਘ, ਹਲਕਾ ਬੁਖਾਰ, ਗਲੇ ਵਿੱਚ ਖਰਾਸ਼', 'ਹੱਥਾਂ ਨੂੰ ਵਾਰ-ਵਾਰ ਧੋਵੋ, ਬੀਮਾਰ ਲੋਕਾਂ ਦੇ ਨੇੜੇ ਨਾ ਜਾਓ, ਚੰਗੀ ਸਫਾਈ ਰੱਖੋ', 'ਆਰਾਮ ਕਰੋ, ਹਾਈਡ੍ਰੇਟਿਡ ਰਹੋ, ਸਲਾਈਨ ਨੱਕ ਦੀਆਂ ਬੂੰਦਾਂ ਦੀ ਵਰਤੋਂ ਕਰੋ, ਜੇ ਲੱਛਣ ਬਣੇ ਰਹਿਣ ਤਾਂ ਡਾਕਟਰ ਦੀ ਸਲਾਹ ਲਓ', 'ਹਲਕਾ', 'pa'),
            # Oriya
            ('ସାଧାରଣ ଶୀତ', 'ନାକ ବହିବା, ଛିଙ୍କ, କାଶ, ହାଲୁକା ଜ୍ୱର, ଗଳା ଦରଜ', 'ବାରମ୍ବାର ହାତ ଧୁଅନ୍ତୁ, ଅସୁସ୍ଥ ଲୋକଙ୍କ ସହିତ ନିକଟ ସଂପର୍କରୁ ଦୂରେଇ ରୁହନ୍ତୁ, ଭଲ ସ୍ୱଚ୍ଛତା ବଜାୟ ରଖନ୍ତୁ', 'ବିଶ୍ରାମ ନିଅନ୍ତୁ, ଜଳପାନ କରନ୍ତୁ, ସାଲାଇନ୍ ନାକର ଡ୍ରପ୍ସ ବ୍ୟବହାର କରନ୍ତୁ, ଯଦି ଲକ୍ଷଣ ରହେ ତେବେ ଡାକ୍ତରଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ', 'ସାମାନ୍ୟ', 'or'),
            # Assamese
            ('সাধাৰণ চৰ্দি', 'নাকেৰে পানী ওলোৱা, হাঁচি, কাহ, সামান্য জ্বৰ, ডিঙিৰ বিষ', 'হাত নিয়মীয়াকৈ ধুব, অসুস্থ মানুহৰ ওচৰলৈ যোৱাৰ পৰা বিৰত থাকক, ভাল স্বাস্থ্যবিধি বজাই ৰাখক', 'বিশ্রাম লওক, পানী খাই থাকক, ছালাইন নাজল ড্ৰপ ব্যৱহাৰ কৰক, লক্ষণসমূহ অব্যাহত থাকিলে চিকিৎসকৰ পৰামৰ্শ লওক', 'সাধাৰণ', 'as'),
        ]
        
        vaccination_data = [
            # English
            ('BCG', 'Newborn (at birth)', 'Single dose at birth', 'Protects against tuberculosis', 'Mild fever, swelling at injection site', 'en'),
            ('DPT', 'Infants', '6, 10, 14 weeks; boosters at 18 months, 5-6 years', 'Protects against Diphtheria, Pertussis (Whooping cough), Tetanus', 'Fever, soreness, swelling at injection site', 'en'),
            ('Polio (OPV)', 'Infants', '6, 10, 14 weeks; boosters at 18 months, 5-6 years', 'Protects against Poliomyelitis', 'Very rare allergic reactions', 'en'),
            ('MMR', 'Children', '12-15 months and 4-6 years', 'Protects against Measles, Mumps, Rubella', 'Mild fever, rash', 'en'),
            # Hindi
            ('BCG', 'नवजात (जन्म के समय)', 'जन्म के समय एक खुराक', 'तपेदिक से सुरक्षा प्रदान करता है', 'हल्का बुखार, इंजेक्शन की जगह सूजन', 'hi'),
            ('DPT', 'शिशु', '6, 10, 14 सप्ताह; बूस्टर 18 महीने, 5-6 साल', 'डिप्थीरिया, कुकुर खांसी, टिटनेस से सुरक्षा', 'बुखार, दर्द, इंजेक्शन की जगह सूजन', 'hi'),
            ('पोलियो (OPV)', 'शिशु', '6, 10, 14 सप्ताह; बूस्टर 18 महीने, 5-6 साल', 'पोलियोमाइलाइटिस से सुरक्षा', 'बहुत दुर्लभ एलर्जी प्रतिक्रियाएं', 'hi'),
            ('MMR', 'बच्चे', '12-15 महीने और 4-6 साल', 'खसरा, कंठमाला, रूबेला से सुरक्षा', 'हल्का बुखार, दाने', 'hi'),
            # Bengali
            ('বিসিজি', 'নবজাতক (জন্মের সময়)', 'জন্মের সময় এক ডোজ', 'যক্ষ্মা থেকে রক্ষা করে', 'হালকা জ্বর, ইনজেকশন সাইটে ফোলা', 'bn'),
            # Tamil
            ('பிசிஜி', 'புதிதாகப் பிறந்த குழந்தை (பிறக்கும் போது)', 'பிறக்கும் போது ஒரு டோஸ்', 'காசநோயிலிருந்து பாதுகாக்கிறது', 'லேசான காய்ச்சல், ஊசி போட்ட இடத்தில் வீக்கம்', 'ta'),
            # Telugu
            ('బిసిజి', 'శిశువు (పుట్టినప్పుడు)', 'పుట్టినప్పుడు ఒక మోతాదు', 'క్షయ వ్యాధి నుండి రక్షిస్తుంది', 'తేలికపాటి జ్వరం, ఇంజెక్షన్ చేసిన చోట వాపు', 'te'),
            # Marathi
            ('बीसीजी', 'नवजात (जन्माच्या वेळी)', 'जन्माच्या वेळी एक डोस', 'क्षयरोगापासून संरक्षण करते', 'हलका ताप, इंजेक्शनच्या जागी सूज', 'mr'),
            # Gujarati
            ('બીસીજી', 'નવજાત (જન્મ સમયે)', 'જન્મ સમયે એક માત્રા', 'ક્ષય રોગથી બચાવે છે', 'હળવો તાવ, ઇન્જેક્શનની જગ્યાએ સોજો', 'gu'),
            # Kannada
            ('ಬಿಸಿಜಿ', 'ನವಜಾತ ಶಿಶು (ಹುಟ್ಟಿದಾಗ)', 'ಹುಟ್ಟಿದಾಗ ಒಂದೇ ಡೋಸ್', 'ಕ್ಷಯ ರೋಗದಿಂದ ರಕ್ಷಿಸುತ್ತದೆ', 'ಸಣ್ಣ ಜ್ವರ, ಚುಚ್ಚುಮದ್ದಿನ ಸ್ಥಳದಲ್ಲಿ ಊತ', 'kn'),
            # Malayalam
            ('ബിസിജി', 'നവജാത ശിശു (ജനിക്കുമ്പോൾ)', 'ജനന സമയത്ത് ഒറ്റ ഡോസ്', 'ക്ഷയരോഗത്തിൽ നിന്ന് സംരക്ഷിക്കുന്നു', 'ചെറിയ പനി, കുത്തിവച്ച സ്ഥലത്ത് വീക്കം', 'ml'),
            # Punjabi
            ('ਬੀਸੀਜੀ', 'ਨਵਜੰਮੇ ਬੱਚੇ (ਜਨਮ ਸਮੇਂ)', 'ਜਨਮ ਸਮੇਂ ਇੱਕ ਖੁਰਾਕ', 'ਤਪਦਿਕ ਤੋਂ ਬਚਾਉਂਦਾ ਹੈ', 'ਹਲਕਾ ਬੁਖਾਰ, ਟੀਕੇ ਵਾਲੀ ਥਾਂ ਤੇ ਸੋਜ', 'pa'),
            # Oriya
            ('ବିସିଜି', 'ନବଜାତ (ଜନ୍ମ ସମୟରେ)', 'ଜନ୍ମ ସମୟରେ ଗୋଟିଏ ଡୋଜ', 'ଯକ୍ଷ୍ମା ରୋଗରୁ ରକ୍ଷା କରେ', 'ହାଲୁକା ଜ୍ୱର, ଇଞ୍ଜେକ୍ସନ୍ ସ୍ଥାନରେ ଫୁଲା', 'or'),
            # Assamese
            ('বিচিজি', 'নৱজাত (জন্মৰ সময়ত)', 'জন্মৰ সময়ত এটা মাত্ৰা', 'যক্ষ্মাৰ পৰা সুৰক্ষা দিয়ে', 'সামান্য জ্বৰ, ইনজেকচনৰ ঠাইত ফুলা', 'as'),
        ]
        
        self.cursor.execute('SELECT COUNT(*) FROM diseases')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany('INSERT INTO diseases (name, symptoms, prevention, treatment, severity, language) VALUES (?, ?, ?, ?, ?, ?)', diseases_data)
            logger.info("Diseases data loaded.")
        
        self.cursor.execute('SELECT COUNT(*) FROM vaccinations')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany('INSERT INTO vaccinations (vaccine_name, age_group, schedule, description, side_effects, language) VALUES (?, ?, ?, ?, ?, ?)', vaccination_data)
            logger.info("Vaccination data loaded.")
        
        self.conn.commit()

    def search_diseases(self, query: str, language: str = 'en') -> List[Dict]:
        """Searches for diseases based on keywords in name, symptoms, or prevention."""
        query = query.lower()
        self.cursor.execute('''
            SELECT name, symptoms, prevention, treatment, severity 
            FROM diseases 
            WHERE language = ? AND (LOWER(name) LIKE ? OR LOWER(symptoms) LIKE ? OR LOWER(prevention) LIKE ?)
        ''', (language, f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = [{'name': r[0], 'symptoms': r[1], 'prevention': r[2], 'treatment': r[3], 'severity': r[4]} for r in self.cursor.fetchall()]
        return results
    
    def get_vaccination_schedule(self, age_group: str = None, language: str = 'en') -> List[Dict]:
        """Retrieves vaccination schedule based on age group or all."""
        if age_group:
            self.cursor.execute('''
                SELECT vaccine_name, age_group, schedule, description, side_effects
                FROM vaccinations 
                WHERE language = ? AND LOWER(age_group) LIKE ?
            ''', (language, f'%{age_group.lower()}%'))
        else:
            self.cursor.execute('SELECT vaccine_name, age_group, schedule, description, side_effects FROM vaccinations WHERE language = ?', (language,))
        
        results = [{'vaccine_name': r[0], 'age_group': r[1], 'schedule': r[2], 'description': r[3], 'side_effects': r[4]} for r in self.cursor.fetchall()]
        return results

    def save_chat_history(self, user_message: str, bot_response: str, language: str, user_id: str = None):
        """Saves a chat interaction to the database."""
        try:
            self.cursor.execute('''
                INSERT INTO chat_history (user_message, bot_response, language, user_id)
                VALUES (?, ?, ?, ?)
            ''', (user_message, bot_response, language, user_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving chat history: {e}")

class AIHealthAssistant:
    """Handles AI-powered health assistant logic using Gemini."""
    
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
            
            Include emergency contact (108) when appropriate.
            If the user asks for vaccinations, provide the full list from the database.
            For any mention of emergency symptoms (chest pain, severe bleeding, unconsciousness),
            immediately and prominently advise calling 108.
            Respond in a conversational, friendly, and reassuring tone.
            """,
            'hi': """आप ग्रामीण और अर्ध-शहरी आबादी के लिए एक स्वास्थ्य शिक्षा सहायक हैं।
            सटीक, सरल और सांस्कृतिक रूप से उपयुक्त स्वास्थ्य जानकारी प्रदान करें।
            हमेशा गंभीर स्थितियों के लिए स्वास्थ्य पेशेवरों से सलाह लेने पर जोर दें।
            जवाब संक्षिप्त और समझने में आसान रखें।
            उपयुक्त होने पर आपातकालीन संपर्क (108) शामिल करें।
            यदि उपयोगकर्ता टीकाकरण के बारे में पूछता है, तो डेटाबेस से पूरी सूची प्रदान करें।
            किसी भी आपातकालीन लक्षणों (सीने में दर्द, गंभीर रक्तस्राव, बेहोशी) का उल्लेख होने पर,
            तुरंत और प्रमुखता से 108 पर कॉल करने की सलाह दें।
            बातचीत के लहजे में, दोस्ताना और आश्वस्त करने वाले अंदाज़ में जवाब दें।
            """,
            'bn': """আপনি গ্রামীণ এবং আধা-শহুরে জনসংখ্যার জন্য একজন স্বাস্থ্যসেবা শিক্ষা সহায়ক।
            সঠিক, সহজ এবং সাংস্কৃতিকভাবে উপযুক্ত স্বাস্থ্য তথ্য প্রদান করুন।
            গুরুতর অবস্থার জন্য সর্বদা স্বাস্থ্যসেবা পেশাদারদের সাথে পরামর্শ করার উপর জোর দিন।
            প্রতিক্রিয়া সংক্ষিপ্ত এবং সহজে বোঝা যায় এমন রাখবেন।
            উপযুক্ত হলে জরুরি যোগাযোগ (108) অন্তর্ভুক্ত করুন।
            যদি ব্যবহারকারী টিকাদান সম্পর্কে জিজ্ঞাসা করে, তাহলে ডাটাবেস থেকে সম্পূর্ণ তালিকা প্রদান করুন।
            কোনো জরুরি উপসর্গের (বুকে ব্যথা, গুরুতর রক্তপাত, অজ্ঞান হয়ে যাওয়া) উল্লেখ হলে,
            অবিলম্বে এবং প্রধানভাবে 108 নম্বরে কল করার পরামর্শ দিন।
            কথোপকথনের, বন্ধুত্বপূর্ণ এবং আশ্বস্ত করার মতো স্বরে সাড়া দিন।
            """,
            'ta': """நீங்கள் கிராமப்புற மற்றும் பகுதி-நகர்ப்புற மக்களுக்கான ஒரு சுகாதார கல்வி உதவியாளர்.
            சரியான, எளிமையான மற்றும் கலாச்சாரத்திற்கு ஏற்ற சுகாதார தகவலை வழங்கவும்.
            கடுமையான நிலைகளுக்கு எப்போதும் சுகாதார நிபுணர்களை அணுக வலியுறுத்தவும்.
            பதில்களை சுருக்கமாகவும், எளிதில் புரிந்துகொள்ளக்கூடியதாகவும் வைத்திருக்கவும்.
            பொருத்தமானால் அவசர தொடர்பு (108) எண்ணை சேர்க்கவும்.
            பயனர் தடுப்பூசிகள் பற்றி கேட்டால், தரவுத்தளத்தில் இருந்து முழு பட்டியலையும் வழங்கவும்.
            அவசர அறிகுறிகளைப் (மார்பு வலி, கடுமையான இரத்தப்போக்கு, மயக்கம்) பற்றி ஏதேனும் குறிப்பிட்டால்,
            உடனடியாகவும் முக்கியமாகவும் 108-ஐ அழைக்க அறிவுறுத்தவும்.
            ஒரு உரையாடல், நட்பு மற்றும் உறுதியளிக்கும் தொனியில் பதிலளிக்கவும்.
            """,
            'te': """మీరు గ్రామీణ మరియు సెమీ-అర్బన్ జనాభా కోసం ఒక ఆరోగ్య విద్య సహాయకుడు.
            ఖచ్చితమైన, సులభమైన, మరియు సాంస్కృతికంగా అనుకూలమైన ఆరోగ్య సమాచారాన్ని అందించండి.
            తీవ్రమైన పరిస్థితుల కోసం ఎల్లప్పుడూ ఆరోగ్య సంరక్షణ నిపుణులను సంప్రదించమని నొక్కి చెప్పండి.
            
            ముఖ్యమైన ఫార్మేటింగ్ నియమాలు:
            - సులభంగా చదవగలిగేలా స్పష్టమైన బుల్లెట్ పాయింట్లను ఉపయోగించండి
            - ముఖ్య పాయింట్ల కోసం "•" మరియు ఉప-పాయింట్ల కోసం "-" ఉపయోగించండి
            - సలహాను క్రియాశీల దశల్లోకి విభజించండి
            - ప్రతి ముఖ్య విభాగాన్ని స్పష్టమైన శీర్షికతో ప్రారంభించండి
            - ప్రతి బుల్లెట్ పాయింట్‌ను సంక్షిప్తంగా ఉంచండి (గరిష్టంగా 1-2 వాక్యాలు)
            
            ప్రతిస్పందన నిర్మాణం:
            1. సంక్షిప్త అభివాదన లేదా అంగీకరణ
            2. బుల్లెట్ పాయింట్ ఫార్మేట్‌లో ముఖ్య సలహా
            3. సంబంధిత ఉంటే అత్యవసర సంప్రదింపు సమాచారం
            4. ఆరోగ్య నిపుణులను సంప్రదించాలని గుర్తు చేయడం
            
            సముచితమైనప్పుడు అత్యవసర సంప్రదింపు (108) నంబర్‌ను చేర్చండి.
            వినియోగదారు టీకాల గురించి అడిగితే, డేటాబేస్ నుండి పూర్తి జాబితాను అందించండి.
            ఏదైనా అత్యవసర లక్షణాలు (ఛాతీ నొప్పి, తీవ్ర రక్తస్రావం, అపస్మారక స్థితి) గురించి ప్రస్తావించినట్లయితే,
            వెంటనే మరియు ప్రముఖంగా 108కి కాల్ చేయమని సలహా ఇవ్వండి.
            సంభాషణ శైలిలో, స్నేహపూర్వకంగా మరియు హామీ ఇచ్చే స్వరంలో ప్రతిస్పందించండి.
            """,
            'mr': """तुम्ही ग्रामीण आणि अर्ध-शहरी लोकसंख्येसाठी एक आरोग्य शिक्षण सहाय्यक आहात.
            सटीक, सोपी आणि सांस्कृतिकदृष्ट्या योग्य आरोग्य माहिती प्रदान करा.
            गंभीर परिस्थितीत नेहमी आरोग्यसेवा व्यावसायिकांचा सल्ला घेण्यावर जोर द्या.
            उत्तरे संक्षिप्त आणि समजण्यास सोपी ठेवा.
            योग्य असल्यास, आपत्कालीन संपर्क (108) समाविष्ट करा.
            जर वापरकर्त्याने लसीकरणाबद्दल विचारले, तर डेटाबेसमधील संपूर्ण यादी प्रदान करा.
            कोणत्याही आपत्कालीन लक्षणांचा (छातीत दुखणे, गंभीर रक्तस्राव, बेशुद्ध होणे) उल्लेख असल्यास,
            त्वरित आणि प्रमुखतेने 108 वर कॉल करण्याचा सल्ला द्या.
            संभाषणात्मक, मैत्रीपूर्ण आणि आश्वासक स्वरात प्रतिसाद द्या.
            """,
            'gu': """તમે ગ્રામીણ અને અર્ધ-શહેરી વસ્તી માટે આરોગ્ય શિક્ષણ સહાયક છો.
            ચોક્કસ, સરળ અને સાંસ્કૃતિક રીતે યોગ્ય આરોગ્ય માહિતી પ્રદાન કરો.
            ગંભીર પરિસ્થિતિઓ માટે હંમેશા આરોગ્ય સંભાળ વ્યાવસાયિકોની સલાહ લેવા પર ભાર મૂકો.
            પ્રતિભાવો સંક્ષિપ્ત અને સમજવામાં સરળ રાખો.
            જ્યારે યોગ્ય હોય ત્યારે કટોકટી સંપર્ક (108) શામેલ કરો.
            જો વપરાશકર્તા રસીકરણ વિશે પૂછે, તો ડેટાબેઝમાંથી સંપૂર્ણ સૂચિ પ્રદાન કરો.
            કોઈપણ કટોકટીના લક્ષણો (છાતીમાં દુખાવો, ગંભીર રક્તસ્ત્રાવ, બેભાન થવું) નો ઉલ્લેખ હોય તો,
            તરત અને મુખ્યત્વે 108 પર કૉલ કરવાની સલાહ આપો.
            વાતચીતપૂર્ણ, મૈત્રીપૂર્ણ અને આશ્વાસન આપતા સ્વરમાં પ્રતિભાવ આપો.
            """,
            'kn': """ನೀವು ಗ್ರಾಮೀಣ ಮತ್ತು ಅರೆ-ನಗರ ಪ್ರದೇಶಗಳ ಜನಸಂಖ್ಯೆಗಾಗಿ ಆರೋಗ್ಯ ಶಿಕ್ಷಣ ಸಹಾಯಕರು.
            ನಿಖರ, ಸರಳ, ಮತ್ತು ಸಾಂಸ್ಕೃತಿಕವಾಗಿ ಸೂಕ್ತವಾದ ಆರೋಗ್ಯ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸಿ.
            ಗಂಭೀರ ಪರಿಸ್ಥಿತಿಗಳಿಗಾಗಿ ಯಾವಾಗಲೂ ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಲು ಒತ್ತು ನೀಡಿ.
            ಪ್ರತಿಕ್ರಿಯೆಗಳನ್ನು ಸಂಕ್ಷಿಪ್ತ ಮತ್ತು ಸುಲಭವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವಂತೆ ಇರಿಸಿ.
            ಸೂಕ್ತವಾದರೆ ತುರ್ತು ಸಂಪರ್ಕ (108) ಅನ್ನು ಸೇರಿಸಿ.
            ಬಳಕೆದಾರರು ಲಸಿಕೆಗಳ ಬಗ್ಗೆ ಕೇಳಿದರೆ, ಡೇಟಾಬೇಸ್‌ನಿಂದ ಸಂಪೂರ್ಣ ಪಟ್ಟಿಯನ್ನು ಒದಗಿಸಿ.
            ಯಾವುದೇ ತುರ್ತು ರೋಗಲಕ್ಷಣಗಳ (ಎದೆ ನೋವು, ತೀವ್ರ ರಕ್ತಸ್ರಾವ, ಪ್ರಜ್ಞಾಹೀನತೆ) ಬಗ್ಗೆ ಉಲ್ಲೇಖಿಸಿದರೆ,
            ತಕ್ಷಣವೇ ಮತ್ತು ಪ್ರಮುಖವಾಗಿ 108 ಗೆ ಕರೆ ಮಾಡಲು ಸಲಹೆ ನೀಡಿ.
            ಸಂವಾದಾತ್ಮಕ, ಸ್ನೇಹಪೂರ್ವಕ ಮತ್ತು ಭರವಸೆಯ ಧ್ವನಿಯಲ್ಲಿ ಪ್ರತಿಕ್ರಿಯಿಸಿ.
            """,
            'ml': """നിങ്ങൾ ഗ്രാമീണ, അർദ്ധ-നഗര ജനങ്ങൾക്കായുള്ള ഒരു ആരോഗ്യ വിദ്യാഭ്യാസ സഹായിയാണ്.
            കൃത്യവും, ലളിതവും, സാംസ്കാരികമായി അനുയോജ്യവുമായ ആരോഗ്യ വിവരങ്ങൾ നൽകുക.
            ഗുരുതരമായ അവസ്ഥകൾക്ക് എല്ലായ്പ്പോഴും ആരോഗ്യ വിദഗ്ദ്ധരെ സമീപിക്കാൻ ഊന്നൽ നൽകുക.
            പ്രതികരണങ്ങൾ സംക്ഷിപ്തവും എളുപ്പത്തിൽ മനസ്സിലാക്കാവുന്നതും ആയിരിക്കണം.
            ഉചിതമെങ്കിൽ അടിയന്തര ബന്ധപ്പെടാനുള്ള നമ്പർ (108) ഉൾപ്പെടുത്തുക.
            ഉപയോക്താവ് വാക്സിനേഷനുകളെക്കുറിച്ച് ചോദിച്ചാൽ, ഡാറ്റാബേസിൽ നിന്ന് പൂർണ്ണമായ ലിസ്റ്റ് നൽകുക.
            അടിയന്തര ലക്ഷണങ്ങളെക്കുറിച്ച് (നെഞ്ചുവേദന, ഗുരുതരമായ രക്തസ്രാവ, ബോധക്കേട്) എന്തെങ്കിലും സൂചിപ്പിച്ചാൽ,
            ഉടൻ തന്നെ 108-ൽ വിളിക്കാൻ പ്രധാനമായി ഉപദേശിക്കുക.
            സംഭാഷണരീതിയിൽ, സൗഹൃദപരവും ആശ്വാസകരവുമായ സ്വരത്തിൽ പ്രതികരിക്കുക.
            """,
            'pa': """ਤੁਸੀਂ ਪੇਂਡੂ ਅਤੇ ਅਰਧ-ਸ਼ਹਿਰੀ ਆਬਾਦੀ ਲਈ ਇੱਕ ਸਿਹਤ ਸਿੱਖਿਆ ਸਹਾਇਕ ਹੋ।
            ਸਹੀ, ਸਰਲ ਅਤੇ ਸੱਭਿਆਚਾਰਕ ਤੌਰ 'ਤੇ ਢੁਕਵੀਂ ਸਿਹਤ ਜਾਣਕਾਰੀ ਪ੍ਰਦਾਨ ਕਰੋ।
            ਗੰਭੀਰ ਹਾਲਤਾਂ ਲਈ ਹਮੇਸ਼ਾ ਸਿਹਤ ਸੰਭਾਲ ਪੇਸ਼ੇਵਰਾਂ ਨਾਲ ਸਲਾਹ ਕਰਨ 'ਤੇ ਜ਼ੋਰ ਦਿਓ।
            ਜਵਾਬਾਂ ਨੂੰ ਸੰਖੇਪ ਅਤੇ ਸਮਝਣ ਵਿੱਚ ਆਸਾਨ ਰੱਖੋ।
            ਜਦੋਂ ਢੁਕਵਾਂ ਹੋਵੇ ਤਾਂ ਐਮਰਜੈਂਸੀ ਸੰਪਰਕ (108) ਸ਼ਾਮਲ ਕਰੋ।
            ਜੇ ਉਪਭੋਗਤਾ ਟੀਕਾਕਰਨ ਬਾਰੇ ਪੁੱਛਦਾ ਹੈ, ਤਾਂ ਡੇਟਾਬੇਸ ਤੋਂ ਪੂਰੀ ਸੂਚੀ ਪ੍ਰਦਾਨ ਕਰੋ।
            ਕਿਸੇ ਵੀ ਐਮਰਜੈਂਸੀ ਲੱਛਣਾਂ (ਛਾਤੀ ਵਿੱਚ ਦਰਦ, ਗੰਭੀਰ ਖੂਨ ਵਗਣਾ, ਬੇਹੋਸ਼ੀ) ਦਾ ਜ਼ਿਕਰ ਹੋਣ 'ਤੇ,
            ਤੁਰੰਤ ਅਤੇ ਪ੍ਰਮੁੱਖ ਤੌਰ 'ਤੇ 108 'ਤੇ ਕਾਲ ਕਰਨ ਦੀ ਸਲਾਹ ਦਿਓ।
            ਗੱਲਬਾਤ ਵਾਲੇ, ਦੋਸਤਾਨਾ ਅਤੇ ਭਰੋਸਾ ਦੇਣ ਵਾਲੇ ਲਹਿਜੇ ਵਿੱਚ ਜਵਾਬ ਦਿਓ।
            """,
            'or': """ଆପଣ ଗ୍ରାମୀଣ ଏବଂ ଅର୍ଦ୍ଧ-ଶାହାରୀ ଜନସଂଖ୍ୟା ପାଇଁ ଏକ ସ୍ୱାସ୍ଥ୍ୟ ଶିକ୍ଷା ସହାୟକ।
            ସଠିକ୍, ସରଳ, ଏବଂ ସାଂସ୍କୃତିକ ଭାବରେ ଉପଯୁକ୍ତ ସ୍ୱାସ୍ଥ୍ୟ ସୂଚନା ପ୍ରଦାନ କରନ୍ତୁ।
            ଗମ୍ଭୀର ଅବସ୍ଥା ପାଇଁ ସର୍ବଦା ସ୍ୱାସ୍ଥ୍ୟ ସେବା ବୃତ୍ତିଗତଙ୍କ ସହିତ ପରାମର୍ଶ କରିବାକୁ ଗୁରୁତ୍ୱ ଦିଅନ୍ତୁ।
            ପ୍ରତିକ୍ରିୟାକୁ ସଂକ୍ଷିପ୍ତ ଏବଂ ବୁଝିବା ସହଜ ରଖନ୍ତୁ।
            ଯେତେବେଳେ ଉପଯୁକ୍ତ ହୁଏ, ଜରୁରୀକାଳୀନ ଯୋଗାଯୋଗ (108) ଅନ୍ତର୍ଭୁକ୍ତ କରନ୍ତୁ।
            ଯଦି ଉପଭୋକ୍ତା ଟୀକାକରଣ ବିଷୟରେ ପଚାରନ୍ତି, ତେବେ ଡାଟାବେସରୁ ସମ୍ପୂର୍ଣ୍ଣ ତାଲିକା ପ୍ରଦାନ କରନ୍ତୁ।
            ଯଦି କୌଣସି ଜରୁରୀକାଳୀନ ଲକ୍ଷଣ (ଛାତି ଯନ୍ତ୍ରଣା, ଗମ୍ଭୀର ରକ୍ତସ୍ରାବ, ବେହୋଶ) ର ଉଲ୍ଲେଖ ଥାଏ,
            ତୁରନ୍ତ ଏବଂ ପ୍ରମୁଖ ଭାବରେ 108 କୁ କଲ୍ କରିବାକୁ ପରାମର୍ଶ ଦିଅନ୍ତୁ।
            କଥାବାର୍ତ୍ତା ଶୈଳୀରେ, ବନ୍ଧୁତ୍ୱପୂର୍ଣ୍ଣ ଏବଂ ଆଶ୍ୱାସକର ସ୍ୱରରେ ପ୍ରତିକ୍ରିୟା କରନ୍ତୁ।
            """,
            'as': """আপুনি গ্ৰাম্য আৰু অৰ্ধ-চহৰীয়া জনসংখ্যাৰ বাবে এজন স্বাস্থ্য শিক্ষা সহায়ক।
            সঠিক, সহজ, আৰু সাংস্কৃতিকভাৱে উপযুক্ত স্বাস্থ্য তথ্য প্ৰদান কৰক।
            গুৰুতৰ অৱস্থাৰ বাবে সদায় স্বাস্থ্যসেৱা পেছাদাৰীৰ সৈতে পৰামৰ্শ কৰিবলৈ গুৰুত্ব দিয়ক।
            প্ৰতিক্ৰিয়া সংক্ষিপ্ত আৰু সহজে বুজিব পৰা ধৰণে ৰাখক।
            উপযুক্ত হ'লে জৰুৰীকালীন যোগাযোগ (108) অন্তৰ্ভুক্ত কৰক।
            যদি ব্যৱহাৰকাৰীয়ে টিকাকৰণৰ বিষয়ে সুধে, তেন্তে ডাটাবেছৰ পৰা সম্পূৰ্ণ তালিকা প্ৰদান কৰক।
            যিকোনো জৰুৰীকালীন লক্ষণৰ (বুকুৰ বিষ, গুৰুতৰ ৰক্তক্ষৰণ, অজ্ঞান হোৱা) উল্লেখ হ'লে,
            তৎক্ষণাৎ আৰু প্ৰধানকৈ 108 নম্বৰত ফোন কৰিবলৈ পৰামৰ্শ দিয়ক।
            কথোপকথনৰ, বন্ধুত্বপূৰ্ণ আৰু আশ্বাসদায়ক সুৰত সঁহাৰি দিয়ক।
            """
        }
    
    def generate_response(self, user_message: str, language: str = 'en') -> str:
        """Generates an AI response based on user message and database knowledge."""
        try:
            db_results = self.search_health_database(user_message, language)
            
            prompt = f"""{self.system_prompt.get(language, self.system_prompt['en'])}

Relevant health information from database:
{db_results}

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

Keep each bullet point concise but informative."""
            
            response = model.generate_content(prompt)
            
            if response.text:
                return self.format_response(response.text, language)
            else:
                return self.get_fallback_response(language)
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self.get_fallback_response(language)
    
    def search_health_database(self, query: str, language: str) -> str:
        """Searches the local database for relevant information."""
        results = []
        
        # Check for vaccination keywords first
        vaccine_keywords = {
            'en': ['vaccine', 'vaccination', 'immunization', 'polio', 'mmr', 'dpt', 'bcg'],
            'hi': ['टीका', 'टीकाकरण', 'पोलियो', 'एमएमआर', 'डीपीटी', 'बीसीजी'],
            'bn': ['টিকা', 'টিকাদান', 'পোলিও', 'এমএমআর', 'ডিপিটি', 'বিসিজি'],
            'ta': ['தடுப்பூசி', 'தடுப்பூசிகள்', 'போலியோ', 'எம்எம்ஆர்', 'டிபிடி', 'பிசிஜி'],
            'te': ['టీకా', 'టీకాలు', 'పోలియో', 'ఎంఎంఆర్', 'డిపిటి', 'బిసిజి'],
            'mr': ['लस', 'लसीकरण', 'पोलिओ', 'एमएमआर', 'डीपीटी', 'बीसीजी'],
            'gu': ['રસી', 'રસીકરણ', 'પોલિયો', 'એમએમઆર', 'ડીપીટી', 'બીસીજી'],
            'kn': ['ಲಸಿಕೆ', 'ಲಸಿಕೆಗಳು', 'ಪೋಲಿಯೋ', 'ಎಂಎಂಆರ್', 'ಡಿಪಿಟಿ', 'ಬಿಸಿಜಿ'],
            'ml': ['വാക്സിൻ', 'വാക്സിനേഷൻ', 'പോളിയോ', 'എംഎംആർ', 'ഡിപിടി', 'ബിസിജി'],
            'pa': ['ਟੀਕਾ', 'ਟੀਕਾਕਰਨ', 'ਪੋਲੀਓ', 'ਐਮਐਮਆਰ', 'ਡੀਪੀਟੀ', 'ਬੀਸੀਜੀ'],
            'or': ['ଟୀକା', 'ଟୀକାକରଣ', 'ପୋଲିଓ', 'ଏମଏମଆର', 'ଡିପିଟି', 'ବିସିଜି'],
            'as': ['টিকাদান', 'টিকাকৰণ', 'পোলিও', 'এমএমআৰ', 'ডিপিটি', 'বিচিজি'],
        }
        
        if any(keyword in query.lower() for keyword in vaccine_keywords.get(language, [])):
            vaccines = self.health_db.get_vaccination_schedule(language=language)
            if vaccines:
                results.append("Vaccination Schedule:")
                for vaccine in vaccines:
                    results.append(f"- {vaccine['vaccine_name']} ({vaccine['age_group']}): {vaccine['schedule']}. {vaccine['description']}.")
            else:
                results.append("No vaccination data found for the selected language.")
        
        # Then, check for disease-related keywords
        diseases = self.health_db.search_diseases(query, language)
        if diseases:
            results.append("\nDisease Information:")
            for disease in diseases[:2]:
                results.append(f"- {disease['name']}: Symptoms - {disease['symptoms']}. Prevention - {disease['prevention']}.")
        
        return "\n".join(results) if results else ""

    def format_response(self, response: str, language: str) -> str:
        """Formats the response and adds emergency contact if necessary."""
        # Replace Markdown bold with plain text for easier front-end handling
        response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)
        response = re.sub(r'\*([^*]+)\*', r'\1', response)
        
        # Check for emergency keywords and add a prominent warning
        serious_keywords = {
            'en': ['chest pain', 'difficulty breathing', 'severe', 'emergency', 'blood', 'unconscious', 'fainting'],
            'hi': ['सीने में दर्द', 'सांस लेने में कठिनाई', 'गंभीर', 'आपातकाल', 'खून', 'बेहोश'],
            'bn': ['বুকে ব্যথা', 'শ্বাসকষ্ট', 'গুরুতর', 'জরুরি', 'রক্ত', 'অজ্ঞান'],
            'ta': ['மார்பு வலி', 'மூச்சு திணறல்', 'கடுமையான', 'அவசரம்', 'இரத்தம்', 'மயக்கம்'],
            'te': ['ఛాతీ నొప్పి', 'శ్వాస తీసుకోవడంలో ఇబ్బంది', 'తీవ్రమైన', 'అత్యవసర', 'రక్తం', 'అపస్మారక'],
            'mr': ['छातीत दुखणे', 'श्वास घेण्यास त्रास', 'गंभीर', 'आपत्कालीन', 'रक्त', 'बेशुद्ध'],
            'gu': ['છાતીમાં દુખાવો', 'શ્વાસ લેવામાં તકલીફ', 'ગંભીર', 'કટોકટી', 'લોહી', 'બેભાન'],
            'kn': ['ಎದೆನೋವು', 'ಉಸಿರಾಟದ ತೊಂದರೆ', 'ತೀವ್ರ', 'ತುರ್ತು', 'ರಕ್ತ', 'ಪ್ರಜ್ಞಾಹೀನ'],
            'ml': ['നെഞ്ചുവേദന', 'ശ്വാസംമുട്ടൽ', 'ഗുരുതരമായ', 'അടിയന്തര', 'രക്തം', 'ബോധം നഷ്ടപ്പെട്ടു'],
            'pa': ['ਛਾਤੀ ਵਿੱਚ ਦਰਦ', 'ਸਾਹ ਲੈਣ ਵਿੱਚ ਮੁਸ਼ਕਲ', 'ਗੰਭੀਰ', 'ਐਮਰਜੈਂਸੀ', 'ਖੂਨ', 'ਬੇਹੋਸ਼'],
            'or': ['ଛାତି ଯନ୍ତ୍ରଣା', 'ଶ୍ବାସକଷ୍ଟ', 'ଗୁରୁତର', 'ଜରୁରୀ', 'ରକ୍ତ', 'ବେହୋଶ'],
            'as': ['বুকুৰ বিষ', 'শ্বাস লোৱাত কষ্ট', 'গুৰুতৰ', 'জৰুৰী', 'তেজ', 'অজ্ঞান'],
        }
        
        if any(keyword in response.lower() for keyword in serious_keywords.get(language, [])):
            emergency_note = {
                'en': "\n⚠️ For medical emergencies, call 108 immediately.",
                'hi': "\n⚠️ आपातकालीन स्थिति में तुरंत 108 पर कॉल करें।",
                'bn': "\n⚠️ চিকিৎসা জরুরী অবস্থার জন্য, অবিলম্বে 108 নম্বরে কল করুন।",
                'ta': "\n⚠️ மருத்துவ அவசரநிலைக்கு, உடனடியாக 108 ஐ அழைக்கவும்.",
                'te': "\n⚠️ వైద్య అత్యవసర పరిస్థితుల్లో, వెంటనే 108కు కాల్ చేయండి.",
                'mr': "\n⚠️ वैद्यकीय आपत्कालीन परिस्थितीत, त्वरित 108 वर कॉल करा.",
                'gu': "\n⚠️ તબીબી કટોકટી માટે, તુરંત 108 પર કૉલ કરો.",
                'kn': "\n⚠️ ವೈದ್ಯಕೀಯ ತುರ್ತುಸ್ಥಿತಿಗೆ, ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ.",
                'ml': "\n⚠️ മെഡിക്കൽ എമർജൻസിക്ക്, ഉടൻ തന്നെ 108-ൽ വിളിക്കുക.",
                'pa': "\n⚠️ ਡਾਕਟਰੀ ਐਮਰਜੈਂਸੀ ਲਈ, ਤੁਰੰਤ 108 'ਤੇ ਕਾਲ ਕਰੋ।",
                'or': "\n⚠️ ଚିକିତ୍ସା ଜରୁରୀ ଅବସ୍ଥା ପାଇଁ, ତୁରନ୍ତ 108 କୁ କଲ୍ କରନ୍ତୁ।",
                'as': "\n⚠️ চিকিৎসা জৰুৰীকালীন অৱস্থাৰ বাবে, তৎক্ষণাৎ 108 নম্বৰত ফোন কৰক।",
            }
            if emergency_note[language] not in response:
                response += emergency_note[language]
        
        return response
    
    def get_fallback_response(self, language: str) -> str:
        """Provides a simple fallback message if AI generation fails."""
        fallback = {
            'en': "I'm sorry, I couldn't process your request right now. Please try rephrasing your question or contact a healthcare professional for urgent matters. For emergencies, call 108.",
            'hi': "मुझे खेद है, मैं अभी आपके अनुरोध को संसाधित नहीं कर सका। कृपया अपने प्रश्न को दोबारा पूछें या तत्काल मामलों के लिए एक स्वास्थ्य पेशेवर से संपर्क करें। आपातकाल के लिए 108 पर कॉल करें।",
            'bn': "আমি দুঃখিত, আমি আপনার অনুরোধটি এই মুহূর্তে প্রক্রিয়া করতে পারিনি। অনুগ্রহ করে আপনার প্রশ্নটি পুনরায় লিখুন বা জরুরি প্রয়োজনে একজন স্বাস্থ্যসেবা পেশাদারের সাথে যোগাযোগ করুন। জরুরি অবস্থার জন্য, 108 নম্বরে কল করুন।",
            'ta': "மன்னிக்கவும், உங்கள் கோரிக்கையை என்னால் இப்போதைக்குச் செயல்படுத்த முடியவில்லை. தயவுசெய்து உங்கள் கேள்வியை மீண்டும் கேளுங்கள் அல்லது அவசர விஷயங்களுக்கு சுகாதார நிபுணரைத் தொடர்பு கொள்ளுங்கள். அவசரநிலைக்கு, 108 ஐ அழைக்கவும்.",
            'te': "క్షమించండి, నేను మీ అభ్యర్థనను ప్రస్తుతం ప్రాసెస్ చేయలేకపోయాను. దయచేసి మీ ప్రశ్నను మళ్లీ అడగండి లేదా అత్యవసర విషయాల కోసం ఆరోగ్య సంరక్షణ నిపుణుడిని సంప్రదించండి. అత్యవసర పరిస్థితులకు, 108కి కాల్ చేయండి.",
            'mr': "माफ करा, मी तुमचा सध्याचा विनंतीवर प्रक्रिया करू शकलो नाही. कृपया तुमचा प्रश्न पुन्हा विचारा किंवा तातडीच्या बाबींसाठी आरोग्यसेवा व्यावसायिकांशी संपर्क साधा. आपत्कालीन परिस्थितीत, 108 वर कॉल करा.",
            'gu': "માફ કરશો, હું તમારી વિનંતી પર હાલમાં પ્રક્રિયા કરી શક્યો નથી. કૃપા કરીને તમારા પ્રશ્નને ફરીથી પૂછો અથવા તાત્કાલિક બાબતો માટે આરોગ્ય સંભાળ વ્યાવસાયિકનો સંપર્ક કરો. કટોકટી માટે, 108 પર કૉલ કરો.",
            'kn': "ಕ್ಷಮಿಸಿ, ನಾನು ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ಇದೀಗ ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಪುನಃ ರೂಪಿಸಿ ಅಥವಾ ತುರ್ತು ವಿಷಯಗಳಿಗಾಗಿ ಆರೋಗ್ಯ ವೃತ್ತಿಪರರನ್ನು ಸಂಪರ್ಕಿಸಿ. ತುರ್ತುಸ್ಥಿತಿಗಳಿಗಾಗಿ, 108 ಗೆ ಕರೆ ಮಾಡಿ.",
            'ml': "ക്ഷമിക്കണം, എനിക്ക് നിങ്ങളുടെ അഭ്യർത്ഥന ഇപ്പോൾ പ്രോസസ്സ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ദയവായി നിങ്ങളുടെ ചോദ്യം വീണ്ടും ചോദിക്കുക അല്ലെങ്കിൽ അടിയന്തിര കാര്യങ്ങൾക്കായി ഒരു ആരോഗ്യ വിദഗ്ദ്ധനെ സമീപിക്കുക. അടിയന്തിര സാഹചര്യങ്ങളിൽ, 108-ൽ വിളിക്കുക.",
            'pa': "ਮੈਨੂੰ ਮਾਫ ਕਰਨਾ, ਮੈਂ ਤੁਹਾਡੀ ਬੇਨਤੀ ਨੂੰ ਇਸ ਸਮੇਂ ਪ੍ਰਕਿਰਿਆ ਨਹੀਂ ਕਰ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਸਵਾਲ ਨੂੰ ਦੁਬਾਰਾ ਪੁੱਛੋ ਜਾਂ ਜ਼ਰੂਰੀ ਮਾਮਲਿਆਂ ਲਈ ਸਿਹਤ ਸੰਭਾਲ ਪੇਸ਼ੇਵਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ। ਐਮਰਜੈਂਸੀ ਲਈ, 108 'ਤੇ ਕਾਲ ਕਰੋ।",
            'or': "ମୁଁ ଦୁଃଖିତ, ମୁଁ ବର୍ତ୍ତମାନ ଆପଣଙ୍କ ଅନୁରୋଧକୁ ପ୍ରକ୍ରିୟା କରିପାରିଲି ନାହିଁ। ଦୟାକରି ଆପଣଙ୍କ ପ୍ରଶ୍ନକୁ ପୁନର୍ବାର ପଚାରନ୍ତୁ କିମ୍ବା ଜରୁରୀ ବିଷୟ ପାଇଁ ଜଣେ ସ୍ୱାସ୍ଥ୍ୟ ସେବା ବୃତ୍ତିଗତଙ୍କ ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ। ଜରୁରୀକାଳୀନ ପରିସ୍ଥିତିରେ, 108 କୁ କଲ୍ କରନ୍ତୁ।",
            'as': "মই দুঃখিত, মই আপোনাৰ অনুৰোধটো এই মুহূৰ্তত প্ৰক্ৰিয়া কৰিব নোৱাৰিলোঁ। অনুগ্ৰহ কৰি আপোনাৰ প্ৰশ্নটো পুনৰ সুধিব অথবা জৰুৰী বিষয়ৰ বাবে এজন স্বাস্থ্যসেৱা পেছাদাৰীৰ সৈতে যোগাযোগ কৰক। জৰুৰীকালীন অৱস্থাৰ বাবে, 108 নম্বৰত ফোন কৰক।",
        }
        return fallback.get(language, fallback['en'])

# Initialize database and AI assistant
health_db = HealthDatabase()
ai_assistant = AIHealthAssistant(health_db)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint to handle chat requests."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        logger.info(f"Received message from user {user_id}: '{user_message}' in language '{language}'")
        
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
    """Endpoint to get disease information."""
    query = request.args.get('q', '')
    language = request.args.get('lang', 'en')
    
    results = health_db.search_diseases(query, language)
    return jsonify({'diseases': results, 'total': len(results)})

@app.route('/api/vaccinations', methods=['GET'])
def get_vaccinations():
    """Endpoint to get vaccination schedule."""
    age_group = request.args.get('age_group')
    language = request.args.get('lang', 'en')
    
    results = health_db.get_vaccination_schedule(age_group, language)
    return jsonify({'vaccinations': results, 'total': len(results)})

@app.route('/api/emergency', methods=['GET'])
def emergency_info():
    """Endpoint to get emergency contact information."""
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
        },
        'bn': {'message': 'চিকিৎসা জরুরী অবস্থার জন্য, অবিলম্বে 108 নম্বরে কল করুন।'},
        'ta': {'message': 'மருத்துவ அவசரநிலைக்கு, உடனடியாக 108 ஐ அழைக்கவும்.'},
        'te': {'message': 'వైద్య అత్యవసర పరిస్థితుల్లో, వెంటనే 108కు కాల్ చేయండి.'},
        'mr': {'message': 'वैद्यकीय आपत्कालीन परिस्थितीत, त्वरित 108 वर कॉल करा.'},
        'gu': {'message': 'તબીબી કટોકટી માટે, તુરંત 108 પર કૉલ કરો.'},
        'kn': {'message': 'ವೈದ್ಯಕೀಯ ತುರ್ತುಸ್ಥಿತಿಗೆ, ತಕ್ಷಣ 108 ಗೆ ಕರೆ ಮಾಡಿ.'},
        'ml': {'message': 'മെഡിക്കൽ എമർജൻസിക്ക്, ഉടൻ തന്നെ 108-ൽ വിളിക്കുക.'},
        'pa': {'message': 'ਡਾਕਟਰੀ ਐਮਰਜੈਂਸੀ ਲਈ, ਤੁਰੰਤ 108 ਤੇ ਕਾਲ ਕਰੋ।'},
        'or': {'message': 'ଚିକିତ୍ସା ଜରୁରୀ ଅବସ୍ଥା ପାଇଁ, ତୁରନ୍ତ 108 କୁ କଲ୍ କରନ୍ତୁ।'},
        'as': {'message': 'চিকিৎসা জৰুৰীকালীন অৱস্থাৰ বাবে, তৎক্ষণাৎ 108 নম্বৰত ফোন কৰক।'},
    }
    return jsonify(emergency_info.get(language, emergency_info['en']))

@app.route('/')
def index():
    """Main route to confirm the backend is running."""
    return "Healthcare Chatbot Backend is running! Use /api/chat endpoint for interactions."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)