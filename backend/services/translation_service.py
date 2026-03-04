"""
Translation service for multi-language support.
Supports English (en), Hindi (hi), and Marathi (mr).
"""

from typing import Dict, Optional


# ============================================================================
# Translation Dictionaries
# ============================================================================

TRANSLATIONS = {
    # -------------------------------------------------------------------------
    # Common UI Labels
    # -------------------------------------------------------------------------
    'app_name': {
        'en': 'Smart Plant Health Assistant',
        'hi': 'स्मार्ट पौधा स्वास्थ्य सहायक',
        'mr': 'स्मार्ट वनस्पती आरोग्य सहाय्यक'
    },
    'welcome': {
        'en': 'Welcome',
        'hi': 'स्वागत है',
        'mr': 'स्वागत आहे'
    },
    'login': {
        'en': 'Login',
        'hi': 'लॉगिन',
        'mr': 'लॉगिन'
    },
    'register': {
        'en': 'Register',
        'hi': 'पंजीकरण',
        'mr': 'नोंदणी'
    },
    'logout': {
        'en': 'Logout',
        'hi': 'लॉगआउट',
        'mr': 'लॉगआउट'
    },
    'dashboard': {
        'en': 'Dashboard',
        'hi': 'डैशबोर्ड',
        'mr': 'डॅशबोर्ड'
    },
    'my_plants': {
        'en': 'My Plants',
        'hi': 'मेरे पौधे',
        'mr': 'माझी रोपे'
    },
    'history': {
        'en': 'History',
        'hi': 'इतिहास',
        'mr': 'इतिहास'
    },
    'settings': {
        'en': 'Settings',
        'hi': 'सेटिंग्स',
        'mr': 'सेटिंग्ज'
    },
    'notifications': {
        'en': 'Notifications',
        'hi': 'सूचनाएं',
        'mr': 'सूचना'
    },
    'analyze': {
        'en': 'Analyze',
        'hi': 'विश्लेषण करें',
        'mr': 'विश्लेषण करा'
    },
    'upload': {
        'en': 'Upload',
        'hi': 'अपलोड करें',
        'mr': 'अपलोड करा'
    },
    'capture': {
        'en': 'Capture',
        'hi': 'कैप्चर करें',
        'mr': 'कॅप्चर करा'
    },
    'submit': {
        'en': 'Submit',
        'hi': 'जमा करें',
        'mr': 'सबमिट करा'
    },
    'cancel': {
        'en': 'Cancel',
        'hi': 'रद्द करें',
        'mr': 'रद्द करा'
    },
    'save': {
        'en': 'Save',
        'hi': 'सहेजें',
        'mr': 'जतन करा'
    },
    'delete': {
        'en': 'Delete',
        'hi': 'हटाएं',
        'mr': 'हटवा'
    },
    'edit': {
        'en': 'Edit',
        'hi': 'संपादित करें',
        'mr': 'संपादित करा'
    },
    'add': {
        'en': 'Add',
        'hi': 'जोड़ें',
        'mr': 'जोडा'
    },
    'search': {
        'en': 'Search',
        'hi': 'खोजें',
        'mr': 'शोधा'
    },
    'loading': {
        'en': 'Loading...',
        'hi': 'लोड हो रहा है...',
        'mr': 'लोड होत आहे...'
    },
    'error': {
        'en': 'Error',
        'hi': 'त्रुटि',
        'mr': 'त्रुटी'
    },
    'success': {
        'en': 'Success',
        'hi': 'सफलता',
        'mr': 'यश'
    },
    
    # -------------------------------------------------------------------------
    # Plant Analysis
    # -------------------------------------------------------------------------
    'plant_analysis': {
        'en': 'Plant Analysis',
        'hi': 'पौधे का विश्लेषण',
        'mr': 'वनस्पती विश्लेषण'
    },
    'health_score': {
        'en': 'Health Score',
        'hi': 'स्वास्थ्य स्कोर',
        'mr': 'आरोग्य स्कोर'
    },
    'disease_detected': {
        'en': 'Disease Detected',
        'hi': 'रोग पाया गया',
        'mr': 'रोग आढळला'
    },
    'no_disease': {
        'en': 'No Disease Detected',
        'hi': 'कोई रोग नहीं पाया गया',
        'mr': 'कोणताही रोग आढळला नाही'
    },
    'healthy': {
        'en': 'Healthy',
        'hi': 'स्वस्थ',
        'mr': 'निरोगी'
    },
    'severity': {
        'en': 'Severity',
        'hi': 'गंभीरता',
        'mr': 'तीव्रता'
    },
    'mild': {
        'en': 'Mild',
        'hi': 'हल्का',
        'mr': 'सौम्य'
    },
    'moderate': {
        'en': 'Moderate',
        'hi': 'मध्यम',
        'mr': 'मध्यम'
    },
    'severe': {
        'en': 'Severe',
        'hi': 'गंभीर',
        'mr': 'गंभीर'
    },
    'confidence': {
        'en': 'Confidence',
        'hi': 'विश्वास',
        'mr': 'आत्मविश्वास'
    },
    'plant_type': {
        'en': 'Plant Type',
        'hi': 'पौधे का प्रकार',
        'mr': 'वनस्पती प्रकार'
    },
    'care_plan': {
        'en': 'Care Plan',
        'hi': 'देखभाल योजना',
        'mr': 'काळजी योजना'
    },
    'recommendations': {
        'en': 'Recommendations',
        'hi': 'सिफारिशें',
        'mr': 'शिफारसी'
    },
    'treatment': {
        'en': 'Treatment',
        'hi': 'उपचार',
        'mr': 'उपचार'
    },
    'prevention': {
        'en': 'Prevention',
        'hi': 'रोकथाम',
        'mr': 'प्रतिबंध'
    },
    'download_report': {
        'en': 'Download Report',
        'hi': 'रिपोर्ट डाउनलोड करें',
        'mr': 'अहवाल डाउनलोड करा'
    },
    'download_pdf': {
        'en': 'Download PDF',
        'hi': 'PDF डाउनलोड करें',
        'mr': 'PDF डाउनलोड करा'
    },
    'download_image': {
        'en': 'Save as Image',
        'hi': 'छवि के रूप में सहेजें',
        'mr': 'प्रतिमा म्हणून जतन करा'
    },
    
    # -------------------------------------------------------------------------
    # Plant Care
    # -------------------------------------------------------------------------
    'watering': {
        'en': 'Watering',
        'hi': 'पानी देना',
        'mr': 'पाणी देणे'
    },
    'fertilizing': {
        'en': 'Fertilizing',
        'hi': 'खाद देना',
        'mr': 'खत देणे'
    },
    'sunlight': {
        'en': 'Sunlight',
        'hi': 'धूप',
        'mr': 'सूर्यप्रकाश'
    },
    'temperature': {
        'en': 'Temperature',
        'hi': 'तापमान',
        'mr': 'तापमान'
    },
    'humidity': {
        'en': 'Humidity',
        'hi': 'आर्द्रता',
        'mr': 'आर्द्रता'
    },
    'soil': {
        'en': 'Soil',
        'hi': 'मिट्टी',
        'mr': 'माती'
    },
    'pruning': {
        'en': 'Pruning',
        'hi': 'छंटाई',
        'mr': 'छाटणी'
    },
    'repotting': {
        'en': 'Repotting',
        'hi': 'पुनः गमले में लगाना',
        'mr': 'पुनः कुंडीत लावणे'
    },
    
    # -------------------------------------------------------------------------
    # Reminders & Notifications
    # -------------------------------------------------------------------------
    'reminder': {
        'en': 'Reminder',
        'hi': 'अनुस्मारक',
        'mr': 'स्मरणपत्र'
    },
    'water_reminder': {
        'en': 'Time to water your plant!',
        'hi': 'अपने पौधे को पानी देने का समय!',
        'mr': 'तुमच्या रोपाला पाणी देण्याची वेळ!'
    },
    'fertilize_reminder': {
        'en': 'Time to fertilize your plant!',
        'hi': 'अपने पौधे को खाद देने का समय!',
        'mr': 'तुमच्या रोपाला खत देण्याची वेळ!'
    },
    'prune_reminder': {
        'en': 'Time to prune your plant!',
        'hi': 'अपने पौधे की छंटाई करने का समय!',
        'mr': 'तुमच्या रोपाची छाटणी करण्याची वेळ!'
    },
    'check_health_reminder': {
        'en': 'Check your plant\'s health',
        'hi': 'अपने पौधे की स्वास्थ्य जांच करें',
        'mr': 'तुमच्या रोपाचे आरोग्य तपासा'
    },
    'set_reminder': {
        'en': 'Set Reminder',
        'hi': 'अनुस्मारक सेट करें',
        'mr': 'स्मरणपत्र सेट करा'
    },
    'reminder_frequency': {
        'en': 'Reminder Frequency',
        'hi': 'अनुस्मारक आवृत्ति',
        'mr': 'स्मरणपत्र वारंवारता'
    },
    'every_day': {
        'en': 'Every day',
        'hi': 'हर दिन',
        'mr': 'दररोज'
    },
    'every_week': {
        'en': 'Every week',
        'hi': 'हर सप्ताह',
        'mr': 'दर आठवड्याला'
    },
    'every_month': {
        'en': 'Every month',
        'hi': 'हर महीने',
        'mr': 'दर महिन्याला'
    },
    'no_notifications': {
        'en': 'No notifications',
        'hi': 'कोई सूचना नहीं',
        'mr': 'कोणतीही सूचना नाही'
    },
    'mark_as_read': {
        'en': 'Mark as read',
        'hi': 'पढ़ा हुआ चिह्नित करें',
        'mr': 'वाचलेले म्हणून चिन्हांकित करा'
    },
    
    # -------------------------------------------------------------------------
    # Dashboard
    # -------------------------------------------------------------------------
    'recent_analyses': {
        'en': 'Recent Analyses',
        'hi': 'हाल के विश्लेषण',
        'mr': 'अलीकडील विश्लेषणे'
    },
    'upcoming_reminders': {
        'en': 'Upcoming Reminders',
        'hi': 'आगामी अनुस्मारक',
        'mr': 'आगामी स्मरणपत्रे'
    },
    'total_plants': {
        'en': 'Total Plants',
        'hi': 'कुल पौधे',
        'mr': 'एकूण रोपे'
    },
    'analyses_this_month': {
        'en': 'Analyses This Month',
        'hi': 'इस महीने के विश्लेषण',
        'mr': 'या महिन्यातील विश्लेषणे'
    },
    'quick_actions': {
        'en': 'Quick Actions',
        'hi': 'त्वरित क्रियाएं',
        'mr': 'जलद क्रिया'
    },
    'analyze_plant': {
        'en': 'Analyze Plant',
        'hi': 'पौधे का विश्लेषण करें',
        'mr': 'वनस्पती विश्लेषण करा'
    },
    'add_plant': {
        'en': 'Add Plant',
        'hi': 'पौधा जोड़ें',
        'mr': 'रोप जोडा'
    },
    'view_history': {
        'en': 'View History',
        'hi': 'इतिहास देखें',
        'mr': 'इतिहास पहा'
    },
    
    # -------------------------------------------------------------------------
    # Chatbot
    # -------------------------------------------------------------------------
    'chat_assistant': {
        'en': 'Plant Care Assistant',
        'hi': 'पौधा देखभाल सहायक',
        'mr': 'वनस्पती काळजी सहाय्यक'
    },
    'chat_placeholder': {
        'en': 'Ask me anything about plant care...',
        'hi': 'पौधों की देखभाल के बारे में कुछ भी पूछें...',
        'mr': 'वनस्पती काळजीबद्दल काहीही विचारा...'
    },
    'chat_welcome': {
        'en': 'Hello! I\'m your plant care assistant. How can I help you today?',
        'hi': 'नमस्ते! मैं आपका पौधा देखभाल सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
        'mr': 'नमस्कार! मी तुमचा वनस्पती काळजी सहाय्यक आहे. आज मी तुम्हाला कशी मदत करू शकतो?'
    },
    'typing': {
        'en': 'Typing...',
        'hi': 'टाइप कर रहा है...',
        'mr': 'टाइप करत आहे...'
    },
    'send': {
        'en': 'Send',
        'hi': 'भेजें',
        'mr': 'पाठवा'
    },
    'clear_chat': {
        'en': 'Clear Chat',
        'hi': 'चैट साफ़ करें',
        'mr': 'चॅट साफ करा'
    },
    
    # -------------------------------------------------------------------------
    # Forms & Inputs
    # -------------------------------------------------------------------------
    'email': {
        'en': 'Email',
        'hi': 'ईमेल',
        'mr': 'ईमेल'
    },
    'password': {
        'en': 'Password',
        'hi': 'पासवर्ड',
        'mr': 'पासवर्ड'
    },
    'name': {
        'en': 'Name',
        'hi': 'नाम',
        'mr': 'नाव'
    },
    'plant_name': {
        'en': 'Plant Name',
        'hi': 'पौधे का नाम',
        'mr': 'वनस्पतीचे नाव'
    },
    'species': {
        'en': 'Species',
        'hi': 'प्रजाति',
        'mr': 'प्रजाती'
    },
    'location': {
        'en': 'Location',
        'hi': 'स्थान',
        'mr': 'स्थान'
    },
    'indoor': {
        'en': 'Indoor',
        'hi': 'घर के अंदर',
        'mr': 'घरातील'
    },
    'outdoor': {
        'en': 'Outdoor',
        'hi': 'बाहर',
        'mr': 'बाहेरील'
    },
    'garden': {
        'en': 'Garden',
        'hi': 'बगीचा',
        'mr': 'बाग'
    },
    'balcony': {
        'en': 'Balcony',
        'hi': 'बालकनी',
        'mr': 'बाल्कनी'
    },
    'notes': {
        'en': 'Notes',
        'hi': 'नोट्स',
        'mr': 'नोट्स'
    },
    'select_language': {
        'en': 'Select Language',
        'hi': 'भाषा चुनें',
        'mr': 'भाषा निवडा'
    },
    'english': {
        'en': 'English',
        'hi': 'अंग्रेज़ी',
        'mr': 'इंग्रजी'
    },
    'hindi': {
        'en': 'Hindi',
        'hi': 'हिंदी',
        'mr': 'हिंदी'
    },
    'marathi': {
        'en': 'Marathi',
        'hi': 'मराठी',
        'mr': 'मराठी'
    },
    
    # -------------------------------------------------------------------------
    # Messages
    # -------------------------------------------------------------------------
    'login_success': {
        'en': 'Login successful',
        'hi': 'लॉगिन सफल',
        'mr': 'लॉगिन यशस्वी'
    },
    'login_failed': {
        'en': 'Login failed',
        'hi': 'लॉगिन विफल',
        'mr': 'लॉगिन अयशस्वी'
    },
    'register_success': {
        'en': 'Registration successful',
        'hi': 'पंजीकरण सफल',
        'mr': 'नोंदणी यशस्वी'
    },
    'register_failed': {
        'en': 'Registration failed',
        'hi': 'पंजीकरण विफल',
        'mr': 'नोंदणी अयशस्वी'
    },
    'analysis_complete': {
        'en': 'Analysis complete',
        'hi': 'विश्लेषण पूर्ण',
        'mr': 'विश्लेषण पूर्ण'
    },
    'analysis_failed': {
        'en': 'Analysis failed',
        'hi': 'विश्लेषण विफल',
        'mr': 'विश्लेषण अयशस्वी'
    },
    'plant_added': {
        'en': 'Plant added successfully',
        'hi': 'पौधा सफलतापूर्वक जोड़ा गया',
        'mr': 'रोप यशस्वीरित्या जोडले'
    },
    'plant_updated': {
        'en': 'Plant updated successfully',
        'hi': 'पौधा सफलतापूर्वक अपडेट किया गया',
        'mr': 'रोप यशस्वीरित्या अद्यतनित केले'
    },
    'plant_deleted': {
        'en': 'Plant deleted successfully',
        'hi': 'पौधा सफलतापूर्वक हटाया गया',
        'mr': 'रोप यशस्वीरित्या हटवले'
    },
    'reminder_set': {
        'en': 'Reminder set successfully',
        'hi': 'अनुस्मारक सफलतापूर्वक सेट किया गया',
        'mr': 'स्मरणपत्र यशस्वीरित्या सेट केले'
    },
    'no_image_selected': {
        'en': 'Please select an image',
        'hi': 'कृपया एक छवि चुनें',
        'mr': 'कृपया एक प्रतिमा निवडा'
    },
    'invalid_file_type': {
        'en': 'Invalid file type. Please upload an image.',
        'hi': 'अमान्य फ़ाइल प्रकार। कृपया एक छवि अपलोड करें।',
        'mr': 'अवैध फाइल प्रकार. कृपया एक प्रतिमा अपलोड करा.'
    },
    'confirm_delete': {
        'en': 'Are you sure you want to delete this?',
        'hi': 'क्या आप वाकई इसे हटाना चाहते हैं?',
        'mr': 'तुम्हाला खात्री आहे की तुम्ही हे हटवू इच्छिता?'
    },
    'session_expired': {
        'en': 'Session expired. Please login again.',
        'hi': 'सत्र समाप्त। कृपया फिर से लॉगिन करें।',
        'mr': 'सत्र संपले. कृपया पुन्हा लॉगिन करा.'
    },
    'network_error': {
        'en': 'Network error. Please check your connection.',
        'hi': 'नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।',
        'mr': 'नेटवर्क त्रुटी. कृपया तुमचे कनेक्शन तपासा.'
    },
}


