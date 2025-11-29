"""
Abstract base classes for repository pattern implementation.

This module defines the interfaces that all repository implementations
must follow, enabling database backend abstraction and testability.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.models.resume import Resume


class ResumeRepository(ABC):
    """Abstract base class for resume data access.
    
    All resume repository implementations (SQLite, MongoDB, etc.) must
    implement this interface to ensure consistent behavior across backends.
    """
    
    @abstractmethod
    def get_all(self) -> List["Resume"]:
        """Retrieve all resumes.
        
        Returns:
            List of Resume objects.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional["Resume"]:
        """Retrieve a resume by its ID.
        
        Args:
            id: The unique identifier of the resume.
            
        Returns:
            Resume object if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def get_by_name(self, name: str) -> Optional["Resume"]:
        """Retrieve a resume by user name (basic_info.name).
        
        Args:
            name: The user's name from basic_info.
            
        Returns:
            Resume object if found, None otherwise.
            
        Raises:
            ResumeNotFoundError: If no resume matches the name.
        """
        pass

    @abstractmethod
    def get_by_resume_name(self, name: str) -> Optional["Resume"]:
        """Retrieve a resume by resume name.
        
        Args:
            name: The resume's name field.
            
        Returns:
            Resume object if found, None otherwise.
            
        Raises:
            ResumeNotFoundError: If no resume matches the name.
        """
        pass
    
    @abstractmethod
    def create(self, resume: "Resume") -> str:
        """Create a new resume.
        
        Args:
            resume: Resume object to create.
            
        Returns:
            The ID of the newly created resume.
            
        Raises:
            DatabaseError: If the creation fails.
        """
        pass
    
    @abstractmethod
    def update(self, id: str, resume: "Resume") -> bool:
        """Update an existing resume.
        
        Args:
            id: The unique identifier of the resume to update.
            resume: Updated Resume object.
            
        Returns:
            True if the resume was updated, False if not found.
            
        Raises:
            DatabaseError: If the update fails.
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a resume by ID.
        
        Args:
            id: The unique identifier of the resume to delete.
            
        Returns:
            True if the resume was deleted, False if not found.
            
        Raises:
            DatabaseError: If the deletion fails.
        """
        pass


class PDFCacheRepository(ABC):
    """Abstract base class for PDF cache data access.
    
    All PDF cache repository implementations must implement this interface
    to provide consistent caching behavior across database backends.
    """
    
    @abstractmethod
    def get(self, resume_id: str, template: str, order: str, content_hash: str) -> Optional[str]:
        """Get cached PDF path if exists and hash matches.
        
        Args:
            resume_id: The ID of the resume.
            template: The template name used for generation.
            order: The section order string.
            content_hash: Hash of the resume content for cache validation.
            
        Returns:
            File path to cached PDF if cache hit, None if miss or hash mismatch.
        """
        pass
    
    @abstractmethod
    def set(self, resume_id: str, template: str, order: str, content_hash: str, file_path: str) -> None:
        """Store or update cache entry for a generated PDF.
        
        Args:
            resume_id: The ID of the resume.
            template: The template name used for generation.
            order: The section order string.
            content_hash: Hash of the resume content.
            file_path: Path to the generated PDF file.
            
        Raises:
            DatabaseError: If the cache operation fails.
        """
        pass
    
    @abstractmethod
    def clear(self, resume_id: Optional[str] = None) -> None:
        """Clear cache entries.
        
        Args:
            resume_id: If provided, clear only that resume's cache.
                      If None, clear all cache entries.
                      
        Raises:
            DatabaseError: If the clear operation fails.
        """
        pass


__all__ = [
    "ResumeRepository",
    "PDFCacheRepository",
]
