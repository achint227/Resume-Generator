"""
Unit tests for data model serialization.

Tests round-trip serialization (to_dict then from_dict) and handling of optional fields.
Requirements: 6.2
"""

import pytest
from typing import Dict, Any

from src.models import (
    BasicInfo,
    Education,
    Experience,
    Project,
    ProjectDetail,
    Resume,
)


class TestBasicInfo:
    """Tests for BasicInfo dataclass."""

    def test_round_trip_serialization(self, sample_basic_info: Dict[str, Any]):
        """Test that to_dict then from_dict preserves data."""
        original = BasicInfo.from_dict(sample_basic_info)
        serialized = original.to_dict()
        restored = BasicInfo.from_dict(serialized)

        assert restored.name == original.name
        assert restored.email == original.email
        assert restored.phone == original.phone
        assert restored.address == original.address
        assert restored.summary == original.summary
        assert restored.github == original.github
        assert restored.linkedin == original.linkedin
        assert restored.homepage == original.homepage

    def test_optional_fields_missing(self):
        """Test handling when optional fields are missing."""
        minimal_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-000-0000",
        }
        info = BasicInfo.from_dict(minimal_data)

        assert info.name == "Jane Doe"
        assert info.email == "jane@example.com"
        assert info.phone == "555-000-0000"
        assert info.address is None
        assert info.summary is None
        assert info.github is None
        assert info.linkedin is None
        assert info.homepage is None

    def test_to_dict_excludes_none_optional_fields(self):
        """Test that to_dict excludes None optional fields."""
        minimal_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-000-0000",
        }
        info = BasicInfo.from_dict(minimal_data)
        result = info.to_dict()

        assert "name" in result
        assert "email" in result
        assert "phone" in result
        assert "address" not in result
        assert "summary" not in result



class TestEducation:
    """Tests for Education dataclass."""

    def test_round_trip_serialization(self, sample_education: Dict[str, Any]):
        """Test that to_dict then from_dict preserves data."""
        original = Education.from_dict(sample_education)
        serialized = original.to_dict()
        restored = Education.from_dict(serialized)

        assert restored.university == original.university
        assert restored.degree == original.degree
        assert restored.location == original.location
        assert restored.duration == original.duration
        assert restored.info == original.info

    def test_empty_info_list(self):
        """Test handling when info list is empty or missing."""
        data = {
            "university": "Test University",
            "degree": "BS",
            "location": "City",
            "duration": "2020-2024",
        }
        edu = Education.from_dict(data)

        assert edu.info == []


class TestProjectDetail:
    """Tests for ProjectDetail dataclass."""

    def test_round_trip_serialization(self):
        """Test that to_dict then from_dict preserves data."""
        data = {
            "title": "API Project",
            "tools": ["Python", "Flask"],
            "details": ["Built APIs", "Improved performance"],
        }
        original = ProjectDetail.from_dict(data)
        serialized = original.to_dict()
        restored = ProjectDetail.from_dict(serialized)

        assert restored.title == original.title
        assert restored.tools == original.tools
        assert restored.details == original.details

    def test_empty_lists(self):
        """Test handling when lists are empty or missing."""
        data = {"title": "Simple Project"}
        detail = ProjectDetail.from_dict(data)

        assert detail.title == "Simple Project"
        assert detail.tools == []
        assert detail.details == []


