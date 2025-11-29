"""
MongoDB implementation of repository interfaces.

This module provides MongoDB-backed implementations of the ResumeRepository
and PDFCacheRepository interfaces for cloud database storage.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.exceptions import DatabaseError, ResumeNotFoundError
from src.models.resume import Resume
from src.repositories.base import PDFCacheRepository, ResumeRepository


class MongoDBResumeRepository(ResumeRepository):
    """MongoDB implementation of ResumeRepository.
    
    Stores resume data in a MongoDB collection with native document storage.
    
    Attributes:
        client: PyMongo client instance.
        db: MongoDB database instance.
        collection: MongoDB collection for resumes.
    """
    
    def __init__(self, connection_url: str, database: str = "Resume"):
        """Initialize the MongoDB repository.
        
        Args:
            connection_url: MongoDB connection URL.
            database: Name of the database to use.
            
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            import pymongo
            from bson.objectid import ObjectId
            
            self._ObjectId = ObjectId
            self.client = pymongo.MongoClient(connection_url)
            self.db = self.client[database]
            self.collection = self.db["Resume"]
        except Exception as e:
            raise DatabaseError(str(e), operation="connect")

    def get_all(self) -> List[Resume]:
        """Retrieve all resumes."""
        try:
            results = []
            for doc in self.collection.find():
                doc["_id"] = str(doc["_id"])
                results.append(Resume.from_dict(doc))
            return results
        except Exception as e:
            raise DatabaseError(str(e), operation="query")
    
    def get_by_id(self, id: str) -> Optional[Resume]:
        """Retrieve a resume by its ID."""
        try:
            document_id = self._ObjectId(id)
            doc = self.collection.find_one({"_id": document_id})
            if doc:
                doc["_id"] = str(doc["_id"])
                return Resume.from_dict(doc)
            return None
        except Exception as e:
            raise DatabaseError(str(e), operation="query")
    
    def get_by_name(self, name: str) -> Optional[Resume]:
        """Retrieve a resume by user name (basic_info.name)."""
        try:
            cursor = self.collection.find({"basic_info.name": name})
            docs = list(cursor)
            if docs:
                doc = docs[0]
                doc["_id"] = str(doc["_id"])
                return Resume.from_dict(doc)
            raise ResumeNotFoundError(name)
        except ResumeNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(str(e), operation="query")
    
    def get_by_resume_name(self, name: str) -> Optional[Resume]:
        """Retrieve a resume by resume name."""
        try:
            cursor = self.collection.find({"name": name})
            docs = list(cursor)
            if docs:
                doc = docs[0]
                doc["_id"] = str(doc["_id"])
                return Resume.from_dict(doc)
            raise ResumeNotFoundError(name)
        except ResumeNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(str(e), operation="query")

    def create(self, resume: Resume) -> str:
        """Create a new resume."""
        try:
            result = self.collection.insert_one(resume.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseError(str(e), operation="insert")
    
    def update(self, id: str, resume: Resume) -> bool:
        """Update an existing resume."""
        try:
            document_id = self._ObjectId(id)
            result = self.collection.update_one(
                {"_id": document_id},
                {"$set": resume.to_dict()}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(str(e), operation="update")
    
    def delete(self, id: str) -> bool:
        """Delete a resume by ID."""
        try:
            document_id = self._ObjectId(id)
            result = self.collection.delete_one({"_id": document_id})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseError(str(e), operation="delete")


class MongoDBPDFCacheRepository(PDFCacheRepository):
    """MongoDB implementation of PDFCacheRepository.
    
    Stores PDF cache entries in a MongoDB collection for tracking
    generated PDFs and avoiding redundant LaTeX compilation.
    
    Attributes:
        client: PyMongo client instance.
        db: MongoDB database instance.
        collection: MongoDB collection for PDF cache.
    """
    
    def __init__(self, connection_url: str, database: str = "Resume"):
        """Initialize the MongoDB PDF cache repository.
        
        Args:
            connection_url: MongoDB connection URL.
            database: Name of the database to use.
            
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            import pymongo
            
            self.client = pymongo.MongoClient(connection_url)
            self.db = self.client[database]
            self.collection = self.db["pdf_cache"]
        except Exception as e:
            raise DatabaseError(str(e), operation="connect")

    def get(self, resume_id: str, template: str, order: str, content_hash: str) -> Optional[str]:
        """Get cached PDF path if exists and hash matches."""
        try:
            cache_doc = self.collection.find_one({
                "resume_id": str(resume_id),
                "template": template,
                "section_order": order
            })
            if cache_doc and cache_doc.get("content_hash") == content_hash:
                return cache_doc.get("file_path")
            return None
        except Exception as e:
            raise DatabaseError(str(e), operation="query")
    
    def set(self, resume_id: str, template: str, order: str, content_hash: str, file_path: str) -> None:
        """Store or update cache entry for a generated PDF."""
        try:
            self.collection.update_one(
                {
                    "resume_id": str(resume_id),
                    "template": template,
                    "section_order": order
                },
                {"$set": {
                    "content_hash": content_hash,
                    "file_path": file_path,
                    "created_at": datetime.utcnow()
                }},
                upsert=True
            )
        except Exception as e:
            raise DatabaseError(str(e), operation="insert")
    
    def clear(self, resume_id: Optional[str] = None) -> None:
        """Clear cache entries."""
        try:
            if resume_id:
                self.collection.delete_many({"resume_id": str(resume_id)})
            else:
                self.collection.delete_many({})
        except Exception as e:
            raise DatabaseError(str(e), operation="delete")


__all__ = [
    "MongoDBResumeRepository",
    "MongoDBPDFCacheRepository",
]
