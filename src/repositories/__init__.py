"""
Repository pattern implementations for database operations.

This module provides repository interfaces and implementations for
abstracting database operations in the Resume Generator application.

The factory functions automatically select the appropriate implementation
based on the application configuration.

Usage:
    from src.repositories import get_resume_repository, get_cache_repository
    
    resume_repo = get_resume_repository()
    cache_repo = get_cache_repository()
"""

from typing import Optional

from src.config import get_config
from src.repositories.base import PDFCacheRepository, ResumeRepository

# Cached repository instances
_resume_repository: Optional[ResumeRepository] = None
_cache_repository: Optional[PDFCacheRepository] = None


def get_resume_repository() -> ResumeRepository:
    """Get the resume repository instance based on configuration.
    
    The repository type is determined by the DATABASE_URL environment
    variable. If set and non-empty, MongoDB is used; otherwise SQLite.
    
    Returns:
        ResumeRepository: The appropriate repository implementation.
        
    Raises:
        DatabaseError: If repository initialization fails.
    """
    global _resume_repository
    
    if _resume_repository is None:
        config = get_config()
        
        if config.database.use_mongodb:
            from src.repositories.mongodb import MongoDBResumeRepository
            _resume_repository = MongoDBResumeRepository(
                connection_url=config.database.mongodb_url,  # type: ignore
                database=config.database.mongodb_database
            )
        else:
            from src.repositories.sqlite import SQLiteResumeRepository
            _resume_repository = SQLiteResumeRepository(
                db_path=config.database.sqlite_path
            )
    
    return _resume_repository


def get_cache_repository() -> PDFCacheRepository:
    """Get the PDF cache repository instance based on configuration.
    
    The repository type is determined by the DATABASE_URL environment
    variable. If set and non-empty, MongoDB is used; otherwise SQLite.
    
    Returns:
        PDFCacheRepository: The appropriate repository implementation.
        
    Raises:
        DatabaseError: If repository initialization fails.
    """
    global _cache_repository
    
    if _cache_repository is None:
        config = get_config()
        
        if config.database.use_mongodb:
            from src.repositories.mongodb import MongoDBPDFCacheRepository
            _cache_repository = MongoDBPDFCacheRepository(
                connection_url=config.database.mongodb_url,  # type: ignore
                database=config.database.mongodb_database
            )
        else:
            from src.repositories.sqlite import SQLitePDFCacheRepository
            _cache_repository = SQLitePDFCacheRepository(
                db_path=config.database.sqlite_path
            )
    
    return _cache_repository


def reset_repositories() -> None:
    """Reset the cached repository instances.
    
    This is primarily useful for testing to force repositories
    to be recreated with new configuration.
    """
    global _resume_repository, _cache_repository
    _resume_repository = None
    _cache_repository = None


__all__ = [
    "ResumeRepository",
    "PDFCacheRepository",
    "get_resume_repository",
    "get_cache_repository",
    "reset_repositories",
]
