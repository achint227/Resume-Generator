import re

from config import KEYWORDS


def make_bold(string, bold_words):
    if not bold_words:
        return string
    for word in bold_words:
        string = re.sub(r"\b" + word + r"\b", r"\\textbf{" + word + "}", string)
    return string


def new_template_project(
    project, org="", location="", duration="", items=[], keywords=None
):
    if type(items) == list:
        items = bullets_from_list(items, highlight=keywords, new_template=True)
    return f"""

\\cventry
{{{org}}}
{{{project}}}
{{{location}}}
{{{duration}}}
{{{items}}}"""


def bullets_from_list(items, end=True, highlight=None, new_template=False):
    if not highlight:
        highlight = KEYWORDS
    if not items:
        return ""
    cmd = "cvitems" if new_template else "itemize"
    res = f"\\begin{{{cmd}}}"
    for item in items:
        text = make_bold(item, highlight)
        res += f"\n\\item {{{text}}}"
    if end:
        res += f"\n\\end{{{cmd}}}"
    return f"\n{res}\n"


def create_details(project, keywords=None):
    if not keywords:
        keywords = KEYWORDS
    if not project:
        return ""
    rs = "\\begin{itemize}\n"
    for p in project:

        rs += f"""
\\item \\textbf{{{p['title']}}} {{\\hfill {{{make_bold(", ".join(p.get("tools")), keywords)}}}}}
{bullets_from_list(p['details'],highlight=keywords)}
"""
    return rs + "\n\\end{itemize}"


def create_experience(exp, keywords=None, new_template=False):
    if new_template:
        return (
            new_template_project(
                exp["company"],
                exp["title"],
                exp["location"],
                exp["duration"],
                keywords=keywords,
            )
            + "\n\\begin{cvparagraph}\n"
            + create_details(exp["projects"], keywords)
            + "\n\\end{cvparagraph}\n"
        )
    rs = f"""
\\datedsubsection{{\\textbf{{{exp['company']}}}}}{{{exp['location']}}}
\\role{{{exp['title']}}} {{\\hfill {exp['duration']}}}
{create_details(exp['projects'],keywords)}
"""
    return rs


def load_experiences(experience, keywords=None, new_template=False):
    rs = ""
    for exp in experience:
        rs += create_experience(exp, keywords, new_template)
    return rs


def create_project(project, keywords=None, new_template=False):
    if not keywords:
        keywords = KEYWORDS
    if new_template:
        repo = (
            "\\href{"
            + project.get("repo")
            + "}{"
            + project.get("repo").split("/")[-1]
            + "}"
            if project.get("repo")
            else ""
        )
        return new_template_project(
            project.get("title"),
            make_bold(", ".join(project["tools"]), keywords),
            repo,
            "",
            project.get("description"),
            keywords=keywords,
        )
    repo = (
        f"{{Repo: }}\\github[{project['repo'].split('/')[-1]}]{{{project['repo']}}}"
        if project.get("repo")
        else ""
    )
    if repo:
        repo = "\\item" + repo
    rs = f"""\\subsection{{\\textbf{{{project["title"]}}}}}
{bullets_from_list(project["description"],end=False,highlight=keywords)}
\\item{{Tools/Libraries: {make_bold(", ".join(project["tools"]),keywords)}}}
{repo}
\\end{{itemize}}
"""
    return rs


def load_projects(projects, keywords=None, new_template=False):
    rs = ""
    for p in projects:
        rs += create_project(p, keywords, new_template)
    return rs


def create_education(education, new_template=False):
    if new_template:
        return new_template_project(
            education.get("university"),
            education.get("degree", ""),
            education.get("location", ""),
            education.get("duration", ""),
            education.get("info", []),
        )
    return f"""\\datedsubsection{{\\textbf{{{education["university"]}}}}}{{{education.get("location","")}}}
\\role{{{education["degree"]}}} {{\\hfill {education["duration"]}}}
"""


def load_education(education, new_template=False):
    rs = ""
    for ed in education:
        rs += create_education(ed, new_template)
    return rs
