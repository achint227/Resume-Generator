from template import Template, split_string, make_bold


class Template2(Template):
    def __init__(self, id, keywords=[]):
        super().__init__(id, keywords)
        self.folder = "russel"

    def build_header(self):
        basic_info = self.resume["basic_info"]
        name = split_string(basic_info.get("name"))
        address = split_string(basic_info.get('address'), ",")
        phone = basic_info.get("phone")
        email = basic_info.get("email")
        homepage = f"\\homepage{{{basic_info.get('homepage')}}}" if basic_info.get(
            'homepage') else ""
        github = f"\\github{{{basic_info.get('github')}}}" if basic_info.get(
            "github") else ""
        linkedin = f"\\linkedin{{{basic_info.get('linkedin')}}}" if basic_info.get(
            "linkedin") else ""
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

    def new_section(self, section_name, content, summary=False):
        if not content.strip():
            return ""
        if summary:
            content = "\n\\begin{cvparagraph}\n" + \
                content + "\n\\end{cvparagraph}"
        else:
            content = "\n\\begin{cventries}\n\n" + \
                content + "\n\\end{cventries}"
        return f"\\cvsection{{{section_name}}}\n{content}"

    def bullets_from_list(self, items):
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\item{{{make_bold(item,self.keywords)}}}\n")
        return f"""\\begin{{cvitems}}
{''.join(rs)}\\end{{cvitems}}"""

    def create_section(self, project, org="", location="", duration="", items=[]):
        if type(items) == list:
            items = self.bullets_from_list(items)
        return f"""
\\cventry
{{{org}}}
{{{project}}}
{{{location}}}
{{{duration}}}
{{{items}}}"""

    def create_details(self, projects):
        if not projects:
            return ""
        rs = "\\begin{itemize}\n"
        for p in projects:
            rs += f"""\\item \\textbf{{{p['title']}}} {{\\hfill {{{make_bold(", ".join(p.get("tools")), self.keywords)}}}}}
{super().bullets_from_list(p['details'])}
"""
        return rs + "\n\\end{itemize}"
    

    def create_education(self, education):
        return self.create_section(
            education.get("university"),
            education.get("degree", ""),
            education.get("location", ""),
            education.get("duration", ""),
            education.get("info", []),
        )

    def create_project(self, project):
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
            project.get("title"),
            make_bold(", ".join(project["tools"]), self.keywords),
            repo,
            "",
            project.get("description")
        )

    def create_experience(self, exp):
        return (
            self.create_section(
                exp["company"],
                exp["title"],
                exp["location"],
                exp["duration"]
            )
            + "\n\\begin{cvparagraph}\n"
            + self.create_details(exp["projects"])
            + "\n\\end{cvparagraph}\n"
        )


if __name__ == "__main__":
    c = Template2("64352dbad8c0f7239c8e3323")
    c.create_file()
