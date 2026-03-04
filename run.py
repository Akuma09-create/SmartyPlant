"""
run.py - Entry point for the application
Run this file to start the Smart Plant Health Assistant
"""

import os
import sys
from pathlib import Path

# Change to script directory so it works from anywhere
os.chdir(Path(__file__).parent)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# Add backend to path (backend modules use top-level imports)
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app


if __name__ == '__main__':
    # Create Flask app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    
    # Get configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ===========================================================
    |                                                           |
    |    Smart Plant Health Assistant                           |
    |    AI-Powered Plant Disease Detection & Care Advisory     |
    |                                                           |
    |    Starting server...                                     |
    |    URL: http://{host}:{port}                              |
    |                                                           |
    |    Press CTRL+C to stop                                   |
    |                                                           |
    ===========================================================
    """)
    
    # Run Flask app
    app.run(host=host, port=port, debug=debug)
