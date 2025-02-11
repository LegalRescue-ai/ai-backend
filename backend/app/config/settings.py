import os
from datetime import timedelta

class Config:
    """
    Base configuration class for the Legal Case Management System
    Provides a centralized configuration management
    """
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-ultra-secret-key-that-no-one-can-guess')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'legal_case_system.log')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Security Configurations
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
    REMEMBER_COOKIE_SECURE = os.getenv('REMEMBER_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate Limiting
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    
    # AI Processing Configurations
    MAX_SUMMARY_LENGTH = int(os.getenv('MAX_SUMMARY_LENGTH', 5000))
    PII_REMOVAL_ENABLED = os.getenv('PII_REMOVAL_ENABLED', 'True') == 'True'
    
    # Prediction Confidence Thresholds
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv('LOW_CONFIDENCE_THRESHOLD', 0.3))
    MEDIUM_CONFIDENCE_THRESHOLD = float(os.getenv('MEDIUM_CONFIDENCE_THRESHOLD', 0.6))
    HIGH_CONFIDENCE_THRESHOLD = float(os.getenv('HIGH_CONFIDENCE_THRESHOLD', 0.8))
    
    # Timeout Configurations
    OPENAI_REQUEST_TIMEOUT = int(os.getenv('OPENAI_REQUEST_TIMEOUT', 30))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Allowed File Upload Types
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
        'doc', 'docx', 'xls', 'xlsx'
    }
    
    # Case Categories Configuration Path
    CATEGORIES_CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'categories'
    )
    
    # Retry Configuration for External Services
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 1))
    
    @classmethod
    def is_production(cls):
        """Check if the application is running in production mode"""
        return cls.ENV == 'production'
    
    @classmethod
    def get_openai_config(cls):
        """Retrieve OpenAI configuration"""
        return {
            'api_key': cls.OPENAI_API_KEY,
            'model': cls.OPENAI_MODEL,
            'timeout': cls.OPENAI_REQUEST_TIMEOUT
        }

class DevelopmentConfig(Config):
    """Development-specific configurations"""
    DEBUG = True
    ENV = 'development'

class TestingConfig(Config):
    """Testing-specific configurations"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'

class ProductionConfig(Config):
    """Production-specific configurations"""
    DEBUG = False
    ENV = 'production'
    
    # Stricter security for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# Configuration Factory
def get_config(config_name=None):
    """
    Configuration factory to return the appropriate configuration
    
    Args:
        config_name (str, optional): Name of the configuration. Defaults to None.
    
    Returns:
        Config: Configuration class
    """
    config_mapping = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    # Default to development if no config specified
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    
    return config_mapping.get(config_name, DevelopmentConfig)