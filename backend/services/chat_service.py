"""
Chat service for AI-powered plant care assistant.
Uses Gemini API to provide conversational plant care advice.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from flask import current_app

from services.translation_service import translate_ai_prompt, get_text


# Chat system prompt for plant care assistant
CHAT_SYSTEM_PROMPT = """You are a friendly and knowledgeable plant care assistant. Your role is to:

1. **Answer Plant Care Questions**: Provide expert advice on watering, fertilizing, sunlight, soil, pruning, and general plant care.

2. **Diagnose Plant Problems**: Help identify potential diseases, pests, or care issues based on user descriptions.

3. **Interpret Analysis Results**: If the user has recently analyzed a plant, help them understand the results and recommended actions.

4. **Provide Personalized Advice**: Consider the user's specific plants, location (indoor/outdoor), and experience level.

5. **Be Conversational**: Engage naturally, ask clarifying questions when needed, and provide actionable advice.

Guidelines:
- Be concise but thorough
- Use simple language, avoid excessive jargon
- Provide step-by-step instructions when appropriate
- Suggest when professional help might be needed (severe infestations, rare diseases)
- Be encouraging and supportive to new plant parents

If you don't know something, be honest about it and suggest reliable resources.
"""


class ChatService:
    """Service for AI-powered chat functionality."""
    
    def __init__(self):
        self._client = None
        self._db = None
        self._ChatMessage = None
    
    @property
    def client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            try:
                from google import genai
                api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                if api_key:
                    self._client = genai.Client(api_key=api_key)
                else:
                    current_app.logger.warning("No Gemini API key configured. Set GEMINI_API_KEY environment variable.")
            except ImportError:
                current_app.logger.warning("Google GenAI not available for chat")
        return self._client
    
    def set_db(self, db):
        """Set database instance."""
        self._db = db
    
    @property
    def ChatMessage(self):
        """Lazy load ChatMessage model."""
        if self._ChatMessage is None:
            from models.database_models import ChatMessage
            self._ChatMessage = ChatMessage
        return self._ChatMessage
    
    def get_chat_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """
        Get chat history for a user.
        
        Args:
            user_id: User ID (None for guests - returns empty)
            limit: Maximum messages to return
        
        Returns:
            List of message dictionaries
        """
        # Return empty for guests
        if not user_id:
            return []
            
        try:
            messages = self.ChatMessage.query.filter_by(user_id=user_id)\
                .order_by(self.ChatMessage.created_at.desc())\
                .limit(limit).all()
            
            # Reverse to get chronological order
            return [msg.to_dict() for msg in reversed(messages)]
        except Exception as e:
            current_app.logger.error(f"Error getting chat history: {e}")
            return []
    
    def save_message(self, user_id: int, role: str, content: str, 
                     analysis_id: int = None) -> Optional[Dict]:
        """
        Save a chat message to database.
        
        Args:
            user_id: User ID (None for guests - messages not saved)
            role: Message role ('user' or 'assistant')
            content: Message content
            analysis_id: Optional related analysis ID
        
        Returns:
            Saved message dictionary
        """
        # Skip saving for guests (no user_id)
        if not user_id:
            return None
            
        try:
            message = self.ChatMessage(
                user_id=user_id,
                role=role,
                content=content,
                analysis_id=analysis_id
            )
            self._db.session.add(message)
            self._db.session.commit()
            return message.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error saving chat message: {e}")
            self._db.session.rollback()
            return None
    
    def clear_history(self, user_id: int) -> bool:
        """
        Clear chat history for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Success status
        """
        try:
            self.ChatMessage.query.filter_by(user_id=user_id).delete()
            self._db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error clearing chat history: {e}")
            self._db.session.rollback()
            return False
    
    def _build_context(self, user_id: int, user_message: str, 
                      analysis_context: Dict = None, 
                      plants_context: List[Dict] = None) -> str:
        """Build context prompt with user's plants and recent analysis."""
        context_parts = []
        
        # Add plant context if available
        if plants_context:
            plants_info = "User's plants:\n"
            for plant in plants_context[:5]:  # Limit to 5 plants
                plants_info += f"- {plant.get('name', 'Unknown')}"
                if plant.get('species'):
                    plants_info += f" ({plant['species']})"
                if plant.get('location'):
                    plants_info += f", {plant['location']}"
                plants_info += "\n"
            context_parts.append(plants_info)
        
        # Add recent analysis context if available
        if analysis_context:
            analysis_info = "Recent plant analysis:\n"
            analysis_info += f"- Plant type: {analysis_context.get('plant_type', 'Unknown')}\n"
            analysis_info += f"- Disease: {analysis_context.get('disease_detected', 'None detected')}\n"
            analysis_info += f"- Severity: {analysis_context.get('severity_level', 'N/A')}\n"
            analysis_info += f"- Health score: {analysis_context.get('health_score', 'N/A')}%\n"
            context_parts.append(analysis_info)
        
        if context_parts:
            return "\n".join(["Context:"] + context_parts + ["\nUser question: " + user_message])
        
        return user_message
    
    def _build_messages(self, user_id: int, current_message: str,
                       language: str = 'en',
                       analysis_context: Dict = None,
                       plants_context: List[Dict] = None) -> List[Dict]:
        """Build conversation messages for API."""
        messages = []
        
        # System prompt with language instruction
        system_prompt = CHAT_SYSTEM_PROMPT
        
        # Add strong language instruction for Hindi/Marathi
        if language == 'hi':
            system_prompt = """**महत्वपूर्ण: आपको हिंदी में जवाब देना होगा।**
You MUST respond entirely in Hindi (हिंदी) using Devanagari script.

""" + system_prompt + """

Remember: ALL your responses must be in Hindi language."""
        elif language == 'mr':
            system_prompt = """**महत्त्वाचे: तुम्हाला मराठीत उत्तर द्यायचे आहे।**
You MUST respond entirely in Marathi (मराठी) using Devanagari script.

""" + system_prompt + """

Remember: ALL your responses must be in Marathi language."""
        
        # Get recent history (last 10 messages for context)
        history = self.get_chat_history(user_id, limit=10)
        
        # Add history
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add current message with context
        enriched_message = self._build_context(
            user_id, current_message, analysis_context, plants_context
        )
        
        if language != 'en':
            enriched_message = translate_ai_prompt(enriched_message, language)
        
        messages.append({
            'role': 'user',
            'content': enriched_message
        })
        
        return system_prompt, messages
    
    def chat(self, user_id: int, message: str, language: str = 'en',
             analysis_context: Dict = None, 
             plants_context: List[Dict] = None) -> Dict:
        """
        Process a chat message and get AI response.
        
        Args:
            user_id: User ID
            message: User's message
            language: Response language
            analysis_context: Optional recent analysis data
            plants_context: Optional user's plants data
        
        Returns:
            Response dictionary with 'success', 'response', 'error'
        """
        try:
            # Save user message
            self.save_message(user_id, 'user', message)
            
            # Check if Gemini is available
            if not self.client:
                # Fallback response
                fallback = self._get_fallback_response(message, language)
                self.save_message(user_id, 'assistant', fallback)
                return {
                    'success': True,
                    'response': fallback,
                    'fallback': True
                }
            
            # Build messages
            system_prompt, messages = self._build_messages(
                user_id, message, language, analysis_context, plants_context
            )
            
            # Format for Gemini
            chat_content = f"{system_prompt}\n\n"
            for msg in messages:
                role_label = "User" if msg['role'] == 'user' else "Assistant"
                chat_content += f"{role_label}: {msg['content']}\n\n"
            chat_content += "Assistant:"
            
            # Get GenerateContentConfig for proper config format
            from google.genai.types import GenerateContentConfig
            
            # Call Gemini API - try multiple models
            model_names = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
            response = None
            last_error = None
            
            for model_name in model_names:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=chat_content,
                        config=GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=1024
                        )
                    )
                    if response and response.text:
                        break
                except Exception as e:
                    last_error = str(e)
                    current_app.logger.warning(f"Chat model {model_name} failed: {e}")
                    continue
            
            if not response or not response.text:
                raise Exception(f"All models failed. Last error: {last_error}")
            
            assistant_response = response.text.strip()
            
            # Save assistant response
            self.save_message(user_id, 'assistant', assistant_response)
            
            return {
                'success': True,
                'response': assistant_response
            }
            
        except Exception as e:
            current_app.logger.error(f"Chat error: {e}")
            error_str = str(e)
            
            # Check if it's a rate limit error
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                # Try keyword-based fallback first
                keyword_response = self._get_fallback_response(message, language)
                
                # Check if we got a specific response (not the default)
                default_responses = {
                    'en': "I'd be happy to help with your plant care questions!",
                    'hi': "मुझे आपके पौधों की देखभाल के सवालों में मदद करने में खुशी होगी!",
                    'mr': "मला तुमच्या वनस्पती काळजीच्या प्रश्नांमध्ये मदत करण्यात आनंद होईल!"
                }
                default_check = default_responses.get(language, default_responses['en'])
                
                if not keyword_response.startswith(default_check[:20]):
                    # We got a specific keyword-based response
                    fallback = keyword_response
                else:
                    # Use rate limit message
                    rate_limit_msg = {
                        'en': "I'm temporarily unavailable due to high usage. Please try again in a few minutes. In the meantime, you can ask me basic questions about watering, sunlight, or fertilizing!",
                        'hi': "उच्च उपयोग के कारण मैं अस्थायी रूप से अनुपलब्ध हूं। कृपया कुछ मिनटों में पुनः प्रयास करें। इस बीच, आप मुझसे पानी देने, धूप या खाद के बारे में बुनियादी सवाल पूछ सकते हैं!",
                        'mr': "जास्त वापरामुळे मी तात्पुरता अनुपलब्ध आहे. कृपया काही मिनिटांत पुन्हा प्रयत्न करा. दरम्यान, तुम्ही मला पाणी देणे, सूर्यप्रकाश किंवा खताबद्दल मूलभूत प्रश्न विचारू शकता!"
                    }
                    fallback = rate_limit_msg.get(language, rate_limit_msg['en'])
                
                return {
                    'success': True,  # Return success so UI doesn't show error
                    'response': fallback,
                    'fallback': True,
                    'rate_limited': True
                }
            
            # For other errors, try to give a helpful fallback
            fallback = self._get_fallback_response(message, language)
            return {
                'success': True,  # Return success with fallback
                'response': fallback,
                'fallback': True,
                'error': str(e)
            }
    
    def _get_fallback_response(self, message: str, language: str) -> str:
        """Get a fallback response when AI is not available."""
        message_lower = message.lower()
        
        # Simple keyword-based responses
        responses = {
            'water': {
                'en': "Most plants need watering when the top inch of soil is dry. Check by sticking your finger in the soil. Water thoroughly until it drains from the bottom, then let the soil dry before watering again.",
                'hi': "अधिकांश पौधों को पानी की जरूरत होती है जब मिट्टी की ऊपरी इंच सूख जाती है। अपनी उंगली मिट्टी में डालकर जांचें। अच्छी तरह से पानी दें जब तक यह नीचे से न निकल जाए, फिर दोबारा पानी देने से पहले मिट्टी को सूखने दें।",
                'mr': "बहुतेक रोपांना पाणी लागते जेव्हा मातीचा वरचा इंच कोरडा असतो. आपले बोट मातीत घालून तपासा. चांगले पाणी द्या जोपर्यंत ते तळातून निघत नाही, नंतर पुन्हा पाणी देण्यापूर्वी माती कोरडी होऊ द्या."
            },
            'fertiliz': {
                'en': "Fertilize your plants during the growing season (spring and summer) with a balanced fertilizer. Most houseplants benefit from monthly feeding. Reduce or stop fertilizing in fall and winter.",
                'hi': "बढ़ते मौसम (वसंत और गर्मी) में संतुलित खाद के साथ अपने पौधों को खाद दें। अधिकांश घरेलू पौधों को मासिक खाद से लाभ होता है। पतझड़ और सर्दियों में खाद कम करें या बंद करें।",
                'mr': "वाढीच्या हंगामात (वसंत आणि उन्हाळा) संतुलित खतासह आपल्या रोपांना खत द्या. बहुतेक घरातील रोपांना मासिक खाद्याचा फायदा होतो. शरद ऋतू आणि हिवाळ्यात खत कमी करा किंवा थांबवा."
            },
            'disease': {
                'en': "Common plant diseases include powdery mildew, root rot, and leaf spot. Prevention includes good air circulation, proper watering (not overwatering), and keeping leaves dry. Remove affected parts promptly.",
                'hi': "सामान्य पौधों की बीमारियों में पाउडरी मिल्ड्यू, जड़ सड़न और पत्ती धब्बा शामिल हैं। रोकथाम में अच्छा वायु संचार, उचित पानी देना (अधिक पानी नहीं), और पत्तियों को सूखा रखना शामिल है।",
                'mr': "सामान्य वनस्पती रोगांमध्ये पावडरी मिल्ड्यू, मुळांचा कुजणे आणि पानांवर डाग यांचा समावेश होतो. प्रतिबंधात चांगले हवा परिसंचरण, योग्य पाणी देणे (जास्त पाणी नाही), आणि पाने कोरडी ठेवणे समाविष्ट आहे."
            },
            'sunlight': {
                'en': "Most flowering plants need 6+ hours of direct sunlight. Foliage plants often prefer bright, indirect light. Signs of too little light: leggy growth, pale leaves. Too much light: scorched, yellow leaves.",
                'hi': "अधिकांश फूल वाले पौधों को 6+ घंटे सीधी धूप की जरूरत होती है। पत्तेदार पौधे अक्सर उज्ज्वल, अप्रत्यक्ष प्रकाश पसंद करते हैं। कम प्रकाश के संकेत: लंबी वृद्धि, पीली पत्तियां। बहुत अधिक प्रकाश: झुलसी, पीली पत्तियां।",
                'mr': "बहुतेक फुलांच्या रोपांना 6+ तास थेट सूर्यप्रकाशाची आवश्यकता असते. पर्णसंभार रोपे अनेकदा तेजस्वी, अप्रत्यक्ष प्रकाश पसंत करतात. खूप कमी प्रकाशाची चिन्हे: लांब वाढ, फिकट पाने. खूप जास्त प्रकाश: जळालेली, पिवळी पाने."
            },
            'hello': {
                'en': "Hello! I'm your plant care assistant. How can I help you with your plants today?",
                'hi': "नमस्ते! मैं आपका पौधा देखभाल सहायक हूं। आज मैं आपके पौधों के साथ कैसे मदद कर सकता हूं?",
                'mr': "नमस्कार! मी तुमचा वनस्पती काळजी सहाय्यक आहे. आज मी तुमच्या रोपांसाठी कशी मदत करू शकतो?"
            }
        }
        
        # Find matching response
        for keyword, response_dict in responses.items():
            if keyword in message_lower:
                return response_dict.get(language, response_dict['en'])
        
        # Default response
        default_responses = {
            'en': "I'd be happy to help with your plant care questions! You can ask me about watering, fertilizing, sunlight, diseases, or any other plant care topics.",
            'hi': "मुझे आपके पौधों की देखभाल के सवालों में मदद करने में खुशी होगी! आप मुझसे पानी देने, खाद देने, धूप, बीमारियों या किसी भी पौधों की देखभाल के विषय पर पूछ सकते हैं।",
            'mr': "मला तुमच्या वनस्पती काळजीच्या प्रश्नांमध्ये मदत करण्यात आनंद होईल! तुम्ही मला पाणी देणे, खत देणे, सूर्यप्रकाश, रोग किंवा इतर कोणत्याही वनस्पती काळजी विषयांबद्दल विचारू शकता."
        }
        
        return default_responses.get(language, default_responses['en'])
    
    def get_quick_suggestions(self, language: str = 'en') -> List[str]:
        """Get quick suggestion chips for chat."""
        suggestions = {
            'en': [
                "How often should I water my plants?",
                "My plant leaves are turning yellow",
                "Best fertilizer for indoor plants?",
                "How to prevent plant diseases?",
                "When should I repot my plant?"
            ],
            'hi': [
                "मुझे अपने पौधों को कितनी बार पानी देना चाहिए?",
                "मेरे पौधे की पत्तियां पीली हो रही हैं",
                "घरेलू पौधों के लिए सबसे अच्छी खाद?",
                "पौधों की बीमारियों को कैसे रोकें?",
                "मुझे अपने पौधे को कब दोबारा गमले में लगाना चाहिए?"
            ],
            'mr': [
                "मी माझ्या रोपांना किती वेळा पाणी द्यावे?",
                "माझ्या रोपाची पाने पिवळी होत आहेत",
                "घरातील रोपांसाठी सर्वोत्तम खत?",
                "वनस्पती रोग कसे टाळावे?",
                "मी माझे रोप केव्हा पुन्हा कुंडीत लावावे?"
            ]
        }
        
        return suggestions.get(language, suggestions['en'])


# Global chat service instance
chat_service = ChatService()


def init_chat_service(db):
    """Initialize chat service with database."""
    chat_service.set_db(db)
    return chat_service
