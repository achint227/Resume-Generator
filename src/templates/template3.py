"""
Template3 (Classic) - A classic ATS-friendly resume template.

Uses standard LaTeX article class with custom commands for ATS compatibility.
"""

from typing import Any, Dict, List, Optional

from src.repositories.base import PDFCacheRepository, ResumeRepository
from src.templates.base import Template
from src.templates.latex_utils import make_bold


class Template3(Template):
    """Classic resume template using standard article class.
    
    An ATS-friendly template designed for machine readability
    while maintaining a professional appearance.
    """
    
    def __init__(
        self,
        id: str,
        keywords: Optional[List[str]] = None,
        resume_repository: Optional[ResumeRepository] = None,
        cache_repository: Optional[PDFCacheRepository] = None,
    ) -> None:
        """Initialize Template3.
        
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
        self.template_name = "classic"

    def build_header(self) -> str:
        """Build the document header with personal information."""
        basic_info = self.resume.get("basic_info", {})
        name = basic_info.get("name", "")
        phone = basic_info.get("phone", "")
        email = basic_info.get("email", "")
        location = basic_info.get("address", "")
        github = basic_info.get("github", "")
        linkedin = basic_info.get("linkedin", "")
        
        # Parse location for city and state
        loc_parts = location.split(",") if location else []
        city = loc_parts[0].strip() if len(loc_parts) > 0 else ""
        state = loc_parts[1].strip() if len(loc_parts) > 1 else ""

        github_link = f"\\href{{https://github.com/{github}}}{{\\underline{{github.com/{github}}}}}" if github else ""
        linkedin_link = f"\\href{{https://linkedin.com/in/{linkedin}}}{{\\underline{{linkedin.com/in/{linkedin}}}}}" if linkedin else ""
        
        # Build contact line with conditional separators
        contact_parts = []
        if city and state:
            contact_parts.append(f"{city}, {state}")
        elif location:
            contact_parts.append(location)
        if email:
            contact_parts.append(f"\\href{{mailto:{email}}}{{\\underline{{{email}}}}}")
        if phone:
            contact_parts.append(str(phone))
        if linkedin_link:
            contact_parts.append(linkedin_link)
        if github_link:
            contact_parts.append(github_link)
        
        contact_line = " $|$ ".join(contact_parts)
        
        return f"""\\documentclass[letterpaper,8pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}
\\input{{glyphtounicode}}
\\setlength{{\\footskip}}{{0.5in}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Adjust margins
\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-0.5in}}
\\addtolength{{\\textheight}}{{1in}}

\\urlstyle{{same}}

\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting
\\titleformat{{\\section}}{{
    \\vspace{{-4pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

% Ensure that generate pdf is machine readable/ATS parsable
\\pdfgentounicode=1

%-------------------------
% Custom commands
\\newcommand{{\\resumeItem}}[1]{{
    \\item\\small{{
        {{#1 \\vspace{{-2pt}}}}
    }}
}}

\\newcommand{{\\resumeSubheading}}[4]{{
    \\vspace{{-2pt}}\\item
    \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{#1}} & #2 \\\\
        \\textit{{\\small#3}} & \\textit{{\\small #4}} \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeProjectHeading}}[2]{{
    \\item
    \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\small#1 & #2 \\\\
    \\end{{tabular*}}\\vspace{{-7pt}}
}}

\\newcommand{{\\resumeSubItem}}[1]{{\\resumeItem{{#1}}\\vspace{{-4pt}}}}

\\renewcommand\\labelitemii{{$\\vcenter{{\\hbox{{\\tiny$\\bullet$}}}}$}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0in,label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}
\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}[leftmargin=0.15in]}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-5pt}}}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{{document}}

%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{1pt}}
    \\small {contact_line}
\\end{{center}}
"""


    def new_section(self, section_name: str, content: str, summary: bool = False) -> str:
        """Create a new section in the resume."""
        if not content.strip():
            return ""
        if summary:
            content = make_bold(content, self.keywords)
            return f"""\\section{{{section_name}}}
\\resumeSubHeadingListStart
\\resumeItem{{{content}}}
\\resumeSubHeadingListEnd
"""
        return f"\\section{{{section_name}}}\n{content}"

    def bullets_from_list(self, items: List[str]) -> str:
        """Format a list of items as LaTeX bullet points using resumeItem."""
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\resumeItem{{{make_bold(item, self.keywords)}}}\n")
        return f"""\\resumeItemListStart
{''.join(rs)}\\resumeItemListEnd
"""

    def create_education(self, education: Dict[str, Any]) -> str:
        """Create an education entry."""
        university = education.get("university", "")
        degree = education.get("degree", "")
        location = education.get("location", "")
        duration = education.get("duration", "")
        items = self.bullets_from_list(education.get("info", []))
        
        return f"""\\resumeSubheading
{{{university}}}{{{location}}}
{{{degree}}}{{{duration}}}
{items}
"""

    def create_project(self, project: Dict[str, Any]) -> str:
        """Create a project entry."""
        title = project.get("title", "")
        tools = ", ".join(project.get("tools", []))
        
        # Create project heading with tools
        heading = f"\\textbf{{{title}}}"
        if tools:
            heading += f" -- {make_bold(tools, self.keywords)}"
        
        details = self.bullets_from_list(project.get("description", []))
        
        return f"""\\resumeProjectHeading
{{{heading}}}{{}}
{details}
"""

    def create_experience(self, experience: Dict[str, Any]) -> str:
        """Create an experience entry."""
        company = experience.get("company", "")
        title = experience.get("title", "")
        location = experience.get("location", "")
        duration = experience.get("duration", "")
        
        # Handle projects within experience
        projects = experience.get("projects", [])
        if projects:
            # Flatten all project details into a single bullet list
            all_details = []
            for proj in projects:
                all_details.extend(proj.get("details", []))
            details = self.bullets_from_list(all_details)
        else:
            details = ""
        
        return f"""\\resumeSubheading
{{{title}}}{{{duration}}}
{{{company}}}{{{location}}}
{details}
"""

    def build_resume(self, order: str) -> str:
        """Build the complete resume LaTeX document."""
        header = self.build_header()
        basic_info = self.resume.get("basic_info", {})
        summary_text = basic_info.get("summary", "") if isinstance(basic_info, dict) else ""
        summary = self.new_section("Summary", summary_text, summary=True) if summary_text else ""
        
        sections = []
        for section in order:
            if section == "e":
                edu_content = self.load_education()
                if edu_content:
                    sections.append(f"""\\section{{Education}}
\\resumeSubHeadingListStart
{edu_content}\\resumeSubHeadingListEnd
""")
            elif section == "p":
                proj_content = self.load_projects()
                if proj_content:
                    sections.append(f"""\\section{{Projects}}
\\resumeSubHeadingListStart
{proj_content}\\resumeSubHeadingListEnd
""")
            elif section == "w":
                exp_content = self.load_experiences()
                if exp_content:
                    sections.append(f"""\\section{{Experience}}
\\resumeSubHeadingListStart
{exp_content}\\resumeSubHeadingListEnd
""")
        
        return f"""{header}
{summary}
{''.join(sections)}
\\end{{document}}
"""
