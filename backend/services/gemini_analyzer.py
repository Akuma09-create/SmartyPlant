"""
Gemini AI Analyzer for Smart Plant Health Assistant.
Uses the NEW google-genai SDK with Google Search Grounding
so Gemini can search the internet for real disease info, cures, and treatments.
"""

import os
import json
import logging
import re
from typing import Dict, Optional, Tuple
from io import BytesIO

logger = logging.getLogger(__name__)


# ── Language instruction for prompts ──────────────
LANGUAGE_INSTRUCTIONS = {
    'hi': '''

**CRITICAL LANGUAGE REQUIREMENT:**
आपको हिंदी में जवाब देना होगा।
You MUST write ALL text values in the JSON response in HINDI (हिंदी) language.
This includes: disease_name, description, symptoms_observed, causes, immediate_actions, treatment options, prevention tips, and ALL other text fields.
Only keep scientific names in English (Latin). Everything else must be in Hindi using Devanagari script.
Example: "disease_name": "चूर्ण आसिता (Powdery Mildew)"
''',
    'mr': '''

**CRITICAL LANGUAGE REQUIREMENT:**
तुम्हाला मराठीत उत्तर द्यायचे आहे.
You MUST write ALL text values in the JSON response in MARATHI (मराठी) language.
This includes: disease_name, description, symptoms_observed, causes, immediate_actions, treatment options, prevention tips, and ALL other text fields.
Only keep scientific names in English (Latin). Everything else must be in Marathi using Devanagari script.
Example: "disease_name": "भुरी बुरशी (Powdery Mildew)"
''',
    'en': ''  # English is default, no extra instruction needed
}


# ── Step 1 prompt: Identify the plant + disease from the image ──────────────
IMAGE_ANALYSIS_PROMPT_BASE = """You are an expert plant pathologist and botanist.
Analyze this plant image carefully.

1. IDENTIFY the plant species (common name and scientific name).
2. DIAGNOSE any disease, pest, or health issue visible.
3. List all SYMPTOMS you can see in the image.

Respond ONLY with valid JSON (no markdown, no code blocks):
{
  "plant_info": {
    "common_name": "e.g. Tomato",
    "scientific_name": "e.g. Solanum lycopersicum",
    "family": "e.g. Solanaceae",
    "plant_type": "herb/shrub/tree/vine/succulent/grass/flower/vegetable/fruit",
    "origin": "Native region",
    "description": "1-2 sentence description of this plant",
    "ideal_conditions": {
      "sunlight": "Full sun / Partial shade / Shade",
      "temperature": "e.g. 18-30C",
      "humidity": "Low / Medium / High",
      "soil": "e.g. Well-drained loamy soil"
    },
    "general_care": {
      "watering": "Watering needs",
      "fertilizing": "Fertilizer schedule",
      "pruning": "Pruning advice",
      "common_issues": ["Issue 1", "Issue 2"]
    }
  },
  "is_healthy": false,
  "disease_name": "Exact disease name or 'Healthy'",
  "disease_type": "fungal/bacterial/viral/pest/nutrient_deficiency/environmental/healthy",
  "confidence": 85,
  "severity": "mild/moderate/severe/none",
  "health_score": 45,
  "symptoms_observed": ["symptom 1", "symptom 2", "symptom 3"]
}

IMPORTANT:
- Be SPECIFIC about the disease - use real pathological names (e.g. "Early Blight", "Powdery Mildew", "Bacterial Leaf Spot")
- List ALL visible symptoms clearly
- If healthy, set health_score above 80 and disease_name to "Healthy"
"""


def get_image_analysis_prompt(lang: str = 'en') -> str:
    """Get the image analysis prompt with language instruction."""
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, '')
    if lang_instruction:
        # Add language instruction at the BEGINNING for better compliance
        return lang_instruction + "\n\n" + IMAGE_ANALYSIS_PROMPT_BASE
    return IMAGE_ANALYSIS_PROMPT_BASE


