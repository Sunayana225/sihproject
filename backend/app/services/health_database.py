import sqlite3
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from app.models.health import DiseaseInfo, VaccinationInfo, HealthChatHistory

logger = logging.getLogger(__name__)

class HealthDatabase:
    """Manages the health database and provides health-related data access."""
    
    def __init__(self, db_path: str = "health_data.db"):
        """Initializes the database connection and loads initial data."""
        self.db_path = db_path
        self.init_database()
        self.load_health_data()

    def get_connection(self):
        """Get a fresh database connection."""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        """Creates tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
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
                cursor.execute('''
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
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_message TEXT NOT NULL,
                        bot_response TEXT NOT NULL,
                        language TEXT DEFAULT 'en',
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT
                    )
                ''')
                conn.commit()
                logger.info("Health database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

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
            # Add more multilingual data as needed...
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
            # Add more vaccination data as needed...
        ]
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM diseases')
                if cursor.fetchone()[0] == 0:
                    cursor.executemany('INSERT INTO diseases (name, symptoms, prevention, treatment, severity, language) VALUES (?, ?, ?, ?, ?, ?)', diseases_data)
                    logger.info("Diseases data loaded.")
                
                cursor.execute('SELECT COUNT(*) FROM vaccinations')
                if cursor.fetchone()[0] == 0:
                    cursor.executemany('INSERT INTO vaccinations (vaccine_name, age_group, schedule, description, side_effects, language) VALUES (?, ?, ?, ?, ?, ?)', vaccination_data)
                    logger.info("Vaccination data loaded.")
                
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error loading health data: {e}")

    def search_diseases(self, query: str, language: str = 'en') -> List[DiseaseInfo]:
        """Searches for diseases based on keywords in name, symptoms, or prevention."""
        query = query.lower()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, symptoms, prevention, treatment, severity, language 
                    FROM diseases 
                    WHERE language = ? AND (LOWER(name) LIKE ? OR LOWER(symptoms) LIKE ? OR LOWER(prevention) LIKE ?)
                ''', (language, f'%{query}%', f'%{query}%', f'%{query}%'))
                
                results = []
                for row in cursor.fetchall():
                    results.append(DiseaseInfo(
                        name=row[0],
                        symptoms=row[1],
                        prevention=row[2],
                        treatment=row[3],
                        severity=row[4],
                        language=row[5]
                    ))
                return results
        except sqlite3.Error as e:
            logger.error(f"Error searching diseases: {e}")
            return []
    
    def get_vaccination_schedule(self, age_group: str = None, language: str = 'en') -> List[VaccinationInfo]:
        """Retrieves vaccination schedule based on age group or all."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if age_group:
                    cursor.execute('''
                        SELECT vaccine_name, age_group, schedule, description, side_effects, language
                        FROM vaccinations 
                        WHERE language = ? AND LOWER(age_group) LIKE ?
                    ''', (language, f'%{age_group.lower()}%'))
                else:
                    cursor.execute('''
                        SELECT vaccine_name, age_group, schedule, description, side_effects, language 
                        FROM vaccinations WHERE language = ?
                    ''', (language,))
                
                results = []
                for row in cursor.fetchall():
                    results.append(VaccinationInfo(
                        vaccine_name=row[0],
                        age_group=row[1],
                        schedule=row[2],
                        description=row[3],
                        side_effects=row[4],
                        language=row[5]
                    ))
                return results
        except sqlite3.Error as e:
            logger.error(f"Error retrieving vaccination schedule: {e}")
            return []

    def save_chat_history(self, user_message: str, bot_response: str, language: str, user_id: str = None):
        """Saves a chat interaction to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO chat_history (user_message, bot_response, language, user_id)
                    VALUES (?, ?, ?, ?)
                ''', (user_message, bot_response, language, user_id))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error saving chat history: {e}")

    def get_chat_history(self, user_id: str = None, language: str = None, limit: int = 50) -> List[HealthChatHistory]:
        """Retrieves chat history for a user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id, user_message, bot_response, language, timestamp, user_id FROM chat_history WHERE 1=1"
                params = []
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if language:
                    query += " AND language = ?"
                    params.append(language)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    results.append(HealthChatHistory(
                        id=row[0],
                        user_message=row[1],
                        bot_response=row[2],
                        language=row[3],
                        timestamp=datetime.fromisoformat(row[4]) if row[4] else None,
                        user_id=row[5]
                    ))
                return results
        except sqlite3.Error as e:
            logger.error(f"Error retrieving chat history: {e}")
            return []

# Global instance
health_db = HealthDatabase()