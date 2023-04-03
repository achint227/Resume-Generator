import re
import sys
from json import load
from os import chdir, system

from load_sections import load_education, load_experiences, load_projects
from load_user import find_by_resume_name, find_by_id


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


def generate_resume_content(resume, keywords=None, new_template=False):

    resume = apply_latex_escape(resume)

    education = new_section(
        "Education", load_education(resume["education"], new_template), new_template
    )

    experience = new_section(
        "Experience",
        load_experiences(resume["experiences"], keywords, new_template),
        new_template,
    )
    projects = new_section(
        "Projects",
        load_projects(resume["projects"], keywords, new_template),
        new_template,
    )

    summary = (
        new_section("Summary", resume["basic_info"].get("summary"), new_template)
        if resume["basic_info"].get("summary")
        else ""
    )
    homepage = (
        f"\\homepage[{resume['basic_info']['homepage']}]{{http://{resume['basic_info']['homepage']}}}"
        if not new_template and resume["basic_info"].get("homepage")
        else ""
    )
    sections = (
        summary,
        projects,
        education,
        experience,
    )
    if new_template:
        RESUME = f"""
\\documentclass[11pt, a4paper]{{russell}}
\\geometry{{left=1.4cm, top=.8cm, right=1.4cm, bottom=1.8cm, footskip=.5cm}}
\\fontdir[fonts/]
\\colorlet{{russell}}{{russell-black}}


\\setbool{{acvSectionColorHighlight}}{{true}}

\\renewcommand{{\\acvHeaderSocialSep}}{{\\quad\\textbar\\quad}}

\\name{'{'+'}{'.join([_ for _ in resume['basic_info'].get('name').split()])+'}'}

\\address{{{resume['basic_info'].get('address')}}}

\\mobile{{{resume['basic_info'].get('phone')}}}
\\email{{{resume['basic_info'].get('email')}}}
\\github{{{resume['basic_info'].get('github')}}}
\\linkedin{{{resume['basic_info'].get('linkedin')}}}
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

\\name{{{resume["basic_info"]["name"]}}}

\\basicInfo{{
\\email{{{resume["basic_info"]["email"]}}} 
\\phone{{{resume["basic_info"]["phone"]}}} 
\\linkedin[{resume["basic_info"]["linkedin"]}]{{https://www.linkedin.com/in/{resume["basic_info"]["linkedin"]}}}
\\github[{resume["basic_info"]["github"]}]{{https://github.com/{resume["basic_info"]["github"]}}}
{homepage}
}}
{sections[0]}

{sections[1]}

{sections[2]}

{sections[3]}

\\end{{document}}

"""
    return (RESUME, "template2" if new_template else "template")


def main(resume_name, filename=None, keywords=None, new_template=False):
    resume = find_by_resume_name(resume_name)
    if not filename:
        filename = resume_name
    RESUME, template = generate_resume_content(resume, keywords, new_template)
    filename += ".tex"
    with open(filename, "w") as output_tex:
        output_tex.write(RESUME)
    system(f"mv {filename} {template}/")
    chdir(f"{template}")
    system(f"xelatex -synctex=1 -interaction=nonstopmode {filename}")
    filename = filename.split(".")[0]
    system(f"mv {filename}.pdf ../assets")
    system(f"mv {filename}.tex ../assets")
    system(f"rm {filename}.*")
    chdir("..")


def build_resume(id, filename=None, keywords=None, new_template=False):
    resume = find_by_id(id)
    if not filename:
        filename = resume["name"]
    if not keywords:
        keywords = resume.get("keywords")
    RESUME, template = generate_resume_content(resume, keywords, new_template)
    filename += ".tex"
    with open(filename, "w") as output_tex:
        output_tex.write(RESUME)
    system(f"mv {filename} {template}/")
    chdir(f"{template}")
    system(f"xelatex -synctex=1 -interaction=nonstopmode {filename}")
    filename = filename.split(".")[0]
    system(f"mv {filename}.pdf ../assets")
    system(f"mv {filename}.tex ../assets")
    system(f"rm {filename}.*")
    chdir("..")
    return f"assets/{filename}.pdf"


if __name__ == "__main__":
    main(sys.argv[1])