# ── Step 2: Search internet for detailed disease info & cures ────────
def get_disease_search_prompt(plant_name, disease_name, symptoms, lang: str = 'en'):
    """Build a prompt that tells Gemini to search the internet for disease details."""
    symptom_text = ", ".join(symptoms) if symptoms else "general decline"
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(lang, '')
    
    base_prompt = f"""Search the internet for comprehensive information about the plant disease described below.
Find REAL, up-to-date treatment solutions, specific product names, and scientific information.

Plant: {plant_name}
Disease: {disease_name}
Symptoms observed: {symptom_text}

Search for and provide ALL of the following in valid JSON format (no markdown, no code blocks):
{{
  "description": "Detailed 3-5 sentence description of this disease - what causes it, how it spreads, and how it affects the plant. Include the scientific name of the pathogen if applicable.",
  "causes": [
    "Primary cause (e.g. specific pathogen name and conditions that favor it)",
    "Secondary contributing factor",
    "Environmental factor that promotes this disease"
  ],
  "immediate_actions": [
    "Step 1: Most urgent action with specific instructions",
    "Step 2: Second priority action",
    "Step 3: Additional immediate step"
  ],
  "treatment": {{
    "organic": [
      "Specific organic treatment with exact dosage and application frequency (e.g. 'Neem oil spray - mix 2 tsp per liter of water, apply every 7 days')",
      "Another organic remedy with method"
    ],
    "chemical": [
      "Specific fungicide/pesticide product NAME with application instructions (e.g. 'Chlorothalonil (Daconil) - apply at 2 tsp per gallon every 7-10 days')",
      "Alternative chemical treatment with dosage"
    ],
    "cultural": [
      "Specific watering adjustment",
      "Environmental change needed",
      "Pruning or maintenance step"
    ]
  }},
  "prevention": [
    "Specific prevention measure for this disease on this plant",
    "Long-term care practice",
    "Environmental condition to maintain"
  ],
  "watering_advice": {{
    "frequency": "Specific watering schedule for this plant when dealing with this disease",
    "method": "Best watering method (e.g. drip irrigation at soil level)",
    "amount": "How much water"
  }},
  "recovery_timeline": {{
    "first_improvement": "When to expect first improvement (e.g. '5-7 days with fungicide treatment')",
    "significant_recovery": "When major recovery happens",
    "full_recovery": "Expected full recovery time"
  }},
  "risk_if_untreated": "What will happen if this condition is not treated - be specific about progression"
}}

IMPORTANT: Search the internet for the LATEST and most ACCURATE treatment information.
Include specific product names, dosages, and frequencies that are commonly available.
Give REAL, practical advice a home gardener can follow immediately."""

    if lang_instruction:
        # Add language instruction at the BEGINNING for better compliance
        return lang_instruction + "\n\n" + base_prompt
    return base_prompt


