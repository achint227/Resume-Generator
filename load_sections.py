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
        res += f"\\item {item}"
    if end:
        res += "\n\\end{itemize}"
    return res


def create_details(project):
    if not project:
        return ""
    rs = "\\begin{itemize}\n"
    for p in project:
        rs += f"""
\\item \\textbf{{{p['title']}}}
{bullets_from_list(p['details'])}
"""
    return rs + "\n\\end{itemize}"


def create_experience(exp):
    rs = f"""
\\datedsubsection{{\\textbf{{{exp['company']}}}}}{{{exp['location']}}}
\\role{{{exp['title']}}} {{\\hfill {exp['duration']}}}
{create_details(exp['projects'])}
"""
    return rs


def load_experiences(experience):
    rs = ""
    for exp in experience:
        rs += create_experience(exp)
    return rs


def create_project(project):
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


def load_projects(projects):
    rs = ""
    for p in projects:
        rs += create_project(p)
    return rs


def create_education(education):
    rs = f"""\\datedsubsection{{\\textbf{{{education["university"]}}}}}{{{education.get("location"," ")}}}
\\role{{{education["degree"]}}} {{\\hfill {education["duration"]}}}
"""
    return rs


def load_education(education):
    rs = ""
    for ed in education:
        rs += create_education(ed)
    return rs
