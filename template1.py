from template import Template, make_bold


class Template1(Template):
    def __init__(self, id, keywords=[]):
        super().__init__(id, keywords)
        self.folder = "resume"

    def build_header(self):
        basic_info = self.resume["basic_info"]
        name = basic_info.get("name")
        phone = basic_info.get("phone")
        email = basic_info.get("email")
        homepage = f"\\homepage[{basic_info.get('homepage')}]{{{basic_info.get('homepage')}}}" if basic_info.get(
            'homepage') else ""
        github = f"\\github[{basic_info.get('github')}]{{https://github.com/{basic_info.get('github')}}}" if basic_info.get(
            "github") else ""
        linkedin = f"\\linkedin[{basic_info.get('linkedin')}]{{https://www.linkedin.com/in/{basic_info.get('linkedin')}}}" if basic_info.get(
            "linkedin") else ""
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

    def new_section(self, section_name, content, summary=False):
        if not content.strip():
            return ""
        if summary:
            content = make_bold(content, self.keywords)
        return f"\\section{{{section_name}}}\n{content}"

    def bullets_from_list(self, items):
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\item{{{make_bold(item,self.keywords)}}}\n")
        return f"""\\begin{{itemize}}
{''.join(rs)}
\\end{{itemize}}"""

    def create_education(self, education):
        items = self.bullets_from_list(education.get("info", []))
        return f"""\\datedsubsection{{\\textbf{{{education.get("university","")}}}}}{{{education.get("location","")}}}
\\role{{{education.get("degree","")}}} {{\\hfill {education.get("duration","")}}}
{items}
"""

    def create_details(self, projects):
        if not projects:
            return ""
        rs = "\\begin{itemize}\n"
        for p in projects:
            rs += f"""\\item \\textbf{{{p['title']}}} {{\\hfill {{{make_bold(", ".join(p.get("tools")), self.keywords)}}}}}
{self.bullets_from_list(p['details'])}
"""
        return rs + "\n\\end{itemize}"

    def create_experience(self, exp):
        return f"""\\datedsubsection{{\\textbf{{{exp['company']}}}}}{{{exp['location']}}}
\\role{{{exp['title']}}} {{\\hfill {exp['duration']}}}
{self.create_details(exp['projects'])}
"""

    def create_project(self, project):
        repo = (
            f"\\item{{Repo: }}\\github[{project['repo'].split('/')[-1]}]{{{project['repo']}}}"
            if project.get("repo")
            else ""
        )
        return f"""\\subsection{{\\textbf{{{project["title"]}}}}}
{self.bullets_from_list(project["description"])}
\\begin{{itemize}}
\\item{{Tools/Libraries: {make_bold(", ".join(project["tools"]),self.keywords)}}}
{repo}
\\end{{itemize}}
"""


if __name__ == "__main__":
    c = Template1("64352dbad8c0f7239c8e3323")
    c.create_file()
