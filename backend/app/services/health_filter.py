import re
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class FilterResult:
    is_health_related: bool
    confidence: float
    reason: str

class HealthContextFilter:
    def __init__(self):
        # Health-related keywords and phrases
        self.health_keywords = {
            'symptoms': ['pain', 'ache', 'fever', 'headache', 'nausea', 'vomiting', 'diarrhea', 
                        'constipation', 'fatigue', 'tired', 'dizzy', 'cough', 'cold', 'flu',
                        'sore throat', 'runny nose', 'congestion', 'shortness of breath',
                        'chest pain', 'back pain', 'stomach pain', 'muscle pain'],
            
            'body_parts': ['head', 'neck', 'chest', 'back', 'stomach', 'abdomen', 'arm', 'leg',
                          'hand', 'foot', 'eye', 'ear', 'nose', 'throat', 'heart', 'lung',
                          'kidney', 'liver', 'brain', 'skin', 'joint', 'muscle', 'bone'],
            
            'medical_terms': ['doctor', 'hospital', 'clinic', 'medicine', 'medication', 'treatment',
                             'diagnosis', 'symptom', 'disease', 'illness', 'infection', 'virus',
                             'bacteria', 'allergy', 'diabetes', 'hypertension', 'blood pressure',
                             'cholesterol', 'vaccine', 'vaccination', 'prescription', 'therapy'],
            
            'health_concerns': ['health', 'medical', 'wellness', 'nutrition', 'diet', 'exercise',
                               'mental health', 'depression', 'anxiety', 'stress', 'sleep',
                               'pregnancy', 'birth control', 'sexual health', 'weight loss',
                               'weight gain', 'healthy eating', 'vitamins', 'supplements'],
            
            'emergency': ['emergency', 'urgent', 'severe', 'intense', 'unbearable', 'bleeding',
                         'unconscious', 'difficulty breathing', 'chest pain', 'heart attack',
                         'stroke', 'poisoning', 'overdose', 'suicide', 'self harm']
        }
        
        # Non-health topics that should be rejected
        self.non_health_keywords = {
            'technology': ['computer', 'software', 'programming', 'coding', 'website', 'app',
                          'internet', 'wifi', 'phone', 'smartphone', 'laptop', 'tablet'],
            
            'entertainment': ['movie', 'music', 'game', 'sport', 'football', 'basketball',
                             'celebrity', 'tv show', 'netflix', 'youtube', 'social media'],
            
            'general': ['weather', 'politics', 'news', 'business', 'finance', 'investment',
                       'stock market', 'cryptocurrency', 'bitcoin', 'travel', 'vacation'],
            
            'education': ['school', 'university', 'homework', 'assignment', 'exam', 'grade',
                         'mathematics', 'history', 'geography', 'literature']
        }

    def is_health_related(self, query: str) -> FilterResult:
        """
        Determine if a query is health-related using keyword matching and pattern analysis
        """
        query_lower = query.lower()
        
        # Check for emergency keywords first
        emergency_score = self._calculate_keyword_score(query_lower, self.health_keywords['emergency'])
        if emergency_score > 0:
            return FilterResult(
                is_health_related=True,
                confidence=1.0,
                reason="Emergency health concern detected"
            )
        
        # Calculate health-related score
        health_score = 0
        for category, keywords in self.health_keywords.items():
            health_score += self._calculate_keyword_score(query_lower, keywords)
        
        # Calculate non-health score
        non_health_score = 0
        for category, keywords in self.non_health_keywords.items():
            non_health_score += self._calculate_keyword_score(query_lower, keywords)
        
        # Check for health-related patterns
        health_patterns = [
            r'\b(how to|what is|why do|when should).*(health|medical|doctor|medicine)',
            r'\b(i have|i feel|i am experiencing).*(pain|ache|symptom)',
            r'\b(is it normal|should i worry|is this serious)',
            r'\b(home remedy|natural treatment|cure for)',
            r'\b(side effect|medication|prescription|dosage)'
        ]
        
        pattern_score = 0
        for pattern in health_patterns:
            if re.search(pattern, query_lower):
                pattern_score += 1
        
        # Calculate final confidence
        total_health_score = health_score + (pattern_score * 2)
        confidence = min(total_health_score / max(total_health_score + non_health_score, 1), 1.0)
        
        # Decision logic
        if total_health_score > 0 and confidence > 0.3:
            return FilterResult(
                is_health_related=True,
                confidence=confidence,
                reason=f"Health keywords detected (score: {total_health_score})"
            )
        elif non_health_score > total_health_score and non_health_score > 2:
            return FilterResult(
                is_health_related=False,
                confidence=1.0 - confidence,
                reason="Non-health topic detected"
            )
        else:
            # Ambiguous case - err on the side of allowing health-related queries
            return FilterResult(
                is_health_related=total_health_score >= non_health_score,
                confidence=0.5,
                reason="Ambiguous query - defaulting based on keyword balance"
            )

    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> int:
        """Calculate score based on keyword matches"""
        score = 0
        for keyword in keywords:
            if keyword in text:
                # Give higher score for exact matches
                if f" {keyword} " in f" {text} ":
                    score += 2
                else:
                    score += 1
        return score

    def get_rejection_message(self, query: str) -> str:
        """Get appropriate rejection message for non-health queries"""
        query_lower = query.lower()
        
        # Check what type of non-health topic it might be
        for category, keywords in self.non_health_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return self._get_category_rejection_message(category)
        
        # Default rejection message
        return (
            "I'm specifically designed to help with health-related questions and concerns. "
            "I can assist you with information about symptoms, general health advice, wellness tips, "
            "and when to seek medical care. Please feel free to ask me any health-related questions!"
        )

    def _get_category_rejection_message(self, category: str) -> str:
        """Get category-specific rejection messages"""
        messages = {
            'technology': (
                "I'm focused on health-related assistance and can't help with technology questions. "
                "However, I'd be happy to discuss health topics like digital wellness, "
                "screen time effects on health, or ergonomics while using devices."
            ),
            'entertainment': (
                "I specialize in health-related guidance rather than entertainment topics. "
                "I can discuss health aspects of activities like the benefits of physical exercise, "
                "mental health and entertainment, or healthy lifestyle choices."
            ),
            'general': (
                "I'm designed to focus on health and wellness topics. "
                "Please feel free to ask me about any health concerns, symptoms, "
                "wellness advice, or general health information."
            ),
            'education': (
                "While I can't help with general educational topics, I'm here for health-related questions. "
                "I can discuss health education topics, wellness in academic settings, "
                "or stress management for students."
            )
        }
        
        return messages.get(category, self.get_rejection_message(""))

    def sanitize_health_query(self, query: str) -> str:
        """Clean and prepare health query for processing"""
        # Remove excessive whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Remove potentially harmful content
        harmful_patterns = [
            r'\b(kill|die|suicide|self.harm)\b',
            r'\b(illegal|drug.abuse|overdose)\b'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, query.lower()):
                # Flag for special handling rather than removing
                query = f"[SENSITIVE_CONTENT] {query}"
        
        return query