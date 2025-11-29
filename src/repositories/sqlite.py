"""
SQLite implementation of repository interfaces.

This module provides SQLite-backed implementations of the ResumeRepository
and PDFCacheRepository interfaces for local database storage.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.exceptions import DatabaseError, ResumeNotFoundError
from src.models.resume import Resume
from src.repositories.base import PDFCacheRepository, ResumeRepository


class SQLiteResumeRepository(ResumeRepository):
    """SQLite implementation of ResumeRepository.
    
    Stores resume data in a SQLite database with JSON serialization
    for the resume content.
    
    Attributes:
        db_path: Path to the SQLite database file.
    """
    
    def __init__(self, db_path: Path):
        """Initialize the SQLite repository.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection with row factory configured."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self) -> None:
        """Ensure required tables exist in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    data TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_name ON resumes(name)
            """)
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="create_tables")
        finally:
            conn.close()
    
    def get_all(self) -> List[Resume]:
        """Retrieve all resumes."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, data FROM resumes")
            results = []
            for row in cursor.fetchall():
                data = json.loads(row["data"])
                data["_id"] = str(row["id"])
                results.append(Resume.from_dict(data))
            return results
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="query")
        finally:
            conn.close()
    
    def get_by_id(self, id: str) -> Optional[Resume]:
        """Retrieve a resume by its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, data FROM resumes WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row["data"])
                data["_id"] = str(row["id"])
                return Resume.from_dict(data)
            return None
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="query")
        finally:
            conn.close()
    
    def get_by_name(self, name: str) -> Optional[Resume]:
        """Retrieve a resume by user name (basic_info.name)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, data FROM resumes")
            for row in cursor.fetchall():
                data = json.loads(row["data"])
                if data.get("basic_info", {}).get("name") == name:
                    data["_id"] = str(row["id"])
                    return Resume.from_dict(data)
            raise ResumeNotFoundError(name)
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="query")
        finally:
            conn.close()

    def get_by_resume_name(self, name: str) -> Optional[Resume]:
        """Retrieve a resume by resume name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, data FROM resumes WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row["data"])
                data["_id"] = str(row["id"])
                return Resume.from_dict(data)
            raise ResumeNotFoundError(name)
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="query")
        finally:
            conn.close()
    
    def create(self, resume: Resume) -> str:
        """Create a new resume."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            resume_dict = resume.to_dict()
            name = resume_dict.get("name")
            data = json.dumps(resume_dict)
            cursor.execute(
                "INSERT INTO resumes (name, data) VALUES (?, ?)",
                (name, data)
            )
            conn.commit()
            return str(cursor.lastrowid)
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="insert")
        finally:
            conn.close()
    
    def update(self, id: str, resume: Resume) -> bool:
        """Update an existing resume."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            resume_dict = resume.to_dict()
            name = resume_dict.get("name")
            data = json.dumps(resume_dict)
            cursor.execute(
                "UPDATE resumes SET name = ?, data = ? WHERE id = ?",
                (name, data, id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="update")
        finally:
            conn.close()
    
    def delete(self, id: str) -> bool:
        """Delete a resume by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM resumes WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="delete")
        finally:
            conn.close()


class SQLitePDFCacheRepository(PDFCacheRepository):
    """SQLite implementation of PDFCacheRepository.
    
    Stores PDF cache entries in a SQLite database for tracking
    generated PDFs and avoiding redundant LaTeX compilation.
    
    Attributes:
        db_path: Path to the SQLite database file.
    """
    
    def __init__(self, db_path: Path):
        """Initialize the SQLite PDF cache repository.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection with row factory configured."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self) -> None:
        """Ensure required tables exist in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdf_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id TEXT NOT NULL,
                    template TEXT NOT NULL,
                    section_order TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(resume_id, template, section_order)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_lookup 
                ON pdf_cache(resume_id, template, section_order)
            """)
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="create_tables")
        finally:
            conn.close()

    def get(self, resume_id: str, template: str, order: str, content_hash: str) -> Optional[str]:
        """Get cached PDF path if exists and hash matches."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT content_hash, file_path FROM pdf_cache 
                WHERE resume_id = ? AND template = ? AND section_order = ?
            """, (str(resume_id), template, order))
            row = cursor.fetchone()
            if row and row["content_hash"] == content_hash:
                return row["file_path"]
            return None
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="query")
        finally:
            conn.close()
    
    def set(self, resume_id: str, template: str, order: str, content_hash: str, file_path: str) -> None:
        """Store or update cache entry for a generated PDF."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO pdf_cache (resume_id, template, section_order, content_hash, file_path)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(resume_id, template, section_order) 
                DO UPDATE SET content_hash = ?, file_path = ?, created_at = CURRENT_TIMESTAMP
            """, (str(resume_id), template, order, content_hash, file_path, content_hash, file_path))
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="insert")
        finally:
            conn.close()
    
    def clear(self, resume_id: Optional[str] = None) -> None:
        """Clear cache entries."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if resume_id:
                cursor.execute("DELETE FROM pdf_cache WHERE resume_id = ?", (str(resume_id),))
            else:
                cursor.execute("DELETE FROM pdf_cache")
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(str(e), operation="delete")
        finally:
            conn.close()


__all__ = [
    "SQLiteResumeRepository",
    "SQLitePDFCacheRepository",
]
