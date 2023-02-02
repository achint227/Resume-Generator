import re
from json import load
from os import chdir, system

from load_sections import load_education, load_experiences, load_projects


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


def new_section(section_name, content, new_template=False):
    if new_template:
        if section_name.casefold() == "summary":
            content = "\n\\begin{cvparagraph}\n" + content + "\n\\end{cvparagraph}"
        else:
            content = "\n\\begin{cventries}\n\n" + content + "\n\\end{cventries}"

        return f"\\cvsection{{{section_name}}}\n{content}"
    return f"\\section{{{section_name}}}\n{content}"


def generate_resume_content(user_json, filter=None, new_template=False):
    with open(f"{user_json}", "r") as f:
        user = load(f)

    user = apply_latex_escape(user)

    education = new_section(
        "Education", load_education(user["education"], new_template), new_template
    )

    experience = new_section(
        "Experience",
        load_experiences(user["experiences"], filter, new_template),
        new_template,
    )
    projects = new_section(
        "Projects",
        load_projects(user["projects"], filter, new_template),
        new_template,
    )

    summary = (
        new_section("Summary", user["basic_info"].get("summary"), new_template)
        if user["basic_info"].get("summary")
        else ""
    )
    homepage = (
        f"\\homepage[{user['basic_info']['homepage']}]{{http://{user['basic_info']['homepage']}}}"
        if not new_template and user["basic_info"].get("homepage")
        else ""
    )
    sections = (
        summary,
        experience,
        projects,
        education,
    )
    if new_template:
        RESUME = f"""
\\documentclass[11pt, a4paper]{{russell}}
\\geometry{{left=1.4cm, top=.8cm, right=1.4cm, bottom=1.8cm, footskip=.5cm}}
\\fontdir[fonts/]
\\colorlet{{russell}}{{russell-black}}


\\setbool{{acvSectionColorHighlight}}{{true}}

\\renewcommand{{\\acvHeaderSocialSep}}{{\\quad\\textbar\\quad}}

\\name{'{'+'}{'.join([_ for _ in user.get('name').split()])+'}'}

\\address{{{user['basic_info'].get('address')}}}

\\mobile{{{user['basic_info'].get('phone')}}}
\\email{{{user['basic_info'].get('email')}}}
\\github{{{user['basic_info'].get('github')}}}
\\linkedin{{{user['basic_info'].get('linkedin')}}}
\\begin{{document}}

\\makecvheader


{sections[0]}

{sections[1]}

{sections[2]}

{sections[3]}


\\vspace*{{\\fill}}
\\end{{document}}

"""
    else:
        RESUME = f"""
% !TEX program = xelatex

\\documentclass{{resume}}

\\begin{{document}}
\\pagenumbering{{gobble}} % suppress displaying page number

\\name{{{user["name"]}}}

\\basicInfo{{
\\email{{{user["basic_info"]["email"]}}} 
\\phone{{{user["basic_info"]["phone"]}}} 
\\linkedin[{user["basic_info"]["linkedin"]}]{{https://www.linkedin.com/in/{user["basic_info"]["linkedin"]}}}
\\github[{user["basic_info"]["github"]}]{{https://github.com/{user["basic_info"]["github"]}}}
{homepage}
}}
{sections[0]}

{sections[1]}

{sections[2]}

{sections[3]}

\\end{{document}}

"""
    return (RESUME, "template2" if new_template else "template")


def main(user_file, filename, filter=None, new_template=False):
    RESUME, template = generate_resume_content(user_file, filter, new_template)
    filename += ".tex"
    with open(filename, "w") as output_tex:
        output_tex.write(RESUME)
    system(f"mv {filename} {template}/")
    chdir(f"{template}")
    system(f"xelatex -synctex=1 -interaction=nonstopmode {filename}")
    filename = filename.split(".")[0]
    system(f"mv {filename}.pdf ..")
    system(f"mv {filename}.tex ..")
    system(f"rm {filename}.*")


if __name__ == "__main__":
    main("user.json", "Resume1")
    main("user.json", "Resume2", new_template=True)
