"""
Authentication routes for Smart Plant Health Assistant.
Handles user login, logout, and session validation endpoints.
JWT-based authentication with database persistence.
"""

from flask import Blueprint, request, jsonify, g
from auth import get_auth_manager, login_required, decode_token

# Create blueprint
auth_routes = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Get auth manager
auth_mgr = get_auth_manager()


def get_limiter():
    """Get rate limiter if available."""
    try:
        from app import limiter
        return limiter
    except (ImportError, AttributeError):
        return None


@auth_routes.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request JSON:
        email (str): User email
        password (str): User password
        name (str): Display name
        language (str, optional): Preferred language (en, hi, mr)
    
    Response:
        success (bool): Registration success
        message (str): Response message
        token (str): JWT token if successful
        user (dict): User info if successful
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', data.get('username', '')).strip()
        language = data.get('language', 'en').strip()
        
        # Validate required fields
        if not email or not password or not name:
            return jsonify({
                'success': False,
                'message': 'Email, password, and name are required'
            }), 400
        
        # Attempt registration
        success, message, auth_data = auth_mgr.register_user(email, password, name, language)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'token': auth_data['token'],
                'session_id': f"jwt_{auth_data['token']}",  # Legacy compatibility
                'user': auth_data['user']
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    
    Request JSON:
        email (str): User email
        password (str): User password
    
    Response:
        success (bool): Login success
        message (str): Response message
        token (str): JWT token if successful
        session_id (str): Legacy session ID (JWT prefixed)
        user (dict): User info if successful
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Attempt login
        success, message, auth_data = auth_mgr.login(email, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'token': auth_data['token'],
                'session_id': f"jwt_{auth_data['token']}",  # Legacy compatibility
                'user': auth_data['user']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/validate', methods=['POST'])
def validate_session():
    """
    Validate JWT token and get user info.
    
    Request JSON:
        session_id (str): Session ID (JWT token with optional prefix)
        token (str): JWT token directly
    
    Response:
        success (bool): Validation result
        message (str): Response message
        user (dict): User info if valid
        is_valid (bool): Token validity
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'is_valid': False,
                'message': 'Request body is required'
            }), 400
        
        # Accept both session_id (legacy) and token
        token = data.get('token', '').strip()
        if not token:
            session_id = data.get('session_id', '').strip()
            if session_id.startswith('jwt_'):
                token = session_id[4:]
            else:
                token = session_id
        
        if not token:
            return jsonify({
                'success': False,
                'is_valid': False,
                'message': 'Token is required'
            }), 400
        
        # Validate token
        is_valid, user_data = auth_mgr.validate_token(token)
        
        if is_valid:
            return jsonify({
                'success': True,
                'is_valid': True,
                'message': 'Token is valid',
                'user': user_data
            }), 200
        else:
            return jsonify({
                'success': True,
                'is_valid': False,
                'message': 'Token is invalid or expired'
            }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'is_valid': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/session-info', methods=['POST'])
def session_info():
    """
    Get detailed session information.
    
    Request JSON:
        session_id (str): Session ID (JWT token)
        token (str): JWT token directly
    
    Response:
        success (bool): Operation success
        message (str): Response message
        session (dict): Session info if valid
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Accept both session_id (legacy) and token
        token = data.get('token', '').strip()
        if not token:
            session_id = data.get('session_id', '').strip()
            if session_id.startswith('jwt_'):
                token = session_id[4:]
            else:
                token = session_id
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        # Validate and get user
        is_valid, user_data = auth_mgr.validate_token(token)
        
        if is_valid:
            return jsonify({
                'success': True,
                'message': 'Session info retrieved',
                'session': {
                    'user': user_data,
                    'is_valid': True
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Session not found or expired'
            }), 401
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (JWT tokens are stateless, so this is mainly for client-side).
    
    Response:
        success (bool): Logout success
        message (str): Response message
    """
    try:
        # JWT is stateless, logout happens client-side by removing token
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current authenticated user info.
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
        success (bool): Operation success
        user (dict): User info
    """
    try:
        user = auth_mgr.get_user(g.user_id)
        if user:
            return jsonify({
                'success': True,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@auth_routes.route('/language', methods=['PUT'])
@login_required
def update_language():
    """
    Update user's preferred language.
    
    Request JSON:
        language (str): Language code (en, hi, mr)
    
    Response:
        success (bool): Operation success
        message (str): Response message
    """
    try:
        data = request.get_json()
        language = data.get('language', 'en').strip()
        
        if language not in ['en', 'hi', 'mr']:
            return jsonify({
                'success': False,
                'message': 'Invalid language. Supported: en, hi, mr'
            }), 400
        
        success = auth_mgr.update_user_language(g.user_id, language)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Language updated'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update language'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
