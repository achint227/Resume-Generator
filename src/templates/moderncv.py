"""
ModernCV - A modern CV template using the moderncv LaTeX class.

Uses the moderncv LaTeX class for a professional, modern look.
"""

from typing import Any, Dict, List, Optional

from src.repositories.base import PDFCacheRepository, ResumeRepository
from src.templates.base import Template
from src.templates.latex_utils import make_bold, split_string


class ModernCV(Template):
    """Resume template using the moderncv LaTeX class.
    
    A modern, professional template with a clean banking style.
    """
    
    def __init__(
        self,
        id: str,
        keywords: Optional[List[str]] = None,
        resume_repository: Optional[ResumeRepository] = None,
        cache_repository: Optional[PDFCacheRepository] = None,
    ) -> None:
        """Initialize ModernCV.
        
        Args:
            id: The unique identifier of the resume to load.
            keywords: Additional keywords to highlight.
            resume_repository: Repository for resume data access.
            cache_repository: Repository for PDF cache access.
        """
        if keywords is None:
            keywords = []
        super().__init__(id, keywords, resume_repository, cache_repository)
        self.latex_dir = "assets/latex"
        self.template_name = "moderncv"

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
            f"\\social[github]{{{basic_info.get('github')}}}"
            if basic_info.get("github")
            else ""
        )
        linkedin = (
            f"\\social[linkedin]{{{basic_info.get('linkedin')}}}"
            if basic_info.get("linkedin")
            else ""
        )
        return f"""\\documentclass[10pt,a4paper,sans]{{moderncv}}  
\\moderncvstyle{{banking}}
\\moderncvcolor{{blue}}
\\usepackage[scale=0.94]{{geometry}}
\\name{name}
\\address{address}
\\phone[mobile]{{{phone}}}
\\email{{{email}}}
{homepage}
{github}
{linkedin}
\\begin{{document}}
\\makecvtitle
"""

    def create_details(self, projects: List[Dict[str, Any]]) -> str:
        """Create details section for experience projects."""
        rs = ""

        if not projects:
            return rs

        for project in projects:
            tools = (
                f"""\\\\Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}"""
                if project.get("tools")
                else ""
            )
            rs += f"""\\smallskip\\cventry{{}}{{\\textbf{{{project.get("title","")}}}}}{{}}{{}}{{}}
{{{self.bullets_from_list(project.get("details",[]),True)}{tools}}}"""
        return rs

    def create_experience(self, experience: Dict[str, Any]) -> str:
        """Create an experience entry."""
        return f"""
\\medskip
\\item
{{\\cventry
{{{experience.get("duration","")}}}
{{{experience.get("title","")}}}
{{\\textbf{{{experience.get("company","")}}}}}
{{{experience.get("location","")}}}
{{}}{{}}}}
{self.create_details(experience.get("projects",[]))}
"""

    def create_project(self, project: Dict[str, Any]) -> str:
        """Create a project entry."""
        tools = (
            f"""
Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}"""
            if project.get("tools")
            else ""
        )
        return f"""\\medskip
\\item
{{\\cventry{{}}{{{project.get("repo","")}}}{{{project.get("title","")}}}{{}}{{}}
{{{make_bold(" ".join(project.get("description",[])),self.keywords)}}}{tools}
}}"""

    def new_section(self, section_name: str, content: str, summary: bool = False) -> str:
        """Create a new section in the resume."""
        if not content.strip():
            return ""
        if not summary:
            content = "\n\\begin{itemize}\n" + content + "\n\\end{itemize}"
        else:
            content = make_bold(content, self.keywords)
        return f"""
\\section{{{section_name}}}
{content}"""

    def bullets_from_list(self, items: List[str], dots: bool = False) -> str:
        """Format a list of items as LaTeX bullet points."""
        rs = []
        for item in items:
            if not dots:
                parts = item.split(":")
                bullet = (
                    f"\\textbf{{{parts[0]}:}}{make_bold(':'.join(parts[1:]),self.keywords)}"
                    if len(parts) > 1
                    else item
                )

                rs.append(f"""
{bullet}""")
            else:
                rs.append(f"""•{make_bold(item,self.keywords)}""")
        if dots:
            return "\\\\".join(rs)
        return "\n".join(rs)

    def create_education(self, education: Dict[str, Any]) -> str:
        """Create an education entry."""
        items = self.bullets_from_list(education.get("info", []))
        return f"""
\\medskip        
\\item
{{\\cventry{{{education.get("duration","")}}}
{{{education.get("degree","")}}}
{{{education.get("university","")}}}
{{{education.get("location","")}}}
{{}}{{}}}}
{items}"""
