from bs4 import BeautifulSoup
from docx import Document

def extract_cv_text(path: str) -> str:
    doc = Document(path)
    
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def parse_gpt_resume(text: str) -> dict:
    sections = {"summary": [], "skills": [], "experience": {}}
    current = None
    current_role = None

    for line in text.splitlines():
        line = line.strip()
        if line.upper() == "## SUMMARY":
            current = "summary"
        elif line.upper() == "## SKILLS":
            current = "skills"
        elif line.upper() == "## EXPERIENCE":
            current = "experience"
        elif current == "experience" and line.startswith("### ROLE"):
            current_role = line
            sections["experience"][current_role] = []
        elif current == "experience" and current_role and line.startswith("-"):
            sections["experience"][current_role].append(line)
        elif current and current != "experience" and line:
            sections[current].append(line)

    return sections

def clean_section(section, section_type="generic"):
    if isinstance(section, list):
        output = ""
        for i, line in enumerate(section):
            style_class = "MsoListParagraphCxSpMiddle"
            if i == 0:
                style_class = "MsoListParagraphCxSpFirst"
            elif i == len(section) - 1:
                style_class = "MsoListParagraphCxSpLast"

            output += f"""
                            <p class="{style_class}" style='margin-left:49.65pt;text-indent:-14.2pt;line-height:normal'>
                            <span lang="EN-US" style='font-size:11.0pt;font-family:Symbol'>
                                <span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
                            </span>
                            <span lang="EN-US" style='font-size:11.0pt;font-family:"Arial",sans-serif'>
                                {line.strip()}
                            </span>
                            </p>
                            """
        return output.strip()

    # For summary or other single-paragraph sections
    return section.strip()  # summary: plain text only

def format_experience_bullets(bullets: list) -> str:
    output = ""
    for i, line in enumerate(bullets):
        style_class = "MsoListParagraphCxSpMiddle"
        if i == 0:
            style_class = "MsoListParagraphCxSpFirst"
        elif i == len(bullets) - 1:
            style_class = "MsoListParagraphCxSpLast"

        output += f"""
<p class="{style_class}" style='margin-left:1.0cm;text-align:justify;text-indent:-14.2pt;line-height:normal'>
  <span lang="EN-US" style='font-size:11.0pt;font-family:Symbol'>
    <span style='font:7.0pt "Times New Roman"'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
  </span>
  <span lang="EN-US" style='font-size:11.0pt;font-family:"Arial",sans-serif'>
    {line.strip()}
  </span>
</p>
"""
    return output.strip()