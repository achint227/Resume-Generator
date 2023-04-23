from template import Template, make_bold


class Template1(Template):
    def __init__(self, id, keywords=...):
        super().__init__(id, keywords)
        self.folder = "resume"

    def build_header(self):
        basic_info = self.resume["basic_info"]
        name = basic_info.get("name")
        phone = basic_info.get("phone")
        email = basic_info.get("email")
        homepage = f"\\homepage[{basic_info.get('homepage')}]{{{basic_info.get('homepage')}}}" if basic_info.get(
            'homepage') else ""
        github = f"\\github[{basic_info.get('github')}]{{https://github.com/{github}}}" if basic_info.get(
            "github") else ""
        linkedin = f"\\linkedin[{basic_info.get('linkedin')}]{{https://www.linkedin.com/in/{linkedin}}}" if basic_info.get(
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

    def new_section(self, section_name, content, summary):
        if not content.strip():
            return ""
        return f"\\section{{{section_name}}}\n{content}"

    def bullets_from_list(self, items):
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
