"""
Template1 (Resume) - A clean, professional resume template.

Uses the custom resume.cls LaTeX class for formatting.
"""

from typing import Any, Dict, List, Optional

from src.repositories.base import PDFCacheRepository, ResumeRepository
from src.templates.base import Template
from src.templates.latex_utils import make_bold


class Template1(Template):
    """Resume template using the custom resume.cls class.
    
    A clean, professional template with sections for education,
    experience, and projects.
    """
    
    def __init__(
        self,
        id: str,
        keywords: Optional[List[str]] = None,
        resume_repository: Optional[ResumeRepository] = None,
        cache_repository: Optional[PDFCacheRepository] = None,
    ) -> None:
        """Initialize Template1.
        
        Args:
            id: The unique identifier of the resume to load.
            keywords: Additional keywords to highlight.
            resume_repository: Repository for resume data access.
            cache_repository: Repository for PDF cache access.
        """
        if keywords is None:
            keywords = []
        super().__init__(id, keywords, resume_repository, cache_repository)
        self.latex_dir = "assets/latex/resume"
        self.template_name = "resume"

    def build_header(self) -> str:
        """Build the document header with personal information."""
        basic_info = self.resume.get("basic_info", {})
        name = basic_info.get("name", "")
        phone = basic_info.get("phone", "")
        email = basic_info.get("email", "")
        homepage = (
            f"\\homepage[{basic_info.get('homepage')}]{{{basic_info.get('homepage')}}}"
            if basic_info.get("homepage")
            else ""
        )
        github = (
            f"\\github[{basic_info.get('github')}]{{https://github.com/{basic_info.get('github')}}}"
            if basic_info.get("github")
            else ""
        )
        linkedin = (
            f"\\linkedin[{basic_info.get('linkedin')}]{{https://www.linkedin.com/in/{basic_info.get('linkedin')}}}"
            if basic_info.get("linkedin")
            else ""
        )
        return f"""\\documentclass{{resume}}
\\begin{{document}}
\\pagenumbering{{gobble}}
\\name{{{name}}}
\\basicInfo{{
\\email{{{email}}}
\\phone{{{phone}}} 
{linkedin}
{github}
{homepage}
}}
"""

    def new_section(self, section_name: str, content: str, summary: bool = False) -> str:
        """Create a new section in the resume."""
        if not content.strip():
            return ""
        if summary:
            content = make_bold(content, self.keywords)
        return f"\\section{{{section_name}}}\n{content}"

    def create_education(self, education: Dict[str, Any]) -> str:
        """Create an education entry."""
        items = self.bullets_from_list(education.get("info", []))
        return f"""\\datedsubsection{{\\textbf{{{education.get("university","")}}}}}{{{education.get("location","")}}}
\\role{{{education.get("degree","")}}} {{\\hfill {education.get("duration","")}}}
{items}
"""

    def create_details(self, projects: List[Dict[str, Any]]) -> str:
        """Create details section for experience projects."""
        if not projects:
            return ""
        rs = "\\begin{itemize}\n"
        for p in projects:
            rs += f"""\\item \\textbf{{{p.get('title','')}}} {{\\hfill {{{make_bold(", ".join(p.get("tools",[])), self.keywords)}}}}}
{self.bullets_from_list(p.get('details',[]))}
"""
        return rs + "\n\\end{itemize}"

    def create_experience(self, experience: Dict[str, Any]) -> str:
        """Create an experience entry."""
        company = experience.get('company', '')
        location = experience.get('location', '')
        title = experience.get('title', '')
        duration = experience.get('duration', '')
        details = self.create_details(experience.get('projects', []))
        return f"""\\datedsubsection{{\\textbf{{{company}}}}}{{{location}}}
\\role{{{title}}} {{\\hfill {duration}}}
{details}
"""

    def create_project(self, project: Dict[str, Any]) -> str:
        """Create a project entry."""
        repo = (
            f"\\item{{Repo: }}\\github[{project['repo'].split('/')[-1]}]{{{project['repo']}}}"
            if project.get("repo")
            else ""
        )
        return f"""\\subsection{{\\textbf{{{project.get("title","")}}}}}
{self.bullets_from_list(project.get("description",[]))}
\\begin{{itemize}}
\\item{{Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}}}
{repo}
\\end{{itemize}}
"""
