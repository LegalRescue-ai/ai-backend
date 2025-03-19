import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv  # type: ignore
from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore
import openai  # type: ignore
from flask_session import Session

# Configure base path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([
    BASE_DIR,
    os.path.join(BASE_DIR, 'app'),
    os.path.join(BASE_DIR, 'app/services'),
    os.path.join(BASE_DIR, 'app/utils')
])


def configure_logging(app):
    logs_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )

    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)

    app.logger.setLevel(log_level)


def validate_environment():
    load_dotenv()

    required_vars = ['SECRET_KEY', 'OPENAI_API_KEY', 'FLASK_ENV', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ ERROR: Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)


def create_app(config_object=None):
    validate_environment()

    app = Flask(__name__)

    from app.config.settings import Config
    app.config.from_object(config_object or Config)

    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    configure_logging(app)

    CORS(app, resources={r"/api/*": 
    {"origins":[ 
    "http://localhost:5173",
    "http://localhost:3000"
    ]
    }}, supports_credentials=True)

    try:
        openai.api_key = os.getenv('OPENAI_API_KEY')
        app.config['OPENAI_CLIENT'] = openai
        app.logger.info("✅ OpenAI API initialized successfully")
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize OpenAI API: {str(e)}")
        sys.exit(1)
        
    # Add Supabase initialization
    try:
        from supabase import create_client, Client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        supabase_client:Client = create_client(supabase_url, supabase_key)
        app.config['SUPABASE_CLIENT'] = supabase_client
        app.logger.info("✅ Supabase client initialized successfully")
    except Exception as e:
        app.logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
        sys.exit(1)

    try:
        from app.api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        app.logger.info("✅ API routes registered successfully")
    except Exception as e:
        app.logger.error(f"❌ Failed to register API routes: {str(e)}")
        sys.exit(1)

    @app.route('/')
    def health_check():
        return {
            "status": "healthy",
            "service": "Legal Case Management System",
            "version": "1.0.0"
        }

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f"❌ Not Found: {error}")
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"❌ Internal Server Error: {error}")
        return {'error': 'Internal Server Error'}, 500

    app.logger.info("✅ Flask app created successfully")
    globals()['supabase_client'] = supabase_client

    return app


# ✅ Make sure `app` is defined at the module level
app = create_app()


def run_app():
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))

    app.logger.info(f"🚀 Starting Legal Case Management System")
    app.logger.info(f"🌍 Host: {host} | 🔢 Port: {port}")
    app.logger.info(f"🌱 Environment: {app.config.get('ENV', 'development')}")
    app.logger.info(f"🐞 Debug Mode: {app.config.get('DEBUG', False)}")

    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))


if __name__ == '__main__':
    run_app()