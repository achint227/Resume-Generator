"""
Property-based tests for repository pattern implementation.

**Feature: codebase-refactor, Property 1: Repository Interface Conformance**

Tests that all repository implementations provide all methods defined in the
ResumeRepository and PDFCacheRepository interfaces with matching signatures.

**Feature: codebase-refactor, Property 2: Repository Selection Based on Configuration**

Tests that repository selection is based on DATABASE_URL environment variable:
MongoDB when set and non-empty, SQLite otherwise.
"""

import inspect
import os
from pathlib import Path
from typing import get_type_hints

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from src.config import reset_config
from src.repositories import (
    get_resume_repository,
    get_cache_repository,
    reset_repositories,
    ResumeRepository,
    PDFCacheRepository,
)
from src.repositories.base import ResumeRepository as BaseResumeRepository
from src.repositories.base import PDFCacheRepository as BasePDFCacheRepository
from src.repositories.sqlite import SQLiteResumeRepository, SQLitePDFCacheRepository


class TestRepositoryInterfaceConformance:
    """
    **Feature: codebase-refactor, Property 1: Repository Interface Conformance**
    **Validates: Requirements 1.1**
    
    Property: For any repository implementation (SQLite or MongoDB), the
    implementation SHALL provide all methods defined in the ResumeRepository
    interface with matching signatures and return types.
    """

    def _get_abstract_methods(self, cls):
        """Get all abstract methods from a class."""
        methods = {}
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                methods[name] = method
        return methods

    def _get_method_signature(self, method):
        """Get the signature of a method."""
        return inspect.signature(method)

    @given(st.just(SQLiteResumeRepository))
    @settings(max_examples=100)
    def test_sqlite_resume_repository_implements_all_abstract_methods(self, repo_class):
        """SQLiteResumeRepository implements all abstract methods from ResumeRepository."""
        abstract_methods = self._get_abstract_methods(BaseResumeRepository)
        
        for method_name in abstract_methods:
            # Check method exists
            assert hasattr(repo_class, method_name), \
                f"SQLiteResumeRepository missing method: {method_name}"
            
            impl_method = getattr(repo_class, method_name)
            
            # Check it's not abstract (i.e., it's implemented)
            assert not getattr(impl_method, '__isabstractmethod__', False), \
                f"Method {method_name} is still abstract in SQLiteResumeRepository"

    @given(st.just(SQLitePDFCacheRepository))
    @settings(max_examples=100)
    def test_sqlite_cache_repository_implements_all_abstract_methods(self, repo_class):
        """SQLitePDFCacheRepository implements all abstract methods from PDFCacheRepository."""
        abstract_methods = self._get_abstract_methods(BasePDFCacheRepository)
        
        for method_name in abstract_methods:
            # Check method exists
            assert hasattr(repo_class, method_name), \
                f"SQLitePDFCacheRepository missing method: {method_name}"
            
            impl_method = getattr(repo_class, method_name)
            
            # Check it's not abstract (i.e., it's implemented)
            assert not getattr(impl_method, '__isabstractmethod__', False), \
                f"Method {method_name} is still abstract in SQLitePDFCacheRepository"


    @given(st.just(True))
    @settings(max_examples=100)
    def test_sqlite_resume_repository_method_signatures_match_interface(self, _):
        """SQLiteResumeRepository method signatures match ResumeRepository interface."""
        abstract_methods = self._get_abstract_methods(BaseResumeRepository)
        
        for method_name, abstract_method in abstract_methods.items():
            impl_method = getattr(SQLiteResumeRepository, method_name)
            
            abstract_sig = self._get_method_signature(abstract_method)
            impl_sig = self._get_method_signature(impl_method)
            
            # Compare parameter names (excluding 'self')
            abstract_params = list(abstract_sig.parameters.keys())
            impl_params = list(impl_sig.parameters.keys())
            
            assert abstract_params == impl_params, \
                f"Method {method_name} signature mismatch: expected {abstract_params}, got {impl_params}"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_sqlite_cache_repository_method_signatures_match_interface(self, _):
        """SQLitePDFCacheRepository method signatures match PDFCacheRepository interface."""
        abstract_methods = self._get_abstract_methods(BasePDFCacheRepository)
        
        for method_name, abstract_method in abstract_methods.items():
            impl_method = getattr(SQLitePDFCacheRepository, method_name)
            
            abstract_sig = self._get_method_signature(abstract_method)
            impl_sig = self._get_method_signature(impl_method)
            
            # Compare parameter names (excluding 'self')
            abstract_params = list(abstract_sig.parameters.keys())
            impl_params = list(impl_sig.parameters.keys())
            
            assert abstract_params == impl_params, \
                f"Method {method_name} signature mismatch: expected {abstract_params}, got {impl_params}"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_resume_repository_has_required_crud_methods(self, _):
        """ResumeRepository interface defines all required CRUD methods."""
        required_methods = ['get_all', 'get_by_id', 'get_by_name', 'get_by_resume_name', 'create', 'update', 'delete']
        abstract_methods = self._get_abstract_methods(BaseResumeRepository)
        
        for method_name in required_methods:
            assert method_name in abstract_methods, \
                f"ResumeRepository missing required method: {method_name}"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_cache_repository_has_required_methods(self, _):
        """PDFCacheRepository interface defines all required cache methods."""
        required_methods = ['get', 'set', 'clear']
        abstract_methods = self._get_abstract_methods(BasePDFCacheRepository)
        
        for method_name in required_methods:
            assert method_name in abstract_methods, \
                f"PDFCacheRepository missing required method: {method_name}"


    @given(st.just(True))
    @settings(max_examples=100)
    def test_mongodb_resume_repository_implements_all_abstract_methods(self, _):
        """MongoDBResumeRepository implements all abstract methods from ResumeRepository."""
        from src.repositories.mongodb import MongoDBResumeRepository
        
        abstract_methods = self._get_abstract_methods(BaseResumeRepository)
        
        for method_name in abstract_methods:
            # Check method exists
            assert hasattr(MongoDBResumeRepository, method_name), \
                f"MongoDBResumeRepository missing method: {method_name}"
            
            impl_method = getattr(MongoDBResumeRepository, method_name)
            
            # Check it's not abstract (i.e., it's implemented)
            assert not getattr(impl_method, '__isabstractmethod__', False), \
                f"Method {method_name} is still abstract in MongoDBResumeRepository"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_mongodb_cache_repository_implements_all_abstract_methods(self, _):
        """MongoDBPDFCacheRepository implements all abstract methods from PDFCacheRepository."""
        from src.repositories.mongodb import MongoDBPDFCacheRepository
        
        abstract_methods = self._get_abstract_methods(BasePDFCacheRepository)
        
        for method_name in abstract_methods:
            # Check method exists
            assert hasattr(MongoDBPDFCacheRepository, method_name), \
                f"MongoDBPDFCacheRepository missing method: {method_name}"
            
            impl_method = getattr(MongoDBPDFCacheRepository, method_name)
            
            # Check it's not abstract (i.e., it's implemented)
            assert not getattr(impl_method, '__isabstractmethod__', False), \
                f"Method {method_name} is still abstract in MongoDBPDFCacheRepository"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_mongodb_resume_repository_method_signatures_match_interface(self, _):
        """MongoDBResumeRepository method signatures match ResumeRepository interface."""
        from src.repositories.mongodb import MongoDBResumeRepository
        
        abstract_methods = self._get_abstract_methods(BaseResumeRepository)
        
        for method_name, abstract_method in abstract_methods.items():
            impl_method = getattr(MongoDBResumeRepository, method_name)
            
            abstract_sig = self._get_method_signature(abstract_method)
            impl_sig = self._get_method_signature(impl_method)
            
            # Compare parameter names (excluding 'self')
            abstract_params = list(abstract_sig.parameters.keys())
            impl_params = list(impl_sig.parameters.keys())
            
            assert abstract_params == impl_params, \
                f"Method {method_name} signature mismatch: expected {abstract_params}, got {impl_params}"

    @given(st.just(True))
    @settings(max_examples=100)
    def test_mongodb_cache_repository_method_signatures_match_interface(self, _):
        """MongoDBPDFCacheRepository method signatures match PDFCacheRepository interface."""
        from src.repositories.mongodb import MongoDBPDFCacheRepository
        
        abstract_methods = self._get_abstract_methods(BasePDFCacheRepository)
        
        for method_name, abstract_method in abstract_methods.items():
            impl_method = getattr(MongoDBPDFCacheRepository, method_name)
            
            abstract_sig = self._get_method_signature(abstract_method)
            impl_sig = self._get_method_signature(impl_method)
            
            # Compare parameter names (excluding 'self')
            abstract_params = list(abstract_sig.parameters.keys())
            impl_params = list(impl_sig.parameters.keys())
            
            assert abstract_params == impl_params, \
                f"Method {method_name} signature mismatch: expected {abstract_params}, got {impl_params}"



