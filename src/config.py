"""
Centralized configuration module for the Resume Generator application.

This module provides type-safe access to application configuration through
dataclasses. Configuration values are loaded from environment variables with
sensible defaults.

Usage:
    from src.config import get_config
    
    config = get_config()
    print(config.app.port)
    print(config.database.use_mongodb)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import os

from src.exceptions import ConfigurationError


# Legacy constant for backwards compatibility
KEYWORDS: List[str] = []


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration settings.
    
    Attributes:
        use_mongodb: Whether to use MongoDB instead of SQLite.
        sqlite_path: Path to the SQLite database file.
        mongodb_url: MongoDB connection URL (required if use_mongodb is True).
        mongodb_database: Name of the MongoDB database to use.
    """
    use_mongodb: bool
    sqlite_path: Path
    mongodb_url: Optional[str]
    mongodb_database: str = "Resume"


@dataclass(frozen=True)
class AppConfig:
    """Application configuration settings.
    
    Attributes:
        debug: Whether to run in debug mode.
        port: Port number for the Flask server.
        allowed_origins: List of allowed CORS origins.
        latex_timeout: Timeout in seconds for LaTeX compilation.
        output_dir: Directory for generated PDF output.
    """
    debug: bool
    port: int
    allowed_origins: List[str]
    latex_timeout: int
    output_dir: Path


@dataclass(frozen=True)
class Config:
    """Main configuration container.
    
    Attributes:
        database: Database-related configuration.
        app: Application-related configuration.
    """
    database: DatabaseConfig
    app: AppConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.
        
        Environment Variables:
            DATABASE_URL: MongoDB connection URL (if set, MongoDB is used)
            SQLITE_PATH: Path to SQLite database (default: "resumes.db")
            MONGODB_DATABASE: MongoDB database name (default: "Resume")
            FLASK_DEBUG: Enable debug mode (default: "false")
            PORT: Server port (default: 8000)
            ALLOWED_ORIGINS: Comma-separated CORS origins (default: "*")
            LATEX_TIMEOUT: LaTeX compilation timeout in seconds (default: 60)
            OUTPUT_DIR: Output directory for PDFs (default: "output")
        
        Returns:
            Config: Populated configuration instance.
            
        Raises:
            ConfigurationError: If a required configuration is missing or invalid.
        """
        db_url = os.environ.get("DATABASE_URL", "").strip()
        
        # Parse port with validation
        port_str = os.environ.get("PORT", "8000")
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ConfigurationError(
                    f"Port must be between 1 and 65535, got {port}",
                    config_key="PORT"
                )
        except ValueError:
            raise ConfigurationError(
                f"Invalid port value: '{port_str}' is not a valid integer",
                config_key="PORT"
            )
        
        # Parse latex_timeout with validation
        timeout_str = os.environ.get("LATEX_TIMEOUT", "60")
        try:
            latex_timeout = int(timeout_str)
            if latex_timeout < 1:
                raise ConfigurationError(
                    f"LaTeX timeout must be positive, got {latex_timeout}",
                    config_key="LATEX_TIMEOUT"
                )
        except ValueError:
            raise ConfigurationError(
                f"Invalid timeout value: '{timeout_str}' is not a valid integer",
                config_key="LATEX_TIMEOUT"
            )
        
        # Parse allowed origins
        origins_str = os.environ.get("ALLOWED_ORIGINS", "*")
        allowed_origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
        if not allowed_origins:
            allowed_origins = ["*"]
        
        database = DatabaseConfig(
            use_mongodb=bool(db_url),
            sqlite_path=Path(os.environ.get("SQLITE_PATH", "resumes.db")),
            mongodb_url=db_url if db_url else None,
            mongodb_database=os.environ.get("MONGODB_DATABASE", "Resume"),
        )
        
        app = AppConfig(
            debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
            port=port,
            allowed_origins=allowed_origins,
            latex_timeout=latex_timeout,
            output_dir=Path(os.environ.get("OUTPUT_DIR", "output")),
        )
        
        return cls(database=database, app=app)


# Global config instance (lazily initialized)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance.
    
    The configuration is lazily loaded on first access and cached
    for subsequent calls.
    
    Returns:
        Config: The global configuration instance.
        
    Raises:
        ConfigurationError: If configuration loading fails.
    """
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance.
    
    This is primarily useful for testing to force configuration
    to be reloaded from environment variables.
    """
    global _config
    _config = None


__all__ = [
    "DatabaseConfig",
    "AppConfig", 
    "Config",
    "get_config",
    "reset_config",
    "KEYWORDS",
]
