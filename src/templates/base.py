from abc import ABC, abstractmethod
from os import chdir, system
import re

from src.database.operations import find_by_id


def split_string(s, sep=" "):
    return "{" + "}{".join([_.strip() for _ in s.split(sep)]) + "}"


def make_bold(string, bold_words):
    if not bold_words:
        return string
    for word in bold_words:
        pattern = re.compile(r"\b" + word + r"\b", flags=re.IGNORECASE)
        for match in pattern.finditer(string):
            start, end = match.span()
            word_case = string[start:end]
            string = string[:start] + "\\textbf{" + word_case + "}" + string[end:]
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
    def __init__(self, id, keywords=[]):
        resume = find_by_id(id)
        name = resume.get("name")
        self.resume = apply_latex_escape(resume)
        self.resume["name"] = name
        
        # Handle keywords as either string or list
        keywords_data = resume.get("keywords", "")
        if isinstance(keywords_data, list):
            resume_keywords = [k.strip() for k in keywords_data if k.strip()]
        else:
            resume_keywords = [k.strip() for k in keywords_data.split(",") if k.strip()]

        self.keywords = keywords + resume_keywords
        self.folder = "assets"

    def create_file(self, order="pwe"):
        filename = self.resume.get("name") + ".tex"

        with open(filename, "w") as output_tex:
            output_tex.write(self.build_resume(order))
        system(f"mv {filename} {self.folder}/")
        chdir(f"{self.folder}")
        system(f"xelatex -synctex=1 -interaction=nonstopmode {filename}")
        filename = filename.split(".")[0]
        system(f"mv {filename}.pdf ../assets")
        system(f"mv {filename}.tex ../assets")
        system(f"rm {filename}.*")
        chdir("..")
        return f"assets/{filename}.pdf"

    @abstractmethod
    def new_section(self, section_name, content, summary):
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
    def build_header(self):
        pass

    def bullets_from_list(self, items):
        if not items:
            return ""
        rs = []
        for item in items:
            rs.append(f"\\item{{{make_bold(item,self.keywords)}}}\n")
        return f"""\\begin{{itemize}}
{''.join(rs)}
\\end{{itemize}}"""

    def build_resume(self, order):
        header = self.build_header()
        basic_info = self.resume.get("basic_info", {})
        summary_text = basic_info.get("summary", "") if isinstance(basic_info, dict) else ""
        summary = self.new_section("Summary", summary_text, summary=True)
        sections = []

        for section in order:
            if section == "e":
                sections.append(self.new_section("Education", self.load_education()))
            elif section == "p":
                sections.append(self.new_section("Projects", self.load_projects()))
            elif section == "w":
                sections.append(self.new_section("Experience", self.load_experiences()))

        return f"""
{header}
{summary}
{sections[0]}
{sections[1]}
{sections[2]}
\\end{{document}}       
"""

    def load_education(self):
        education = self.resume.get("education", [])
        rs = ""
        for ed in education:
            rs += self.create_education(ed)
        return rs

    def load_projects(self):
        projects = self.resume.get("projects", [])
        rs = ""
        for p in projects:
            rs += self.create_project(p)
        return rs

    def load_experiences(self):
        experience = self.resume.get("experiences", [])
        rs = ""
        for exp in experience:
            rs += self.create_experience(exp)
        return rs
