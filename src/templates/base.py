"""
Base template class for resume generation.

This module provides the abstract base class that all resume templates
must inherit from, along with common functionality for PDF generation.
"""

import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.repositories.base import PDFCacheRepository, ResumeRepository
from src.repositories import get_resume_repository, get_cache_repository
from src.templates.latex_utils import (
    compute_content_hash,
    escape_latex_recursive,
    make_bold,
)

logger = logging.getLogger(__name__)


class Template(ABC):
    """Abstract base class for resume templates.
    
    Provides common functionality for loading resume data, generating PDFs,
    and managing caching. Subclasses must implement the abstract methods
    to define template-specific LaTeX formatting.
    
    Attributes:
        resume: The resume data dictionary with LaTeX-escaped values.
        keywords: List of keywords to highlight in the resume.
        latex_dir: Directory containing LaTeX resources (cls files, fonts).
        template_name: Name identifier for this template.
        output_dir: Directory for generated PDF files.
    """
    
    def __init__(
        self,
        id: str,
        keywords: Optional[List[str]] = None,
        resume_repository: Optional[ResumeRepository] = None,
        cache_repository: Optional[PDFCacheRepository] = None,
    ) -> None:
        """Initialize the template with resume data.
        
        Args:
            id: The unique identifier of the resume to load.
            keywords: Additional keywords to highlight in the resume.
            resume_repository: Repository for resume data access.
                If None, uses the default repository from configuration.
            cache_repository: Repository for PDF cache access.
                If None, uses the default repository from configuration.
                
        Raises:
            ValueError: If no resume is found with the given ID.
        """
        if keywords is None:
            keywords = []

        # Use injected repositories or get defaults
        self._resume_repo = resume_repository or get_resume_repository()
        self._cache_repo = cache_repository or get_cache_repository()
        
        # Load resume data
        resume = self._resume_repo.get_by_id(id)
        if not resume:
            raise ValueError(f"Resume with id {id} not found")
        
        # Preserve original name before escaping
        name = resume.get("name")
        self.resume = escape_latex_recursive(resume)
        self.resume["name"] = name
        
        # Handle keywords as either string or list
        keywords_data = resume.get("keywords", "")
        if isinstance(keywords_data, list):
            resume_keywords = [k.strip() for k in keywords_data if k.strip()]
        else:
            resume_keywords = [k.strip() for k in keywords_data.split(",") if k.strip()]

        self.keywords = keywords + resume_keywords
        self.latex_dir = "assets"  # Where LaTeX resources live (cls files, fonts)
        self.template_name = "default"  # Override in subclasses
        self.output_dir = Path("output")  # Where generated files go

    def create_file(self, order: str = "pwe", force: bool = False) -> str:
        """Generate PDF from resume data with caching.
        
        Args:
            order: Section order string (e.g., 'pwe' for projects, work, education).
            force: If True, regenerate even if cached version exists.
        
        Returns:
            Path to the generated PDF file.
            
        Raises:
            RuntimeError: If LaTeX compilation fails or times out.
        """
        resume_id = str(self.resume.get("_id", ""))
        resume_name = self.resume.get("name", "resume")
        content_hash = compute_content_hash(self.resume, self.template_name, order)
        
        # Filename: name_template_hash.pdf
        base_name = f"{resume_name}_{self.template_name}_{content_hash}"
        filename = f"{base_name}.tex"
        latex_path = Path(self.latex_dir)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        pdf_output = self.output_dir / f"{base_name}.pdf"
        
        # Check database cache first
        if not force:
            cached_path = self._cache_repo.get(
                resume_id, self.template_name, order, content_hash
            )
            if cached_path and Path(cached_path).exists():
                logger.info(f"Cache hit (db): {cached_path}")
                return cached_path
        
        logger.info(f"Cache miss, generating: {pdf_output}")
        
        # Write .tex file to latex resource folder (needs cls/fonts)
        tex_path = latex_path / filename
        tex_path.write_text(self.build_resume(order), encoding="utf-8")

        # Compile LaTeX to PDF
        try:
            result = subprocess.run(
                ["xelatex", "-synctex=1", "-interaction=nonstopmode", filename],
                cwd=latex_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning(f"xelatex warning/error: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error("LaTeX compilation timed out")
            raise RuntimeError("LaTeX compilation timed out")
        except FileNotFoundError:
            logger.error("xelatex not found. Please install texlive.")
            raise RuntimeError("xelatex not found")
        
        # Move generated PDF and tex to output folder
        for ext in [".pdf", ".tex"]:
            src = latex_path / f"{base_name}{ext}"
            dest = self.output_dir / f"{base_name}{ext}"
            if src.exists():
                src.rename(dest)
        
        # Clean up auxiliary files from latex folder
        for ext in [".aux", ".log", ".out", ".synctex.gz"]:
            aux_file = latex_path / f"{base_name}{ext}"
            if aux_file.exists():
                aux_file.unlink()
        
        # Store in database cache
        self._cache_repo.set(
            resume_id, self.template_name, order, content_hash, str(pdf_output)
        )
        
        return str(pdf_output)

    @abstractmethod
    def new_section(self, section_name: str, content: str, summary: bool = False) -> str:
        """Create a new section in the resume.
        
        Args:
            section_name: The title of the section.
            content: The content to include in the section.
            summary: If True, format as a summary section.
            
        Returns:
            LaTeX string for the section.
        """
        pass

    @abstractmethod
    def create_education(self, education: Dict[str, Any]) -> str:
        """Create an education entry.
        
        Args:
            education: Dictionary containing education data.
            
        Returns:
            LaTeX string for the education entry.
        """
        pass

    @abstractmethod
    def create_project(self, project: Dict[str, Any]) -> str:
        """Create a project entry.
        
        Args:
            project: Dictionary containing project data.
            
        Returns:
            LaTeX string for the project entry.
        """
        pass

    @abstractmethod
    def create_experience(self, experience: Dict[str, Any]) -> str:
        """Create an experience entry.
        
        Args:
            experience: Dictionary containing experience data.
            
        Returns:
            LaTeX string for the experience entry.
        """
        pass

    @abstractmethod
    def build_header(self) -> str:
        """Build the document header including preamble and personal info.
        
        Returns:
            LaTeX string for the document header.
        """
        pass


    def bullets_from_list(self, items: List[str]) -> str:
        """Format a list of items as LaTeX bullet points.
        
        Args:
            items: List of strings to format as bullet points.
            
        Returns:
            LaTeX itemize environment string, or empty string if items is empty.
        """
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\item{{{make_bold(item, self.keywords)}}}\n")
        return f"""\\begin{{itemize}}
{''.join(rs)}
\\end{{itemize}}"""

    def build_resume(self, order: str) -> str:
        """Build the complete resume LaTeX document.
        
        Args:
            order: Section order string (e.g., 'pwe').
            
        Returns:
            Complete LaTeX document string.
        """
        header = self.build_header()
        basic_info = self.resume.get("basic_info", {})
        summary_text = basic_info.get("summary", "") if isinstance(basic_info, dict) else ""
        summary = self.new_section("Summary", summary_text, summary=True)
        sections = []

        for section in order:
            if section == "e":
                sections.append(self.new_section("Education", self.load_education()))
            elif section == "p":
                sections.append(self.new_section("Projects", self.load_projects()))
            elif section == "w":
                sections.append(self.new_section("Experience", self.load_experiences()))

        return f"""
{header}
{summary}
{sections[0]}
{sections[1]}
{sections[2]}
\\end{{document}}       
"""

    def load_education(self) -> str:
        """Load and format all education entries.
        
        Returns:
            Combined LaTeX string for all education entries.
        """
        education = self.resume.get("education", [])
        rs = ""
        for ed in education:
            rs += self.create_education(ed)
        return rs

    def load_projects(self) -> str:
        """Load and format all project entries.
        
        Returns:
            Combined LaTeX string for all project entries.
        """
        projects = self.resume.get("projects", [])
        rs = ""
        for p in projects:
            rs += self.create_project(p)
        return rs

    def load_experiences(self) -> str:
        """Load and format all experience entries.
        
        Returns:
            Combined LaTeX string for all experience entries.
        """
        experience = self.resume.get("experiences", [])
        rs = ""
        for exp in experience:
            rs += self.create_experience(exp)
        return rs