class TestRepositorySelectionBasedOnConfiguration:
    """
    **Feature: codebase-refactor, Property 2: Repository Selection Based on Configuration**
    **Validates: Requirements 1.4**
    
    Property: For any database configuration, when DATABASE_URL is set and non-empty,
    the system SHALL instantiate a MongoDB repository; otherwise, the system SHALL
    instantiate a SQLite repository.
    """

    @given(st.just(True))
    @settings(max_examples=100)
    def test_sqlite_repository_selected_when_database_url_not_set(self, _):
        """SQLite repository is selected when DATABASE_URL is not set."""
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            # Remove DATABASE_URL to ensure SQLite mode
            os.environ.pop("DATABASE_URL", None)
            
            resume_repo = get_resume_repository()
            cache_repo = get_cache_repository()
            
            # Verify SQLite implementations are returned
            assert isinstance(resume_repo, SQLiteResumeRepository), \
                f"Expected SQLiteResumeRepository, got {type(resume_repo).__name__}"
            assert isinstance(cache_repo, SQLitePDFCacheRepository), \
                f"Expected SQLitePDFCacheRepository, got {type(cache_repo).__name__}"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()

    @given(st.just(True))
    @settings(max_examples=100)
    def test_sqlite_repository_selected_when_database_url_empty(self, _):
        """SQLite repository is selected when DATABASE_URL is empty string."""
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            # Set DATABASE_URL to empty string
            os.environ["DATABASE_URL"] = ""
            
            resume_repo = get_resume_repository()
            cache_repo = get_cache_repository()
            
            # Verify SQLite implementations are returned
            assert isinstance(resume_repo, SQLiteResumeRepository), \
                f"Expected SQLiteResumeRepository, got {type(resume_repo).__name__}"
            assert isinstance(cache_repo, SQLitePDFCacheRepository), \
                f"Expected SQLitePDFCacheRepository, got {type(cache_repo).__name__}"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()

    @given(
        whitespace=st.sampled_from([" ", "  ", "\t", "\n", "\r", "   ", " \t ", "\n\r"])
    )
    @settings(max_examples=100)
    def test_sqlite_repository_selected_when_database_url_whitespace(self, whitespace: str):
        """SQLite repository is selected when DATABASE_URL is only whitespace."""
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            # Set DATABASE_URL to whitespace only
            os.environ["DATABASE_URL"] = whitespace
            
            resume_repo = get_resume_repository()
            cache_repo = get_cache_repository()
            
            # Verify SQLite implementations are returned
            assert isinstance(resume_repo, SQLiteResumeRepository), \
                f"Expected SQLiteResumeRepository, got {type(resume_repo).__name__}"
            assert isinstance(cache_repo, SQLitePDFCacheRepository), \
                f"Expected SQLitePDFCacheRepository, got {type(cache_repo).__name__}"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()


    @given(
        mongodb_url=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters=":/.-_@")
        )
    )
    @settings(max_examples=100)
    def test_mongodb_repository_selected_when_database_url_set(self, mongodb_url: str):
        """MongoDB repository is selected when DATABASE_URL is set and non-empty."""
        assume(mongodb_url.strip())  # Must be non-empty after stripping
        
        from src.repositories.mongodb import MongoDBResumeRepository, MongoDBPDFCacheRepository
        
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            # Set DATABASE_URL to a non-empty value
            os.environ["DATABASE_URL"] = mongodb_url
            
            # Note: We can't actually connect to MongoDB in tests, so we verify
            # the configuration logic by checking use_mongodb flag
            from src.config import Config
            config = Config.from_env()
            
            assert config.database.use_mongodb is True, \
                "use_mongodb should be True when DATABASE_URL is set"
            assert config.database.mongodb_url == mongodb_url, \
                "mongodb_url should match DATABASE_URL"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()

    @given(st.just(True))
    @settings(max_examples=100)
    def test_repository_returns_same_instance_on_repeated_calls(self, _):
        """Repository factory returns the same instance on repeated calls."""
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            os.environ.pop("DATABASE_URL", None)
            
            resume_repo1 = get_resume_repository()
            resume_repo2 = get_resume_repository()
            cache_repo1 = get_cache_repository()
            cache_repo2 = get_cache_repository()
            
            # Same instance should be returned
            assert resume_repo1 is resume_repo2, \
                "get_resume_repository should return the same instance"
            assert cache_repo1 is cache_repo2, \
                "get_cache_repository should return the same instance"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()

    @given(st.just(True))
    @settings(max_examples=100)
    def test_reset_repositories_clears_cached_instances(self, _):
        """reset_repositories clears cached repository instances."""
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            os.environ.pop("DATABASE_URL", None)
            
            resume_repo1 = get_resume_repository()
            cache_repo1 = get_cache_repository()
            
            reset_repositories()
            
            resume_repo2 = get_resume_repository()
            cache_repo2 = get_cache_repository()
            
            # New instances should be created after reset
            assert resume_repo1 is not resume_repo2, \
                "New resume repository instance should be created after reset"
            assert cache_repo1 is not cache_repo2, \
                "New cache repository instance should be created after reset"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()

    @given(
        sqlite_filename=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters="_-")
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sqlite_repository_uses_configured_path(self, sqlite_filename: str, tmp_path):
        """SQLite repository uses the path from configuration."""
        assume(sqlite_filename.strip())
        # Avoid Windows reserved device names
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                         'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
        assume(sqlite_filename.upper() not in reserved_names)
        assume(not sqlite_filename.upper().startswith(tuple(f"{n}." for n in reserved_names)))
        
        sqlite_path = str(tmp_path / f"{sqlite_filename}.db")
        
        original_env = os.environ.copy()
        reset_config()
        reset_repositories()
        
        try:
            os.environ.pop("DATABASE_URL", None)
            os.environ["SQLITE_PATH"] = sqlite_path
            
            resume_repo = get_resume_repository()
            
            assert isinstance(resume_repo, SQLiteResumeRepository)
            assert resume_repo.db_path == Path(sqlite_path), \
                f"Expected db_path={sqlite_path}, got {resume_repo.db_path}"
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
            reset_repositories()
