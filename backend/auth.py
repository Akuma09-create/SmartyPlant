"""
Authentication module for Smart Plant Health Assistant.
Database-backed user management with JWT tokens.
"""

import os
import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app, g


def get_secret_key():
    """Get the JWT secret key from config or environment."""
    return os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def validate_password_strength(password: str) -> Optional[str]:
    """
    Validate password meets security requirements.
    
    Returns:
        None if valid, error message string if invalid
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number"
    
    # Check for special characters
    special_chars = "!@#$%^&*(),.?\":{}|<>-_=+[]\\/'`~"
    if not any(c in special_chars for c in password):
        return "Password must contain at least one special character (!@#$%^&* etc.)"
    
    return None  # Password is valid


def generate_token(user_id: int, email: str, is_guest: bool = False, expires_days: int = 7) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'email': email,
        'is_guest': is_guest,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=expires_days)
    }
    return jwt.encode(payload, get_secret_key(), algorithm='HS256')


def decode_token(token: str) -> Optional[Dict]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request() -> Optional[str]:
    """Extract JWT token from request headers or cookies."""
    # Check Authorization header (Bearer token)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Check X-Session-ID header (legacy support)
    session_id = request.headers.get('X-Session-ID', '')
    if session_id.startswith('jwt_'):
        return session_id[4:]
    
    # Check cookies
    return request.cookies.get('auth_token')


def login_required(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Store user info in g for access in route
        g.user_id = payload.get('user_id')
        g.user_email = payload.get('email')
        g.is_guest = payload.get('is_guest', False)
        
        return f(*args, **kwargs)
    return decorated_function


def login_optional(f):
    """Decorator for routes where auth is optional but provides context if present."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        g.user_id = None
        g.user_email = None
        g.is_guest = True
        
        if token:
            payload = decode_token(token)
            if payload:
                g.user_id = payload.get('user_id')
                g.user_email = payload.get('email')
                g.is_guest = payload.get('is_guest', False)
        
        return f(*args, **kwargs)
    return decorated_function


class AuthenticationManager:
    """
    Database-backed authentication manager.
    Uses bcrypt for password hashing and JWT for tokens.
    """
    
    def __init__(self, db=None):
        """Initialize authentication manager with database."""
        self.db = db
        self._User = None
    
    @property
    def User(self):
        """Lazy import User model to avoid circular imports."""
        if self._User is None:
            from models.database_models import User
            self._User = User
        return self._User
    
    def set_db(self, db):
        """Set database instance."""
        self.db = db
    
    def register_user(self, email: str, password: str, name: str, language: str = 'en') -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user.
        
        Returns:
            Tuple of (success, message, user_data)
        """
        # Validate input
        if not email or not password or not name:
            return False, "All fields are required", None
        
        if "@" not in email or "." not in email.split("@")[-1]:
            return False, "Invalid email format", None
        
        # Strong password validation
        password_error = validate_password_strength(password)
        if password_error:
            return False, password_error, None
        
        try:
            # Check if user exists
            existing = self.User.query.filter_by(email=email.lower()).first()
            if existing:
                return False, "Email already registered", None
            
            # Create user
            user = self.User(
                email=email.lower(),
                password_hash=hash_password(password),
                name=name,
                language=language
            )
            self.db.session.add(user)
            self.db.session.commit()
            
            # Generate token
            token = generate_token(user.id, user.email)
            
            return True, "User registered successfully", {
                'token': token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user and return token.
        
        Returns:
            Tuple of (success, message, auth_data)
        """
        if not email or not password:
            return False, "Email and password are required", None
        
        try:
            user = self.User.query.filter_by(email=email.lower(), is_active=True).first()
            
            if not user:
                return False, "Invalid email or password", None
            
            if not verify_password(password, user.password_hash):
                return False, "Invalid email or password", None
            
            # Generate token
            token = generate_token(user.id, user.email)
            
            return True, "Login successful", {
                'token': token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
    
    def login_guest(self) -> Tuple[bool, str, Dict]:
        """
        Create a guest user session.
        
        Returns:
            Tuple of (success, message, auth_data)
        """
        try:
            # Create guest user
            guest_id = f"guest_{uuid.uuid4().hex[:8]}"
            guest_email = f"{guest_id}@guest.local"
            
            user = self.User(
                email=guest_email,
                password_hash=hash_password(uuid.uuid4().hex),
                name=f"Guest_{uuid.uuid4().hex[:6]}",
                is_guest=True
            )
            self.db.session.add(user)
            self.db.session.commit()
            
            # Generate token
            token = generate_token(user.id, user.email, is_guest=True, expires_days=1)
            
            return True, "Guest session created", {
                'token': token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            self.db.session.rollback()
            return False, f"Guest login failed: {str(e)}", None
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate token and return user info.
        
        Returns:
            Tuple of (is_valid, user_data)
        """
        payload = decode_token(token)
        if not payload:
            return False, None
        
        try:
            user = self.User.query.get(payload.get('user_id'))
            if not user or not user.is_active:
                return False, None
            
            return True, user.to_dict()
            
        except Exception:
            return False, None
    
    def get_user(self, user_id: int):
        """Get user by ID."""
        try:
            return self.User.query.get(user_id)
        except Exception:
            return None
    
    def update_user_language(self, user_id: int, language: str) -> bool:
        """Update user's preferred language."""
        try:
            user = self.User.query.get(user_id)
            if user:
                user.language = language
                self.db.session.commit()
                return True
            return False
        except Exception:
            self.db.session.rollback()
            return False
    
    def update_push_subscription(self, user_id: int, subscription: str) -> bool:
        """Update user's push notification subscription."""
        try:
            user = self.User.query.get(user_id)
            if user:
                user.push_subscription = subscription
                self.db.session.commit()
                return True
            return False
        except Exception:
            self.db.session.rollback()
            return False
    
    def get_all_demo_credentials(self) -> list:
        """Get demo credentials for testing."""
        return [
            ("demo@example.com", "demo123"),
            ("test@example.com", "test123"),
        ]
    
    def create_demo_users(self):
        """Create demo users if they don't exist."""
        demo_users = [
            ("demo@example.com", "demo123", "Demo User"),
            ("test@example.com", "test123", "Test User"),
        ]
        
        for email, password, name in demo_users:
            existing = self.User.query.filter_by(email=email).first()
            if not existing:
                try:
                    user = self.User(
                        email=email,
                        password_hash=hash_password(password),
                        name=name
                    )
                    self.db.session.add(user)
                    self.db.session.commit()
                except Exception:
                    self.db.session.rollback()


# Global authentication manager instance
auth_manager = AuthenticationManager()


def get_auth_manager() -> AuthenticationManager:
    """Get the global authentication manager instance."""
    return auth_manager


def init_auth(db):
    """Initialize auth manager with database."""
    auth_manager.set_db(db)
    return auth_manager
