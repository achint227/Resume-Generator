"""
Shared pytest fixtures for the Resume Generator test suite.
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_basic_info() -> Dict[str, Any]:
    """Sample basic info data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "address": "123 Main St, City, State 12345",
        "summary": "Experienced software developer",
        "github": "johndoe",
        "linkedin": "johndoe",
        "homepage": "https://johndoe.dev",
    }


@pytest.fixture
def sample_education() -> Dict[str, Any]:
    """Sample education data for testing."""
    return {
        "university": "State University",
        "degree": "Bachelor of Science in Computer Science",
        "location": "City, State",
        "duration": "2018 - 2022",
        "info": ["GPA: 3.8", "Dean's List"],
    }


@pytest.fixture
def sample_experience() -> Dict[str, Any]:
    """Sample experience data for testing."""
    return {
        "company": "Tech Corp",
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "duration": "2022 - Present",
        "projects": [
            {
                "title": "API Development",
                "tools": ["Python", "Flask", "PostgreSQL"],
                "details": ["Built RESTful APIs", "Improved performance by 50%"],
            }
        ],
    }


@pytest.fixture
def sample_project() -> Dict[str, Any]:
    """Sample project data for testing."""
    return {
        "title": "Resume Generator",
        "description": ["A tool to generate PDF resumes from structured data"],
        "tools": ["Python", "LaTeX", "Flask"],
        "repo": "https://github.com/johndoe/resume-generator",
    }


@pytest.fixture
def sample_resume_data(
    sample_basic_info: Dict[str, Any],
    sample_education: Dict[str, Any],
    sample_experience: Dict[str, Any],
    sample_project: Dict[str, Any],
) -> Dict[str, Any]:
    """Complete sample resume data for testing."""
    return {
        "name": "test_resume",
        "basic_info": sample_basic_info,
        "education": [sample_education],
        "experiences": [sample_experience],
        "projects": [sample_project],
        "keywords": ["Python", "Flask", "API"],
    }


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Provide a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Provide a temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Fixture that provides a clean environment for config testing."""
    original_env = os.environ.copy()
    # Clear relevant environment variables
    env_vars_to_clear = [
        "DATABASE_URL",
        "SQLITE_PATH",
        "MONGODB_DATABASE",
        "FLASK_DEBUG",
        "PORT",
        "ALLOWED_ORIGINS",
        "LATEX_TIMEOUT",
        "OUTPUT_DIR",
    ]
    for var in env_vars_to_clear:
        os.environ.pop(var, None)
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