# ============================================================================
# Translation Functions
# ============================================================================

def get_text(key: str, lang: str = 'en', default: str = None) -> str:
    """
    Get translated text for a key.
    
    Args:
        key: Translation key
        lang: Language code (en, hi, mr)
        default: Default value if key not found
    
    Returns:
        Translated text
    """
    if key not in TRANSLATIONS:
        return default if default else key
    
    translations = TRANSLATIONS[key]
    
    # Fall back to English if language not available
    if lang not in translations:
        lang = 'en'
    
    return translations.get(lang, default if default else key)


def t(key: str, lang: str = 'en') -> str:
    """Shorthand for get_text."""
    return get_text(key, lang)


def get_all_translations(lang: str = 'en') -> Dict[str, str]:
    """
    Get all translations for a language.
    
    Args:
        lang: Language code
    
    Returns:
        Dictionary of all translations
    """
    result = {}
    for key, translations in TRANSLATIONS.items():
        result[key] = translations.get(lang, translations.get('en', key))
    return result


def get_supported_languages() -> list:
    """Get list of supported languages."""
    return [
        {'code': 'en', 'name': 'English', 'native': 'English'},
        {'code': 'hi', 'name': 'Hindi', 'native': 'हिंदी'},
        {'code': 'mr', 'name': 'Marathi', 'native': 'मराठी'}
    ]


