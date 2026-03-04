"""
Configuration module for Smart Plant Health Assistant.
Centralized configuration for all environments and settings.
NO hardcoded secrets - all sensitive data from environment variables.
"""

import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Base configuration - shared across all environments."""
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    BACKEND_DIR = PROJECT_ROOT / 'backend'
    FRONTEND_DIR = PROJECT_ROOT / 'frontend'
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # File upload settings
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', '10'))
    MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        str(PROJECT_ROOT / 'uploads')
    )
    
    # Database settings
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{PROJECT_ROOT / "plant_health.db"}'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # API settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    API_VERSION = 'v1'
    
    # OpenAI API Configuration (SECURE)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '60'))
    
    # Google Gemini API Configuration (SECURE)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    # Image Processing Configuration
    IMAGE_MIN_SIZE = (100, 100)
    IMAGE_MAX_SIZE = (4096, 4096)
    IMAGE_TARGET_SIZE = (224, 224)
    IMAGE_QUALITY = int(os.getenv('IMAGE_QUALITY', '95'))
    
    # AI Analysis Configuration
    AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '50.0'))
    AI_HEALTH_CRITICAL = float(os.getenv('AI_HEALTH_CRITICAL', '20.0'))
    AI_HEALTH_POOR = float(os.getenv('AI_HEALTH_POOR', '40.0'))
    MAX_PREDICTIONS = 5
    
    # Model settings (kept for backwards compatibility)
    CONFIDENCE_THRESHOLD = 0.7
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.getenv('SESSION_LIFETIME', '604800'))  # 7 days
    )
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Authentication Configuration
    AUTH_ENABLED = os.getenv('AUTH_ENABLED', 'True').lower() == 'true'
    GUEST_MODE_ENABLED = os.getenv('GUEST_MODE_ENABLED', 'True').lower() == 'true'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(PROJECT_ROOT / 'app.log'))
    
    # Rate Limiting (optional)
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'False').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Language Support
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES = ['en', 'hi', 'mr']
    
    # Email Configuration (Flask-Mail)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@plantcare.local')
    
    # Push Notifications (Web Push / VAPID)
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')
    VAPID_CLAIMS_EMAIL = os.getenv('VAPID_CLAIMS_EMAIL', 'mailto:admin@plantcare.local')
    
    # Scheduler Settings
    SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'True').lower() == 'true'
    REMINDER_CHECK_INTERVAL_MINUTES = int(os.getenv('REMINDER_CHECK_INTERVAL', '60'))
    
    # Reports directory
    REPORTS_FOLDER = os.getenv(
        'REPORTS_FOLDER',
        str(PROJECT_ROOT / 'reports')
    )
    
    @classmethod
    def validate_required_keys(cls):
        """
        Validate that all required configuration is present.
        
        Raises:
            ValueError: If required configuration is missing
        """
        # At least one AI API key is required (Gemini OR OpenAI)
        if not cls.GEMINI_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError(
                "Missing required AI API key. Please set GEMINI_API_KEY (or GOOGLE_API_KEY) "
                "or OPENAI_API_KEY in your .env file or environment."
            )
    
    @classmethod
    def init_directories(cls):
        """Create required directories if they don't exist."""
        # Create upload folder
        Path(cls.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
        
        # Create log directory
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self):
        """
        Convert configuration to dictionary (excluding secrets).
        Safe for logging and debugging.
        """
        return {
            'DEBUG': self.DEBUG,
            'TESTING': self.TESTING,
            'DATABASE_URL': self.DATABASE_URL if 'sqlite' in self.DATABASE_URL else '***',
            'OPENAI_MODEL': self.OPENAI_MODEL,
            'MAX_UPLOAD_SIZE_MB': self.MAX_UPLOAD_SIZE_MB,
            'AUTH_ENABLED': self.AUTH_ENABLED,
            'GUEST_MODE_ENABLED': self.GUEST_MODE_ENABLED,
            'AI_CONFIDENCE_THRESHOLD': self.AI_CONFIDENCE_THRESHOLD,
            'SESSION_LIFETIME_DAYS': self.PERMANENT_SESSION_LIFETIME.days
        }



class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    
    @classmethod
    def validate_production_secrets(cls):
        """
        Validate that production has secure secrets.
        Called during app startup in production mode.
        """
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key == 'dev-secret-key-change-in-production':
            raise ValueError(
                "CRITICAL: Production requires a secure SECRET_KEY. "
                "Set a strong random SECRET_KEY environment variable. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        if len(secret_key) < 32:
            raise ValueError(
                "SECRET_KEY is too short. Use at least 32 characters for production."
            )


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)
