"""
Chat routes for AI-powered plant care assistant.
"""

from flask import Blueprint, request, jsonify, g
from auth import login_required, login_optional
from services.chat_service import chat_service

# Create blueprint
chat_routes = Blueprint('chat', __name__, url_prefix='/api/v1/chat')


@chat_routes.route('', methods=['POST'])
@login_optional
def send_message():
    """
    Send a message to the chat assistant.
    
    Request JSON:
        message (str): User's message
        language (str, optional): Response language (en, hi, mr)
        analysis_id (int, optional): Related analysis ID for context
    
    Response:
        success (bool): Operation success
        response (str): Assistant's response
        error (str, optional): Error message if failed
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        language = data.get('language', 'en')
        analysis_id = data.get('analysis_id')
        
        # Get analysis context if provided
        analysis_context = None
        if analysis_id:
            try:
                from models.database_models import PlantAnalysis
                analysis = PlantAnalysis.query.get(analysis_id)
                if analysis and analysis.user_id == g.user_id:
                    analysis_context = analysis.to_dict()
            except:
                pass
        
        # Get user's plants for context
        plants_context = None
        if g.user_id:
            try:
                from models.database_models import Plant
                plants = Plant.query.filter_by(user_id=g.user_id).limit(5).all()
                plants_context = [p.to_dict() for p in plants]
            except:
                pass
        
        # Get chat response
        result = chat_service.chat(
            user_id=g.user_id,  # Can be None for guests
            message=message,
            language=language,
            analysis_context=analysis_context,
            plants_context=plants_context
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Chat failed'),
                'response': result.get('response', '')
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@chat_routes.route('/history', methods=['GET'])
@login_required
def get_history():
    """
    Get chat history for current user.
    
    Query params:
        limit (int, optional): Maximum messages to return (default 50)
    
    Response:
        success (bool): Operation success
        messages (list): List of chat messages
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        messages = chat_service.get_chat_history(g.user_id, limit)
        
        return jsonify({
            'success': True,
            'messages': messages
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@chat_routes.route('/history', methods=['DELETE'])
@login_required
def clear_history():
    """
    Clear chat history for current user.
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        success = chat_service.clear_history(g.user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Chat history cleared'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear chat history'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@chat_routes.route('/suggestions', methods=['GET'])
@login_optional
def get_suggestions():
    """
    Get quick suggestion chips for chat.
    
    Query params:
        language (str, optional): Language code (en, hi, mr)
    
    Response:
        success (bool): Operation success
        suggestions (list): List of suggestion strings
    """
    try:
        language = request.args.get('language', 'en')
        suggestions = chat_service.get_quick_suggestions(language)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
