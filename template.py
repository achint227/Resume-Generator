from abc import ABC, abstractmethod
import re


def split_string(s, sep=" "):
    return '{' + \
        '}{'.join(
            [_.strip() for _ in s.split(sep)])+'}'


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
        self.keywords = keywords + resume.get("keywords", [])

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

    @abstractmethod
    def bullets_from_list(self, items):
        pass

    def build_resume(self, order=['e', 'p', 'w']):
        header = self.build_header()
        summary = self.new_section("Summary", self.resume.get(
            "basic_info", {"summary": ""})["summary"],summary=True)
        sections = []

        for section in order:
            if section == 'e':
                sections.append(self.new_section(
                    "Education", self.load_education()))
            elif section == 'p':
                sections.append(self.new_section(
                    "Projects", self.load_projects()))
            elif section == 'w':
                sections.append(self.new_section(
                    "Experience", self.load_experiences()))

        return f"""
{header}
{summary}
{sections[0]}
{sections[1]}
{sections[2]}
\\end{{document}}       
"""

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
