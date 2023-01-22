from json import load
from os import chdir, system
from load_sections import load_education, load_experiences, load_projects


with open("user.json", "r") as f:
    user = load(f)


def new_section(section_name, content):
    return f"\\section{{{section_name}}}\n{content}"


education = new_section("Education", load_education(user["education"]))

experience = new_section("Experience", load_experiences(user["experiences"]))
projects = new_section("Projects", load_projects(user["projects"]))

summary = (
    f"""\\section{{Summary}}
{{{user["basic_info"].get("summary")}}}"""
    if user["basic_info"].get("summary")
    else ""
)
homepage = (
    f"\\homepage[{user['basic_info']['homepage']}]{{http://{user['basic_info']['homepage']}}}"
    if user["basic_info"].get("homepage")
    else ""
)
section1, section2, section3 = (
    projects,
    education,
    experience,
)
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
{summary}

{section1}

{section2}

{section3}

\\end{{document}}

"""

if __name__ == "__main__":
    filename = "Resume.tex"
    with open(filename, "w") as output_tex:
        output_tex.write(RESUME)
    system(f"mv {filename} template/")
    chdir("template")
    system(f"xelatex -synctex=1 -interaction=nonstopmode {filename}")
    filename = filename[:-4]
    system(f"mv {filename}.pdf ..")
    system(f"mv {filename}.tex ..")
    system(f"rm {filename}.*")
