def bullets_from_list(items, end=True, highlight=None):
    if not items:
        return ""
    res = "\\begin{itemize}\n"
    for item in items:
        text = item.split()
        text = [
            (f"\\textbf{{{word}}}" if (highlight and word in highlight) else word)
            for word in text
        ]
        text = " ".join(text)
        res += f"\\item{{{item}}}"
        if end:
            res += "\n\\end{itemize}"
    return res


def load_experiences(experience):
    return ""


def create_project(project):
    repo = (
        f"\\\\{{Repo: }}\\github[{project['repo'].split('/')[-1]}]{{{project['repo']}}}"
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


def load_projects(projects):
    rs = ""
    for p in projects:
        rs += create_project(p)
    return rs


def load_education(education):
    rs = ""

    return rs
