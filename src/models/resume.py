"""
Typed dataclasses for resume data structures.

This module provides type-safe data models for representing resume information
with serialization support (from_dict and to_dict methods).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class BasicInfo:
    """Contact and personal information for a resume."""
    name: str
    email: str
    phone: Union[str, int]
    address: Optional[str] = None
    summary: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    homepage: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BasicInfo":
        """Create BasicInfo from dictionary."""
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address"),
            summary=data.get("summary"),
            github=data.get("github"),
            linkedin=data.get("linkedin"),
            homepage=data.get("homepage"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert BasicInfo to dictionary."""
        result: Dict[str, Any] = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }
        if self.address is not None:
            result["address"] = self.address
        if self.summary is not None:
            result["summary"] = self.summary
        if self.github is not None:
            result["github"] = self.github
        if self.linkedin is not None:
            result["linkedin"] = self.linkedin
        if self.homepage is not None:
            result["homepage"] = self.homepage
        return result


@dataclass
class Education:
    """Educational background entry."""
    university: str
    degree: str
    location: str
    duration: str
    info: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Education":
        """Create Education from dictionary."""
        return cls(
            university=data.get("university", ""),
            degree=data.get("degree", ""),
            location=data.get("location", ""),
            duration=data.get("duration", ""),
            info=data.get("info", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Education to dictionary."""
        return {
            "university": self.university,
            "degree": self.degree,
            "location": self.location,
            "duration": self.duration,
            "info": self.info,
        }


@dataclass
class ProjectDetail:
    """Project details within an experience entry."""
    title: str
    tools: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectDetail":
        """Create ProjectDetail from dictionary."""
        return cls(
            title=data.get("title", ""),
            tools=data.get("tools", []),
            details=data.get("details", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ProjectDetail to dictionary."""
        return {
            "title": self.title,
            "tools": self.tools,
            "details": self.details,
        }


@dataclass
class Experience:
    """Work experience entry."""
    company: str
    title: str
    location: str
    duration: str
    projects: List[ProjectDetail] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """Create Experience from dictionary."""
        projects = [
            ProjectDetail.from_dict(p) for p in data.get("projects", [])
        ]
        return cls(
            company=data.get("company", ""),
            title=data.get("title", ""),
            location=data.get("location", ""),
            duration=data.get("duration", ""),
            projects=projects,
            skills=data.get("skills", []),
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Experience to dictionary."""
        return {
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "duration": self.duration,
            "projects": [p.to_dict() for p in self.projects],
            "skills": self.skills,
            "description": self.description,
            "tags": self.tags,
        }


@dataclass
class Project:
    """Personal/side project entry."""
    title: str
    description: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    repo: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create Project from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", []),
            tools=data.get("tools", []),
            repo=data.get("repo"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Project to dictionary."""
        result: Dict[str, Any] = {
            "title": self.title,
            "description": self.description,
            "tools": self.tools,
        }
        if self.repo is not None:
            result["repo"] = self.repo
        return result


@dataclass
class Resume:
    """Main resume data structure containing all resume information."""
    id: Optional[str] = None
    name: Optional[str] = None
    basic_info: Optional[BasicInfo] = None
    education: List[Education] = field(default_factory=list)
    experiences: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resume":
        """Create Resume from dictionary."""
        basic_info = None
        if data.get("basic_info"):
            basic_info = BasicInfo.from_dict(data["basic_info"])

        education = [
            Education.from_dict(e) for e in data.get("education", [])
        ]
        experiences = [
            Experience.from_dict(e) for e in data.get("experiences", [])
        ]
        projects = [
            Project.from_dict(p) for p in data.get("projects", [])
        ]

        return cls(
            id=data.get("id") or data.get("_id"),
            name=data.get("name"),
            basic_info=basic_info,
            education=education,
            experiences=experiences,
            projects=projects,
            keywords=data.get("keywords", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Resume to dictionary."""
        result: Dict[str, Any] = {}

        if self.id is not None:
            result["id"] = self.id
        if self.name is not None:
            result["name"] = self.name
        if self.basic_info is not None:
            result["basic_info"] = self.basic_info.to_dict()
        
        result["education"] = [e.to_dict() for e in self.education]
        result["experiences"] = [e.to_dict() for e in self.experiences]
        result["projects"] = [p.to_dict() for p in self.projects]
        result["keywords"] = self.keywords

        return result
