import re


def make_bold(string, bold_words):
    if not bold_words:
        return string
    for word in bold_words:
        string = re.sub(r"\b" + word + r"\b", r"\\textbf{" + word + "}", string)
    return string


def new_template_project(project, org="", location="", duration="", items=[]):
    if type(items) == list:
        items = bullets_from_list(items, new_template=True)
    return f"""

\\cventry
{{{org}}}
{{{project}}}
{{{location}}}
{{{duration}}}
{{{items}}}"""


def bullets_from_list(items, end=True, highlight=None, new_template=False):
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


def create_details(project, filter=None):
    if not project:
        return ""
    rs = "\\begin{itemize}\n"
    for p in project:
        if filter and (
            not any([_.lower() in [_.lower() for _ in p.get("tools")] for _ in filter])
        ):
            continue

        rs += f"""
\\item \\textbf{{{p['title']}}} {{\\hfill {{{', '.join(p['tools'])}}}}}
{bullets_from_list(p['details'])}
"""
    return rs + "\n\\end{itemize}"


def create_experience(exp, filter=None, new_template=False):
    if new_template:
        return (
            new_template_project(
                exp["company"], exp["title"], exp["location"], exp["duration"]
            )
            + "\n\\begin{cvparagraph}\n"
            + create_details(exp["projects"], filter)
            + "\n\\end{cvparagraph}\n"
        )
    rs = f"""
\\datedsubsection{{\\textbf{{{exp['company']}}}}}{{{exp['location']}}}
\\role{{{exp['title']}}} {{\\hfill {exp['duration']}}}
{create_details(exp['projects'],filter)}
"""
    return rs


def load_experiences(experience, filter=None, new_template=False):
    rs = ""
    for exp in experience:
        rs += create_experience(exp, filter, new_template)
    return rs


def create_project(project, new_template=False):
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
            ", ".join(project.get("tools")),
            repo,
            "",
            project.get("description"),
        )
    repo = (
        f"{{Repo: }}\\github[{project['repo'].split('/')[-1]}]{{{project['repo']}}}"
        if project.get("repo")
        else ""
    )
    if repo:
        repo = "\\item" + repo
    rs = f"""\\subsection{{\\textbf{{{project["title"]}}}}}
{bullets_from_list(project["description"],end=False)}
\\item{{Tools/Libraries: {", ".join(project["tools"])}}}
{repo}
\\end{{itemize}}
"""
    return rs


def load_projects(projects, filter=None, new_template=False):
    rs = ""
    for p in projects:
        if filter and not bool(p.get("repo")):
            continue

        if filter and (
            not any([_.lower() in [_.lower() for _ in p.get("tools")] for _ in filter])
        ):
            continue
        rs += create_project(p, new_template)
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
