from bs4 import BeautifulSoup

def inject_into_html(html: str, new_text: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Replace content inside a known section (e.g., experience)
    target = soup.find("h2", string="PROFESSIONAL EXPERIENCE")
    if target:
        next_sibling = target.find_next_sibling()
        if next_sibling:
            next_sibling.string = new_text

    return str(soup)

def parse_gpt_resume(text: str) -> dict:
    sections = {"summary": [], "skills": [], "experience": []}
    current = None

    for line in text.splitlines():
        line = line.strip()
        if line.upper() == "## SUMMARY":
            current = "summary"
        elif line.upper() == "## SKILLS":
            current = "skills"
        elif line.upper() == "## EXPERIENCE":
            current = "experience"
        elif current and line:
            sections[current].append(line)

    return sections