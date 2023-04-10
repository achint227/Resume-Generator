from template import Template, make_bold


class ModernCV(Template):

    def build_resume(self):
        return super().build_resume()

    def create_details(self, projects):
        rs = ""

        if not projects:
            return rs

        for project in projects:
            tools = f"""\\\\Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}""" if project.get(
                "tools") else ""
            rs += f"""\\smallskip\\cventry{{}}{{\\textbf{{{project.get("title","")}}}}}{{}}{{}}{{}}
{{{self.bullets_from_list(project.get("details",[]),True)}{tools}}}"""
        return rs

    def create_experience(self, exp):
        return f"""
\\medskip
\\item
{{\\cventry
{{{exp.get("duration","")}}}
{{{exp.get("title")}}}
{{\\textbf{{{exp.get("company","")}}}}}
{{{exp.get("location","")}}}
{{}}{{}}}}
{self.create_details(exp.get("projects"))}
"""

    def create_project(self, project):
        tools = f"""\\\\Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}""" if project.get(
            "tools") else ""
        return f"""\\medskip
\\item
{{\\cventry{{}}{{{project.get("repo","")}}}{{{project.get("title","")}}}{{}}{{}}
{{{make_bold(" ".join(project.get("description",[])),self.keywords)}}}{tools}
}}"""

    def new_section(self, section_name, content, summary=False):
        if not content.strip():
            return ""
        if not summary:
            content = "\n\\begin{itemize}\n" + \
                content + "\n\\end{itemize}"
        return f"""
\\section{{{section_name}}}
{content}"""

    def bullets_from_list(self, items, dots=False):
        rs = []
        for item in items:
            if not dots:
                parts = item.split(":")
                bullet = f"\\textbf{{{parts[0]}:}}{make_bold(':'.join(parts[1:]),self.keywords)}" if len(
                    parts) > 1 else item

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


if __name__ == "__main__":
    from json import load
    with open("user.json", "r") as f:
        resume = load(f)
    c = ModernCV(resume, ["SQL"])
    print(c.load_experiences())