def translate_ai_prompt(prompt: str, lang: str) -> str:
    """
    Add language instruction to AI prompt.
    
    Args:
        prompt: Original prompt
        lang: Target language code
    
    Returns:
        Modified prompt with language instruction
    """
    if lang == 'en':
        return prompt
    
    lang_names = {
        'hi': 'Hindi',
        'mr': 'Marathi'
    }
    
    lang_name = lang_names.get(lang, 'English')
    
    return f"{prompt}\n\nIMPORTANT: Please respond in {lang_name}."


class TranslationService:
    """Service class for translations with context support."""
    
    def __init__(self, default_lang: str = 'en'):
        self.default_lang = default_lang
    
    def get(self, key: str, lang: str = None) -> str:
        """Get translated text."""
        return get_text(key, lang or self.default_lang)
    
    def t(self, key: str, lang: str = None) -> str:
        """Shorthand for get."""
        return self.get(key, lang)
    
    def get_all(self, lang: str = None) -> Dict[str, str]:
        """Get all translations for a language."""
        return get_all_translations(lang or self.default_lang)
    
    def set_default_lang(self, lang: str):
        """Set default language."""
        if lang in ['en', 'hi', 'mr']:
            self.default_lang = lang


# Global translation service instance
translation_service = TranslationService()
