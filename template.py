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
        self.keywords = keywords + resume.get("keywords", [])

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
