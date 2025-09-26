import google.generativeai as genai
import os
from typing import List, Optional
from ..models.chat import Message, MessageRole
import logging

logger = logging.getLogger(__name__)

class GeminiHealthBot:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Health-focused system prompt
        self.system_prompt = """
You are a helpful AI health assistant designed specifically for rural communities with limited access to healthcare. Your role is to:

1. Provide general health information and guidance
2. Help users understand common symptoms and when to seek medical care
3. Offer wellness and prevention advice
4. Be culturally sensitive to rural healthcare challenges
5. Always emphasize the importance of professional medical care

IMPORTANT GUIDELINES:
- Always include medical disclaimers
- Never provide specific medical diagnoses
- Encourage seeking professional medical care for serious concerns
- Be empathetic and understanding of rural healthcare access challenges
- Provide practical, actionable advice when appropriate
- If asked about emergency situations, immediately direct to emergency services

RESPONSE FORMAT:
- Be clear, concise, and easy to understand
- Use simple language appropriate for all education levels
- Include relevant disclaimers about seeking professional medical advice
- Offer practical next steps when appropriate

Remember: You are providing general health information only, not medical advice.
"""

    async def get_health_response(self, query: str, context: List[Message] = None) -> str:
        """
        Generate health-focused response using Gemini API
        """
        try:
            # Prepare conversation context
            conversation_context = self._prepare_context(query, context)
            
            # Generate response
            response = self.model.generate_content(conversation_context)
            
            if response.text:
                # Add medical disclaimer if not already present
                formatted_response = self._format_health_response(response.text)
                return formatted_response
            else:
                return self._get_fallback_response()
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return self._get_error_response()

    def _prepare_context(self, query: str, context: List[Message] = None) -> str:
        """
        Prepare conversation context for Gemini API
        """
        # Start with system prompt
        conversation = self.system_prompt + "\n\n"
        
        # Add conversation history if available
        if context:
            conversation += "CONVERSATION HISTORY:\n"
            for message in context[-5:]:  # Last 5 messages for context
                role = "User" if message.role == MessageRole.USER else "Assistant"
                conversation += f"{role}: {message.content}\n"
            conversation += "\n"
        
        # Add current query
        conversation += f"User: {query}\n\nAssistant:"
        
        return conversation

    def _format_health_response(self, response: str) -> str:
        """
        Format response with appropriate medical disclaimers
        """
        # Check if response already contains disclaimer
        disclaimer_keywords = ['medical advice', 'healthcare professional', 'doctor', 'disclaimer']
        has_disclaimer = any(keyword in response.lower() for keyword in disclaimer_keywords)
        
        if not has_disclaimer:
            disclaimer = "\n\n⚠️ **Important:** This information is for general guidance only and should not replace professional medical advice. Please consult with a healthcare provider for proper diagnosis and treatment."
            response += disclaimer
        
        # Check for emergency situations
        emergency_keywords = ['emergency', 'urgent', 'severe', 'call 911', 'immediate']
        if any(keyword in response.lower() for keyword in emergency_keywords):
            emergency_notice = "\n\n🚨 **Emergency:** If this is a medical emergency, please call 911 or go to your nearest emergency room immediately."
            response = emergency_notice + "\n\n" + response
        
        return response

    def _get_fallback_response(self) -> str:
        """
        Fallback response when Gemini API doesn't return content
        """
        return (
            "I understand you're asking about a health-related concern. While I'd like to help, "
            "I'm having trouble generating a response right now. For any health questions or concerns, "
            "I recommend consulting with a healthcare professional who can provide personalized advice.\n\n"
            "⚠️ **Important:** This is for general information only and should not replace professional medical advice."
        )

    def _get_error_response(self) -> str:
        """
        Error response when API call fails
        """
        return (
            "I apologize, but I'm experiencing technical difficulties right now. "
            "For health-related questions and concerns, please consider:\n\n"
            "• Contacting your local healthcare provider\n"
            "• Calling a nurse hotline if available in your area\n"
            "• Visiting a nearby clinic or urgent care center\n"
            "• For emergencies, call 911 immediately\n\n"
            "⚠️ **Important:** This service provides general health information only and should not replace professional medical care."
        )

    def format_health_disclaimer(self, response: str) -> str:
        """
        Ensure proper health disclaimers are included
        """
        return self._format_health_response(response)