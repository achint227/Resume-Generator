from src.templates.base import Template, make_bold, split_string


class ModernCV(Template):
    def __init__(self, id, keywords=[]):
        super().__init__(id, keywords)
        self.folder = "moderncv"

    def build_header(self):
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

    def create_details(self, projects):
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

    def create_experience(self, exp):
        return f"""
\\medskip
\\item
{{\\cventry
{{{exp.get("duration","")}}}
{{{exp.get("title","")}}}
{{\\textbf{{{exp.get("company","")}}}}}
{{{exp.get("location","")}}}
{{}}{{}}}}
{self.create_details(exp.get("projects",[]))}
"""

    def create_project(self, project):
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

    def new_section(self, section_name, content, summary=False):
        if not content.strip():
            return ""
        if not summary:
            content = "\n\\begin{itemize}\n" + content + "\n\\end{itemize}"
        else:
            content = make_bold(content, self.keywords)
        return f"""
\\section{{{section_name}}}
{content}"""

    def bullets_from_list(self, items, dots=False):
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

    def create_education(self, education):
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
