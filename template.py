from abc import ABC, abstractmethod
import re


def make_bold(string, bold_words):
    if not bold_words:
        return string
    for word in bold_words:
        string = re.sub(r"\b" + word + r"\b",
                        r"\\textbf{" + word + "}", string)
    return string


def to_latex_escape(string):
    string = re.sub(r"([&%$#_{}])", r"\\\1", string)
    return string


def apply_latex_escape(d):
    for key, value in d.items():
        if isinstance(value, str):
            d[key] = to_latex_escape(value)
        elif isinstance(value, dict):
            apply_latex_escape(value)
        elif isinstance(value, list):
            d[key] = [
                apply_latex_escape(i)
                if isinstance(i, (dict, list))
                else to_latex_escape(i)
                if isinstance(i, str)
                else i
                for i in value
            ]
    return d


class Template(ABC):
    def __init__(self, resume, keywords=[]):
        self.resume = apply_latex_escape(resume)
        self.keywords = keywords if keywords else resume.get("keywords")

    @abstractmethod
    def new_section(self, section_name, content):
        pass

    @abstractmethod
    def create_education(self):
        pass

    @abstractmethod
    def create_project(self):
        pass

    @abstractmethod
    def create_experience(self):
        pass

    @abstractmethod
    def build_resume(self):
        pass

    @abstractmethod
    def bullets_from_list(self, items):
        pass

    def load_education(self):
        education = self.resume.get("education")
        rs = ""
        for ed in education:
            rs += self.create_education(ed)
        return rs

    def load_projects(self):
        projects = self.resume.get("projects")
        rs = ""
        for p in projects:
            rs += self.create_project(p)
        return rs

    def load_experiences(self):
        experience = self.resume.get("experiences")
        rs = ""
        for exp in experience:
            rs += self.create_experience(exp)
        return rs


class ModernCV(Template):

    def build_resume(self):
        return super().build_resume()

    def create_details(self, projects):
        rs = ""

        if not projects:
            return rs

        for project in projects:
            tools=f"""\\\\Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}""" if project.get("tools") else ""
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
        tools=f"""\\\\Tools/Libraries: {make_bold(", ".join(project.get("tools",[])),self.keywords)}""" if project.get("tools") else ""
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