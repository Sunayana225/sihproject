import google.generativeai as genai
import re
import logging
import os
from typing import Dict, List
from app.services.health_database import health_db
from app.models.health import DiseaseInfo, VaccinationInfo

logger = logging.getLogger(__name__)

class AIHealthAssistant:
    """Handles AI-powered health assistant logic using Gemini."""
    
    def __init__(self):
        # Configure Gemini AI
        api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.system_prompt = {
            'en': """You are a healthcare education assistant for rural and semi-urban populations.
            Provide accurate, simple, and culturally appropriate health information.
            Always emphasize consulting healthcare professionals for serious conditions.
            Keep responses concise and easy to understand.
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
            কথোপকথনের, বন্ধুত্বপূর্ণ এবং আশ্বস্ত করার মতো স্वরে সাড়া দিন।
            """,
            # Add more languages as needed...
        }
    
    def generate_response(self, user_message: str, language: str = 'en') -> str:
        """Generates an AI response based on user message and database knowledge."""
        try:
            db_results = self.search_health_database(user_message, language)
            
            prompt = f"{self.system_prompt.get(language, self.system_prompt['en'])}\n\nRelevant health information from database:\n{db_results}\n\nUser question: {user_message}"
            
            response = self.model.generate_content(prompt)
            
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
            # Add more languages as needed...
        }
        
        if any(keyword in query.lower() for keyword in vaccine_keywords.get(language, [])):
            vaccines = health_db.get_vaccination_schedule(language=language)
            if vaccines:
                results.append("Vaccination Schedule:")
                for vaccine in vaccines:
                    results.append(f"- {vaccine.vaccine_name} ({vaccine.age_group}): {vaccine.schedule}. {vaccine.description}.")
            else:
                results.append("No vaccination data found for the selected language.")
        
        # Then, check for disease-related keywords
        diseases = health_db.search_diseases(query, language)
        if diseases:
            results.append("\nDisease Information:")
            for disease in diseases[:2]:  # Limit to first 2 results
                results.append(f"- {disease.name}: Symptoms - {disease.symptoms}. Prevention - {disease.prevention}.")
        
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
            # Add more languages as needed...
        }
        
        if any(keyword in response.lower() for keyword in serious_keywords.get(language, [])):
            emergency_note = {
                'en': "\n⚠️ For medical emergencies, call 108 immediately.",
                'hi': "\n⚠️ आपातकालीन स्थिति में तुरंत 108 पर कॉल करें।",
                'bn': "\n⚠️ চিকিৎসা জরুরী অবস্থার জন্য, অবিলম্বে 108 নম্বরে কল করুন।",
                # Add more languages as needed...
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
            # Add more languages as needed...
        }
        return fallback.get(language, fallback['en'])

# Global instance
ai_assistant = AIHealthAssistant()