class TestExperience:
    """Tests for Experience dataclass."""

    def test_round_trip_serialization(self, sample_experience: Dict[str, Any]):
        """Test that to_dict then from_dict preserves data."""
        original = Experience.from_dict(sample_experience)
        serialized = original.to_dict()
        restored = Experience.from_dict(serialized)

        assert restored.company == original.company
        assert restored.title == original.title
        assert restored.location == original.location
        assert restored.duration == original.duration
        assert len(restored.projects) == len(original.projects)
        if restored.projects:
            assert restored.projects[0].title == original.projects[0].title

    def test_nested_projects_serialization(self, sample_experience: Dict[str, Any]):
        """Test that nested ProjectDetail objects are properly serialized."""
        exp = Experience.from_dict(sample_experience)
        serialized = exp.to_dict()

        assert "projects" in serialized
        assert len(serialized["projects"]) == 1
        assert serialized["projects"][0]["title"] == "API Development"
        assert "Python" in serialized["projects"][0]["tools"]

    def test_optional_fields(self):
        """Test handling of optional experience fields."""
        minimal_data = {
            "company": "Test Corp",
            "title": "Developer",
            "location": "Remote",
            "duration": "2023",
        }
        exp = Experience.from_dict(minimal_data)

        assert exp.projects == []
        assert exp.skills == []
        assert exp.description == ""
        assert exp.tags == []



class TestProject:
    """Tests for Project dataclass."""

    def test_round_trip_serialization(self, sample_project: Dict[str, Any]):
        """Test that to_dict then from_dict preserves data."""
        original = Project.from_dict(sample_project)
        serialized = original.to_dict()
        restored = Project.from_dict(serialized)

        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.tools == original.tools
        assert restored.repo == original.repo

    def test_optional_repo_field(self):
        """Test handling when repo is missing."""
        data = {
            "title": "Private Project",
            "description": ["A private project"],
            "tools": ["Python"],
        }
        project = Project.from_dict(data)

        assert project.repo is None

    def test_to_dict_excludes_none_repo(self):
        """Test that to_dict excludes None repo field."""
        data = {
            "title": "Private Project",
            "description": ["A private project"],
            "tools": ["Python"],
        }
        project = Project.from_dict(data)
        result = project.to_dict()

        assert "repo" not in result


class TestResume:
    """Tests for Resume dataclass."""

    def test_round_trip_serialization(self, sample_resume_data: Dict[str, Any]):
        """Test that to_dict then from_dict preserves data."""
        original = Resume.from_dict(sample_resume_data)
        serialized = original.to_dict()
        restored = Resume.from_dict(serialized)

        assert restored.name == original.name
        assert restored.basic_info.name == original.basic_info.name
        assert len(restored.education) == len(original.education)
        assert len(restored.experiences) == len(original.experiences)
        assert len(restored.projects) == len(original.projects)
        assert restored.keywords == original.keywords

    def test_nested_structures_preserved(self, sample_resume_data: Dict[str, Any]):
        """Test that nested structures are properly preserved through serialization."""
        resume = Resume.from_dict(sample_resume_data)
        serialized = resume.to_dict()

        # Verify nested basic_info
        assert serialized["basic_info"]["name"] == "John Doe"
        assert serialized["basic_info"]["email"] == "john.doe@example.com"

        # Verify nested education
        assert serialized["education"][0]["university"] == "State University"

        # Verify nested experiences with projects
        assert serialized["experiences"][0]["company"] == "Tech Corp"
        assert serialized["experiences"][0]["projects"][0]["title"] == "API Development"

        # Verify nested projects
        assert serialized["projects"][0]["title"] == "Resume Generator"

    def test_empty_resume(self):
        """Test handling of empty/minimal resume."""
        resume = Resume.from_dict({})

        assert resume.id is None
        assert resume.name is None
        assert resume.basic_info is None
        assert resume.education == []
        assert resume.experiences == []
        assert resume.projects == []
        assert resume.keywords == []

    def test_id_from_mongodb_format(self):
        """Test that _id field is properly handled (MongoDB format)."""
        data = {"_id": "mongo_id_123", "name": "test"}
        resume = Resume.from_dict(data)

        assert resume.id == "mongo_id_123"

    def test_id_from_standard_format(self):
        """Test that id field is properly handled."""
        data = {"id": "standard_id_456", "name": "test"}
        resume = Resume.from_dict(data)

        assert resume.id == "standard_id_456"
