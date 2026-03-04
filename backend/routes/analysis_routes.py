"""Plant analysis routes - Main API endpoints."""

from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.utils import secure_filename
import os
import json
from services import PlantAnalyzer, CareAdvisor
from services.gemini_analyzer import get_gemini_analyzer
from services.perenual_api import get_perenual_api
from utils.validators import validate_file_upload, validate_image_file
from auth import login_required
from models.database_models import db, Plant, PlantAnalysis
from routes.plant_routes import create_plant_care_reminders

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/v1')

# Initialize services
plant_analyzer = PlantAnalyzer()
care_advisor = CareAdvisor()


@analysis_bp.route('/analyze', methods=['POST'])
def analyze_plant():
    """
    Analyze plant image for disease detection.
    Uses Gemini AI for real disease detection when available,
    falls back to rule-based analysis otherwise.
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Validate file
        validation = validate_file_upload(file)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # Validate image
        image_validation = validate_image_file(file)
        if not image_validation['valid']:
            return jsonify({
                'success': False,
                'error': image_validation['error']
            }), 400
        
        # Read file bytes into memory so multiple readers can use it
        file.seek(0)
        from io import BytesIO
        file_bytes = file.read()
        file.seek(0)
        
        # Get user's preferred language (from header, form data, or query param)
        lang = (request.headers.get('Accept-Language', 'en')[:2] or 
                request.form.get('lang', '') or 
                request.args.get('lang', 'en'))
        # Validate language code
        if lang not in ['en', 'hi', 'mr']:
            lang = 'en'
        current_app.logger.info(f"Analysis requested with language: {lang}")
        
        # Try Gemini AI analysis first (real disease detection)
        gemini = get_gemini_analyzer()
        current_app.logger.info(f"Gemini available: {gemini.is_available}, API key set: {bool(gemini.api_key)}")
        if gemini.is_available:
            image_io = BytesIO(file_bytes)
            ai_result, ai_message = gemini.analyze_image(image_io, lang=lang)
            current_app.logger.info(f"Gemini result: {ai_message}, got data: {ai_result is not None}")
            
            if ai_result:
                # Extract plant info
                plant_info = ai_result.get('plant_info', {})
                plant_name = plant_info.get('common_name', '') or ai_result.get('plant_type', 'Unknown')
                
                # Enrich with Perenual data (plant details, images, care info)
                perenual = get_perenual_api()
                perenual_data = None
                if perenual.is_available and plant_name and plant_name != 'Unknown':
                    try:
                        perenual_data = perenual.search_and_get_details(plant_name)
                        if perenual_data:
                            current_app.logger.info(f"Perenual enrichment: {perenual_data.get('common_name')}")
                            # Merge Perenual data into plant_info
                            plant_info['perenual_id'] = perenual_data.get('id')
                            plant_info['scientific_name'] = plant_info.get('scientific_name') or perenual_data.get('scientific_name')
                            plant_info['family'] = plant_info.get('family') or perenual_data.get('family')
                            plant_info['cycle'] = perenual_data.get('cycle')
                            plant_info['watering'] = perenual_data.get('watering')
                            plant_info['sunlight'] = perenual_data.get('sunlight')
                            plant_info['sunlight_list'] = perenual_data.get('sunlight_list', [])
                            plant_info['growth_rate'] = perenual_data.get('growth_rate')
                            plant_info['maintenance'] = perenual_data.get('maintenance')
                            plant_info['care_level'] = perenual_data.get('care_level')
                            plant_info['indoor'] = perenual_data.get('indoor')
                            plant_info['hardiness_zone'] = perenual_data.get('hardiness_zone')
                            plant_info['default_image'] = perenual_data.get('default_image')
                            plant_info['images'] = perenual_data.get('images', [])
                            plant_info['poisonous_to_pets'] = perenual_data.get('poisonous_to_pets')
                            plant_info['poisonous_to_humans'] = perenual_data.get('poisonous_to_humans')
                            plant_info['drought_tolerant'] = perenual_data.get('drought_tolerant')
                            plant_info['medicinal'] = perenual_data.get('medicinal')
                    except Exception as e:
                        current_app.logger.warning(f"Perenual enrichment failed: {e}")
                
                response = {
                    'success': True,
                    'analysis_type': 'ai',
                    'plant_info': plant_info,
                    'perenual_data': perenual_data,  # Include full Perenual data separately
                    'analysis': {
                        'success': True,
                        'plant_type': plant_name,
                        'is_healthy': ai_result.get('is_healthy', False),
                        'disease_detection': {
                            'primary_disease': ai_result.get('disease_name', 'Unknown'),
                            'disease_type': ai_result.get('disease_type', 'unknown'),
                            'confidence': ai_result.get('confidence', 50) / 100.0,
                            'severity': ai_result.get('severity', 'moderate'),
                            'description': ai_result.get('description', ''),
                            'common_causes': ai_result.get('causes', []),
                            'health_score': ai_result.get('health_score', 50),
                            'symptoms_observed': ai_result.get('symptoms_observed', []),
                            'risk_if_untreated': ai_result.get('risk_if_untreated', '')
                        },
                        'predictions': [{
                            'disease': ai_result.get('disease_name', 'Unknown'),
                            'confidence': ai_result.get('confidence', 50) / 100.0,
                            'severity': ai_result.get('severity', 'moderate'),
                            'description': ai_result.get('description', ''),
                            'common_causes': ai_result.get('causes', [])
                        }],
                        'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
                    },
                    'care_plan': {
                        'success': True,
                        'disease': ai_result.get('disease_name', 'Unknown'),
                        'severity': ai_result.get('severity', 'moderate'),
                        'confidence': ai_result.get('confidence', 50) / 100.0,
                        'immediate_actions': ai_result.get('immediate_actions', []),
                        'treatment': ai_result.get('treatment', {}),
                        'prevention': ai_result.get('prevention', []),
                        'watering_advice': ai_result.get('watering_advice', {}),
                        'recovery_timeline': ai_result.get('recovery_timeline', {}),
                        'risk_if_untreated': ai_result.get('risk_if_untreated', '')
                    }
                }
                return jsonify(response), 200
            else:
                # If rate limited, tell the user clearly
                if '429' in ai_message or 'Rate limit' in ai_message or 'quota' in ai_message.lower():
                    current_app.logger.warning(f"Gemini rate limited: {ai_message}")
                    return jsonify({
                        'success': False,
                        'error': 'AI analysis rate limit reached. Please wait 1-2 minutes and try again. (Free tier has limited requests per minute/day)'
                    }), 429
                current_app.logger.warning(f"Gemini analysis failed: {ai_message}, falling back to rule-based")
        
        # Fallback: rule-based analysis
        current_app.logger.info("Using fallback rule-based analysis")
        file.seek(0)
        confidence_threshold = request.args.get('confidence_threshold', 0.7, type=float)
        confidence_threshold = max(0.0, min(1.0, confidence_threshold))
        
        analysis_result = plant_analyzer.analyze_plant_image(file, confidence_threshold)
        
        if not analysis_result['success']:
            return jsonify(analysis_result), 400
        
        care_plan = care_advisor.generate_care_plan(analysis_result)
        
        # Determine reason for using rule-based analysis
        ai_unavailable_reason = None
        if not gemini.is_available:
            ai_unavailable_reason = 'AI service not configured (no API key set)'
        else:
            ai_unavailable_reason = 'AI service temporarily unavailable, using local analysis'
        
        response = {
            'success': True,
            'analysis_type': 'rule_based',
            'ai_unavailable_reason': ai_unavailable_reason,
            'analysis': analysis_result,
            'care_plan': care_plan
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Analysis error: {str(e)}")
        error_msg = 'An unexpected error occurred during analysis'
        if current_app.debug:
            error_msg = f'Server error: {str(e)}'
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@analysis_bp.route('/analyze/save-to-plants', methods=['POST'])
@login_required
def save_analysis_to_plants():
    """
    Save the most recent analysis result as a plant in My Plants.
    
    Request JSON:
        plant_name (str): Name for the plant
        species (str, optional): Plant species
        location (str, optional): Where the plant is located
        disease_name (str, optional): Detected disease
        confidence (float, optional): Analysis confidence
        health_score (float, optional): Plant health score
        severity (str, optional): Disease severity
        analysis_details (dict, optional): Full analysis details
        care_plan (dict, optional): Full care plan
        image_url (str, optional): Image URL/path
    """
    try:
        user_id = g.user_id
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Request body is required'}), 400
        
        plant_name = data.get('plant_name', '').strip()
        if not plant_name:
            return jsonify({'success': False, 'error': 'Plant name is required'}), 400
        
        # Create the plant
        plant = Plant(
            user_id=user_id,
            name=plant_name,
            species=data.get('species', '').strip() or None,
            location=data.get('location', '').strip() or None,
            image_filename=data.get('image_url') or None,
            notes=data.get('notes', '').strip() or None
        )
        db.session.add(plant)
        db.session.flush()  # Get the plant ID
        
        # Save the analysis linked to this plant
        analysis = PlantAnalysis(
            user_id=user_id,
            plant_id=plant.id,
            image_filename=data.get('image_url') or 'uploaded_image',
            plant_type=data.get('species') or plant_name,
            disease_detected=data.get('disease_name') or None,
            confidence_score=data.get('confidence'),
            health_score=data.get('health_score'),
            severity_level=data.get('severity') or None,
            analysis_details=json.dumps(data.get('analysis_details', {})),
            recommended_actions=json.dumps(data.get('care_plan', {})),
            language=data.get('language', 'en')
        )
        db.session.add(analysis)
        
        # Create automatic care reminders
        reminders_created = create_plant_care_reminders(plant, user_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{plant_name} saved to My Plants with {len(reminders_created)} care reminders!',
            'plant': plant.to_dict(),
            'analysis_id': analysis.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Save to plants error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error saving plant: {str(e)}'
        }), 500


@analysis_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple plant images.
    
    Request:
        - files: Multiple image files
    
    Response:
        - List of analysis results
    """
    try:
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'Empty file list'
            }), 400
        
        # Analyze each file
        results = []
        for file in files:
            # Validate
            validation = validate_file_upload(file)
            if not validation['valid']:
                results.append({
                    'success': False,
                    'filename': file.filename,
                    'error': validation['error']
                })
                continue
            
            file.seek(0)
            
            # Analyze
            analysis = plant_analyzer.analyze_plant_image(file)
            care = care_advisor.generate_care_plan(analysis) if analysis.get('success') else None
            
            results.append({
                'success': analysis.get('success', False),
                'filename': file.filename,
                'analysis': analysis,
                'care_plan': care
            })
        
        return jsonify({
            'success': True,
            'total_images': len(files),
            'successful': len([r for r in results if r['success']]),
            'results': results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Batch analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@analysis_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """
    Get analysis history for a session.
    
    Args:
        session_id: Unique session identifier
    
    Response:
        - List of previous analyses
    """
    try:
        # In production, retrieve from database
        # For now, return empty result
        return jsonify({
            'success': True,
            'session_id': session_id,
            'analyses': [],
            'total': 0
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"History retrieval error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@analysis_bp.route('/diseases', methods=['GET'])
def get_disease_list():
    """Get list of detectable diseases."""
    from models import PlantDiseaseDetector
    
    detector = PlantDiseaseDetector()
    
    diseases = []
    for disease_name, info in detector.DISEASE_DATABASE.items():
        diseases.append({
            'name': disease_name,
            'severity': info.get('severity', 'unknown'),
            'description': info.get('description', ''),
            'common_causes': info.get('common_causes', [])
        })
    
    return jsonify({
        'success': True,
        'total_diseases': len(diseases),
        'diseases': diseases
    }), 200


@analysis_bp.route('/plants/search', methods=['GET'])
def search_plants():
    """
    Search for plants by name using Perenual API.
    
    Query params:
        - q: Plant name to search for (required)
        - page: Page number for pagination (default: 1)
    
    Response:
        - List of matching plants with details
    """
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query (q) is required'
            }), 400
        
        perenual = get_perenual_api()
        if not perenual or not perenual.is_available:
            return jsonify({
                'success': False,
                'error': 'Plant search API not configured. Set PERENUAL_API_KEY.'
            }), 503
        
        results = perenual.search_plants(query, page)
        
        if not results or not isinstance(results, dict):
            return jsonify({
                'success': False,
                'error': 'Search failed. Please try again.'
            }), 500
        
        # Format results
        plants = []
        for plant in results.get('data', []):
            if not isinstance(plant, dict):
                continue
            plants.append({
                'id': plant.get('id'),
                'common_name': plant.get('common_name'),
                'scientific_name': plant.get('scientific_name', [None])[0] if isinstance(plant.get('scientific_name'), list) else plant.get('scientific_name'),
                'cycle': plant.get('cycle'),
                'watering': plant.get('watering'),
                'sunlight': plant.get('sunlight', []),
                'default_image': (plant.get('default_image') or {}).get('medium_url') or (plant.get('default_image') or {}).get('regular_url', '')
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'page': page,
            'total': results.get('total', len(plants)),
            'last_page': results.get('last_page', 1),
            'plants': plants
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Plant search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@analysis_bp.route('/plants/<int:plant_id>', methods=['GET'])
def get_plant_details(plant_id):
    """
    Get detailed information about a specific plant by Perenual ID.
    
    Args:
        plant_id: Perenual plant ID
    
    Response:
        - Detailed plant information
    """
    try:
        perenual = get_perenual_api()
        if not perenual.is_available:
            return jsonify({
                'success': False,
                'error': 'Plant API not configured. Set PERENUAL_API_KEY.'
            }), 503
        
        details = perenual.get_plant_details(plant_id)
        
        if not details:
            return jsonify({
                'success': False,
                'error': f'Plant with ID {plant_id} not found'
            }), 404
        
        # Format the response
        formatted = perenual._format_detailed_info(details)
        
        return jsonify({
            'success': True,
            'plant': formatted
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Plant details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
