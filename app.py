"""
Resume Generator Application Entry Point.

This module initializes and configures the Flask application with:
- Centralized configuration management
- CORS support
- API routes with error handlers
- Swagger/OpenAPI documentation

Requirements: 5.1
"""

import logging
from typing import NoReturn

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from src.api.routes import register_routes
from src.api.swagger import init_swagger
from src.config import get_config
from src.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application.
    
    This factory function creates a new Flask application instance
    with all necessary configuration, middleware, routes, and
    documentation set up.
    
    Returns:
        Flask: The configured Flask application instance.
        
    Raises:
        ConfigurationError: If required configuration is missing or invalid.
    """
    # Load configuration from environment
    config = get_config()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure CORS
    CORS(
        app,
        resources={
            r"/*": {
                "origins": config.app.allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )
    
    # Register API routes and error handlers
    register_routes(app)
    
    # Initialize Swagger/OpenAPI documentation
    init_swagger(app)
    
    logger.info(
        f"Application initialized: debug={config.app.debug}, "
        f"port={config.app.port}, "
        f"database={'MongoDB' if config.database.use_mongodb else 'SQLite'}"
    )
    
    return app


# Create the application instance
app = create_app()


def main() -> NoReturn:
    """Run the Flask development server.
    
    This function starts the Flask development server using
    configuration from environment variables.
    
    Note: This should only be used for development. In production,
    use a WSGI server like Gunicorn or uWSGI.
    """
    config = get_config()
    
    logger.info(f"Starting server on port {config.app.port}, debug={config.app.debug}")
    
    app.run(
        host="0.0.0.0",
        port=config.app.port,
        debug=config.app.debug
    )


if __name__ == "__main__":
    main()