class GeminiAnalyzer:
    """
    Analyzes plant images using Google Gemini API with Google Search Grounding.
    
    Two-step process:
    1. Analyze image -> identify plant + disease + symptoms
    2. Search internet (via Google Search grounding) -> get detailed cure & treatment info
    
    This ensures the app provides real, internet-sourced disease information and cures.
    
    Supports multiple API keys for rotation when rate limited.
    Set GEMINI_API_KEYS=key1,key2,key3 or GEMINI_API_KEY + GEMINI_API_KEY_2 + GEMINI_API_KEY_3
    """

    def __init__(self, api_key=None):
        """Initialize Gemini analyzer with API key rotation support."""
        # Collect all available API keys
        self._api_keys = []
        self._current_key_index = 0
        
        # Single key passed directly
        if api_key:
            self._api_keys.append(api_key)
        
        # Comma-separated keys in GEMINI_API_KEYS
        keys_str = os.getenv('GEMINI_API_KEYS', '')
        if keys_str:
            self._api_keys.extend([k.strip() for k in keys_str.split(',') if k.strip()])
        
        # Individual keys: GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.
        primary_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if primary_key and primary_key not in self._api_keys:
            self._api_keys.insert(0, primary_key)
        
        for i in range(2, 10):  # Support up to 9 keys
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key and key not in self._api_keys:
                self._api_keys.append(key)
        
        self._client = None
        self._initialized = False
        self._genai = None
        self.api_key = None
        # Preferred model order
        self._model_names = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']

        if self._api_keys:
            self._init_client(self._api_keys[0])
            logger.info("Gemini AI analyzer initialized with %d API key(s)", len(self._api_keys))
        else:
            logger.info("No Gemini API key found. Set GEMINI_API_KEY for AI analysis.")

    def _init_client(self, api_key):
        """Initialize client with specific API key."""
        try:
            from google import genai
            self._client = genai.Client(api_key=api_key)
            self._genai = genai
            self._initialized = True
            self.api_key = api_key
            return True
        except Exception as e:
            logger.warning("Failed to initialize Gemini with key: %s", e)
            self._initialized = False
            return False

    def _rotate_key(self):
        """Rotate to next API key when rate limited. Returns True if rotated successfully."""
        if len(self._api_keys) <= 1:
            logger.warning("No additional API keys to rotate to")
            return False
        
        self._current_key_index = (self._current_key_index + 1) % len(self._api_keys)
        new_key = self._api_keys[self._current_key_index]
        logger.info("Rotating to API key %d of %d", self._current_key_index + 1, len(self._api_keys))
        return self._init_client(new_key)

    @property
    def is_available(self):
        return self._initialized and self._client is not None

    def analyze_image(self, image_file, lang: str = 'en'):
        """
        Analyze a plant image using Gemini Vision API + Google Search grounding.

        Two-step process:
        1. Send image to Gemini -> identify plant and disease
        2. Use Google Search grounding -> search internet for disease cure and treatment

        Args:
            image_file: Image file to analyze
            lang: Language code for response (en, hi, mr). Default is 'en' (English)

        Returns:
            Tuple of (analysis_result dict or None, message string)
        """
        # Validate language code
        if lang not in ['en', 'hi', 'mr']:
            lang = 'en'
        if not self.is_available:
            return None, "Gemini AI not configured. Set GEMINI_API_KEY env variable."

        try:
            from PIL import Image as PILImage
            from google.genai.types import GenerateContentConfig, Part, Tool, GoogleSearch

            # ── Read image bytes ──
            image_bytes = self._read_image_bytes(image_file)
            if image_bytes is None:
                return None, "Cannot read image file"

            # Open with PIL for logging
            img = PILImage.open(BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            logger.info("Image loaded (%dx%d)", img.size[0], img.size[1])

            # Detect mime type
            mime_type = "image/jpeg"
            if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                mime_type = "image/png"
            elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
                mime_type = "image/webp"

            # ═══════════════════════════════════════════════════════
            #  STEP 1: Analyze Image -> Identify plant + disease
            # ═══════════════════════════════════════════════════════
            logger.info("Step 1: Analyzing image for plant identification and disease detection...")
            
            image_part = Part.from_bytes(data=image_bytes, mime_type=mime_type)
            
            # Get localized prompt
            analysis_prompt = get_image_analysis_prompt(lang)
            
            step1_result = None
            last_error = None
            
            for model_name in self._model_names:
                try:
                    logger.info("Trying model: %s with language: %s", model_name, lang)
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=[analysis_prompt, image_part],
                        config=GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=2048,
                        ),
                    )

                    if response and response.text:
                        step1_result = self._parse_json(response.text)
                        if step1_result:
                            logger.info(
                                "Step 1 success with %s: plant=%s, disease=%s",
                                model_name,
                                step1_result.get('plant_info', {}).get('common_name', '?'),
                                step1_result.get('disease_name', '?'),
                            )
                            break
                        else:
                            last_error = "Failed to parse step 1 response"
                    else:
                        last_error = "Empty response"
                        
                except Exception as e:
                    error_str = str(e)
                    last_error = error_str
                    if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                        logger.warning("Rate limited on %s, trying key rotation...", model_name)
                        if self._rotate_key():
                            logger.info("Rotated to new API key, retrying...")
                            import time
                            time.sleep(1)
                            continue
                        else:
                            import time
                            time.sleep(2)
                            continue
                    logger.warning("Error with %s: %s", model_name, error_str)
                    continue

            if not step1_result:
                # If we failed due to rate limits on all keys, give clear message
                if '429' in str(last_error) or 'RESOURCE_EXHAUSTED' in str(last_error):
                    return None, "Rate limit reached on all API keys. Please wait 1-2 minutes."
                return None, "Image analysis failed. Last error: {}".format(last_error)

            # ═══════════════════════════════════════════════════════
            #  STEP 2: Search Internet for Disease Info & Cures
            #  Uses Google Search Grounding — Gemini searches the web!
            # ═══════════════════════════════════════════════════════
            plant_name = step1_result.get('plant_info', {}).get('common_name', 'Unknown plant')
            disease_name = step1_result.get('disease_name', 'Unknown')
            symptoms = step1_result.get('symptoms_observed', [])
            is_healthy = step1_result.get('is_healthy', False) or disease_name.lower() in ('healthy', 'none', '')

            if not is_healthy and disease_name.lower() not in ('healthy', 'unknown', 'none', ''):
                logger.info("Step 2: Searching internet for '%s' on '%s' (lang=%s)...", disease_name, plant_name, lang)
                
                search_prompt = get_disease_search_prompt(plant_name, disease_name, symptoms, lang)
                
                step2_result = None
                for model_name in self._model_names:
                    try:
                        # Use Google Search grounding!
                        search_tool = Tool(google_search=GoogleSearch())
                        response = self._client.models.generate_content(
                            model=model_name,
                            contents=search_prompt,
                            config=GenerateContentConfig(
                                temperature=0.3,
                                max_output_tokens=4096,
                                tools=[search_tool],
                            ),
                        )

                        if response and response.text:
                            step2_result = self._parse_json(response.text)
                            if step2_result:
                                logger.info("Step 2 success with %s (internet search): got treatments and cures", model_name)
                                break

                        # Fallback: try without grounding if model doesn't support it
                        response = self._client.models.generate_content(
                            model=model_name,
                            contents=search_prompt,
                            config=GenerateContentConfig(
                                temperature=0.3,
                                max_output_tokens=4096,
                            ),
                        )
                        if response and response.text:
                            step2_result = self._parse_json(response.text)
                            if step2_result:
                                logger.info("Step 2 success with %s (no grounding fallback)", model_name)
                                break

                    except Exception as e:
                        error_str = str(e)
                        if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                            import time
                            time.sleep(2)
                            continue
                        logger.warning("Step 2 error with %s: %s", model_name, error_str)
                        continue

                # Merge step 2 results into step 1
                if step2_result:
                    for key in ['description', 'causes', 'immediate_actions', 'treatment',
                                'prevention', 'watering_advice', 'recovery_timeline', 'risk_if_untreated']:
                        if key in step2_result and step2_result[key]:
                            step1_result[key] = step2_result[key]
                else:
                    logger.warning("Step 2 failed - using basic info from step 1 only")
                    step1_result = self._fill_defaults(step1_result, plant_name, disease_name)
            else:
                # Plant is healthy
                logger.info("Plant appears healthy, skipping disease search")
                step1_result = self._fill_healthy_defaults(step1_result, plant_name)

            # Final validation
            step1_result = self._validate_result(step1_result)
            return step1_result, "Analysis completed successfully"

        except Exception as e:
            logger.error("Gemini analysis error: %s", e, exc_info=True)
            return None, "AI analysis error: {}".format(str(e))

    def _read_image_bytes(self, image_file):
        """Read image bytes from various file-like sources."""
        try:
            if isinstance(image_file, bytes):
                return image_file
            elif isinstance(image_file, str):
                with open(image_file, 'rb') as f:
                    return f.read()
            elif hasattr(image_file, 'stream'):
                image_file.stream.seek(0)
                data = image_file.stream.read()
                image_file.stream.seek(0)
                return data
            elif hasattr(image_file, 'read'):
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
                data = image_file.read()
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
                return data
        except Exception as e:
            logger.error("Error reading image: %s", e)
        return None

    def _parse_json(self, text):
        """Parse JSON from Gemini response text."""
        try:
            cleaned = text.strip()
            # Remove markdown wrappers
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            # Try direct parse
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass

            # Try regex extraction
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

            # Try to find the largest valid JSON object
            brace_count = 0
            start = None
            for i, ch in enumerate(cleaned):
                if ch == '{':
                    if brace_count == 0:
                        start = i
                    brace_count += 1
                elif ch == '}':
                    brace_count -= 1
                    if brace_count == 0 and start is not None:
                        try:
                            return json.loads(cleaned[start:i+1])
                        except json.JSONDecodeError:
                            start = None

            logger.warning("Could not parse JSON from: %s", text[:200])
            return None

        except Exception as e:
            logger.warning("JSON parse error: %s", e)
            return None

    def _fill_defaults(self, result, plant_name, disease_name):
        """Fill in default treatment data when internet search fails."""
        if not result.get('description'):
            result['description'] = "{} detected on {}. This condition requires attention.".format(disease_name, plant_name)
        if not result.get('causes'):
            result['causes'] = ["{} is commonly caused by environmental stress or pathogens".format(disease_name)]
        if not result.get('immediate_actions'):
            result['immediate_actions'] = [
                'Isolate the affected plant from healthy plants',
                'Remove heavily affected leaves and dispose of them',
                'Improve air circulation around the plant',
            ]
        if not result.get('treatment'):
            result['treatment'] = {
                'organic': ['Apply neem oil spray (2 tsp per liter water, every 7 days)'],
                'chemical': ['Consult your local garden center for specific fungicide/pesticide'],
                'cultural': ['Ensure proper watering - avoid wetting leaves', 'Improve drainage'],
            }
        if not result.get('prevention'):
            result['prevention'] = ['Regular monitoring', 'Proper spacing between plants', 'Good hygiene']
        if not result.get('watering_advice'):
            result['watering_advice'] = {
                'frequency': 'Water when top inch of soil is dry',
                'method': 'Water at the base, avoid wetting leaves',
                'amount': 'Until water drains from bottom',
            }
        if not result.get('recovery_timeline'):
            result['recovery_timeline'] = {
                'first_improvement': '1-2 weeks with proper treatment',
                'significant_recovery': '3-4 weeks',
                'full_recovery': '6-8 weeks',
            }
        if not result.get('risk_if_untreated'):
            result['risk_if_untreated'] = 'The condition may spread and worsen, potentially killing the plant.'
        return result

    def _fill_healthy_defaults(self, result, plant_name):
        """Fill defaults for a healthy plant."""
        result.setdefault('description', 'This {} appears to be in good health with no visible signs of disease.'.format(plant_name))
        result.setdefault('causes', [])
        result.setdefault('immediate_actions', [
            'Continue current care routine',
            'Monitor for any changes in leaf color or texture',
            'Maintain consistent watering schedule',
        ])
        result.setdefault('treatment', {
            'organic': ['No treatment needed - plant is healthy'],
            'chemical': ['No chemical treatment required'],
            'cultural': ['Continue good cultural practices'],
        })
        result.setdefault('prevention', [
            'Regular inspection of leaves and stems',
            'Proper watering and fertilizing schedule',
            'Good air circulation',
        ])
        result.setdefault('watering_advice', {
            'frequency': 'Follow regular schedule for this plant',
            'method': 'Water at soil level',
            'amount': 'Standard amount for the species',
        })
        result.setdefault('recovery_timeline', {
            'first_improvement': 'N/A - Plant is healthy',
            'significant_recovery': 'N/A',
            'full_recovery': 'N/A',
        })
        result.setdefault('risk_if_untreated', 'No risk - plant is currently healthy.')
        return result

    def _validate_result(self, result):
        """Validate and clean the final result dict."""
        # Ensure all required top-level fields
        result.setdefault('plant_info', {})
        result.setdefault('is_healthy', False)
        result.setdefault('disease_name', 'Unknown')
        result.setdefault('disease_type', 'unknown')
        result.setdefault('confidence', 50)
        result.setdefault('severity', 'moderate')
        result.setdefault('health_score', 50)
        result.setdefault('symptoms_observed', [])
        result.setdefault('description', '')
        result.setdefault('causes', [])
        result.setdefault('immediate_actions', [])
        result.setdefault('treatment', {})
        result.setdefault('prevention', [])
        result.setdefault('watering_advice', {})
        result.setdefault('recovery_timeline', {})
        result.setdefault('risk_if_untreated', '')

        # Ensure description is a string
        if isinstance(result.get('description'), dict):
            result['description'] = json.dumps(result['description'])

        # Normalize confidence to 0-100
        conf = result.get('confidence', 50)
        if isinstance(conf, (int, float)):
            if conf <= 1.0:
                conf = conf * 100
            result['confidence'] = min(100, max(0, conf))

        # Ensure plant_info has all sub-fields
        pi = result['plant_info']
        pi.setdefault('common_name', 'Unknown Plant')
        pi.setdefault('scientific_name', '')
        pi.setdefault('family', '')
        pi.setdefault('plant_type', '')
        pi.setdefault('origin', '')
        pi.setdefault('description', '')
        pi.setdefault('ideal_conditions', {})
        pi.setdefault('general_care', {})

        return result


# ── Singleton ──────────────────────────────────────────────
_gemini_instance = None


def get_gemini_analyzer():
    """Get or create Gemini analyzer singleton."""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiAnalyzer()
    return _gemini_instance
