"""
Template2 (Russel) - A modern resume template with the russell.cls class.

Uses the custom russell.cls LaTeX class for a modern, clean look.
"""

from typing import Any, Dict, List, Optional

from src.repositories.base import PDFCacheRepository, ResumeRepository
from src.templates.base import Template
from src.templates.latex_utils import make_bold, split_string


class Template2(Template):
    """Resume template using the custom russell.cls class.
    
    A modern template with a clean layout and professional styling.
    """
    
    def __init__(
        self,
        id: str,
        keywords: Optional[List[str]] = None,
        resume_repository: Optional[ResumeRepository] = None,
        cache_repository: Optional[PDFCacheRepository] = None,
    ) -> None:
        """Initialize Template2.
        
        Args:
            id: The unique identifier of the resume to load.
            keywords: Additional keywords to highlight.
            resume_repository: Repository for resume data access.
            cache_repository: Repository for PDF cache access.
        """
        if keywords is None:
            keywords = []
        super().__init__(id, keywords, resume_repository, cache_repository)
        self.latex_dir = "assets/latex/russel"
        self.template_name = "russel"

    def build_header(self) -> str:
        """Build the document header with personal information."""
        basic_info = self.resume.get("basic_info", {})
        name = split_string(basic_info.get("name", ""))
        address = split_string(basic_info.get("address", ""), ",")
        phone = basic_info.get("phone", "")
        email = basic_info.get("email", "")
        homepage = (
            f"\\homepage{{{basic_info.get('homepage')}}}"
            if basic_info.get("homepage")
            else ""
        )
        github = (
            f"\\github{{{basic_info.get('github')}}}" if basic_info.get("github") else ""
        )
        linkedin = (
            f"\\linkedin{{{basic_info.get('linkedin')}}}"
            if basic_info.get("linkedin")
            else ""
        )
        return f"""\\documentclass[11pt, a4paper]{{russell}}
\\geometry{{left=1.4cm, top=.8cm, right=1.4cm, bottom=1.8cm, footskip=.5cm}}
\\fontdir[fonts/]
\\colorlet{{russell}}{{russell-black}}
\\setbool{{acvSectionColorHighlight}}{{true}}
\\renewcommand{{\\acvHeaderSocialSep}}{{\\quad\\textbar\\quad}}
\\name{name}
\\address{{{address}}}
\\mobile{{{phone}}}
\\email{{{email}}}
{linkedin}
{homepage}
{github}
\\begin{{document}}
\\makecvheader
"""

    def new_section(self, section_name: str, content: str, summary: bool = False) -> str:
        """Create a new section in the resume."""
        if not content.strip():
            return ""
        if summary:
            content = "\n\\begin{cvparagraph}\n" + content + "\n\\end{cvparagraph}"
        else:
            content = "\n\\begin{cventries}\n\n" + content + "\n\\end{cventries}"
        return f"\\cvsection{{{section_name}}}\n{content}"

    def bullets_from_list(self, items: List[str]) -> str:
        """Format a list of items as LaTeX bullet points using cvitems."""
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\item{{{make_bold(item, self.keywords)}}}\n")
        return f"""\\begin{{cvitems}}
{''.join(rs)}\\end{{cvitems}}"""

    def create_section(
        self,
        project: str,
        org: str = "",
        location: str = "",
        duration: str = "",
        items: Any = None,
    ) -> str:
        """Create a generic section entry using cventry."""
        if items is None:
            items = []
        if isinstance(items, list):
            items = self.bullets_from_list(items)
        return f"""
\\cventry
{{{org}}}
{{{project}}}
{{{location}}}
{{{duration}}}
{{{items}}}"""

    def create_details(self, projects: List[Dict[str, Any]]) -> str:
        """Create details section for experience projects."""
        if not projects:
            return ""
        rs = "\\begin{itemize}\n"
        for p in projects:
            rs += f"""\\item \\textbf{{{p.get('title','')}}} {{\\hfill {{{make_bold(", ".join(p.get("tools",[])), self.keywords)}}}}}
{super().bullets_from_list(p.get('details',[]))}
"""
        return rs + "\n\\end{itemize}"

    def create_education(self, education: Dict[str, Any]) -> str:
        """Create an education entry."""
        return self.create_section(
            education.get("university", ""),
            education.get("degree", ""),
            education.get("location", ""),
            education.get("duration", ""),
            education.get("info", []),
        )

    def create_project(self, project: Dict[str, Any]) -> str:
        """Create a project entry."""
        repo = (
            "\\href{"
            + project.get("repo")
            + "}{"
            + project.get("repo").split("/")[-1]
            + "}"
            if project.get("repo")
            else ""
        )
        return self.create_section(
            project.get("title", ""),
            make_bold(", ".join(project.get("tools", [])), self.keywords),
            repo,
            "",
            project.get("description", []),
        )

    def create_experience(self, experience: Dict[str, Any]) -> str:
        """Create an experience entry."""
        return (
            self.create_section(
                experience.get("company", ""),
                experience.get("title", ""),
                experience.get("location", ""),
                experience.get("duration", ""),
            )
            + "\n\\begin{cvparagraph}\n"
            + self.create_details(experience.get("projects", []))
            + "\n\\end{cvparagraph}\n"
        )
