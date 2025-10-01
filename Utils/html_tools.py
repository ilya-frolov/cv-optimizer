import re
import subprocess
import shutil
from bs4 import BeautifulSoup, Comment

pandoc_path = shutil.which("pandoc") or r"C:\Program Files\Pandoc\pandoc.exe"

def docx_to_html_with_styles(docx_path: str, html_path: str):
    try:
        subprocess.run([
            pandoc_path,
            docx_path,
            "-f", "docx",
            "-t", "html",
            "-s",  # standalone HTML
            "-o", html_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Pandoc failed to convert DOCX to HTML: {e}")

def html_to_docx(html_path: str, output_path: str):
    try:
        subprocess.run([pandoc_path, html_path, "-o", output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Pandoc failed to convert HTML to DOCX: {e}")

def tag_sections(html: str, verbose=False) -> str:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body")
    if not body:
        return html

    # Step 1: Wrap first 3 <p> tags as contact
    contact_div = soup.new_tag("div", id="contact")
    contact_tags = body.find_all("p", limit=3)
    for tag in contact_tags:
        contact_div.append(tag.extract())
    body.insert(0, contact_div)
    if verbose:
        print("✅ Tagged contact section")

    # Step 2: Wrap first <ul> as summary
    first_ul = body.find("ul")
    if first_ul:
        summary_div = soup.new_tag("div", id="summary")
        summary_div.append(first_ul.extract())
        body.insert(1, summary_div)
        if verbose:
            print("✅ Tagged summary section")

    # Step 3: Tag skills section
    skills_header = body.find(lambda tag: tag.name == "p" and "CORE COMPETENCIES" in tag.get_text(strip=True).upper())
    experience_header = body.find(lambda tag: tag.name == "p" and "PROFESSIONAL EXPERIENCE" in tag.get_text(strip=True).upper())

    if skills_header and experience_header:
        skills_div = soup.new_tag("div", id="skills")
        next_sibling = skills_header.find_next_sibling()
        while next_sibling and next_sibling != experience_header:
            skills_div.append(next_sibling.extract())
            next_sibling = skills_header.find_next_sibling()
        skills_header.insert_after(skills_div)
        if verbose:
            print("✅ Tagged skills section")

    # Step 4: Tag experience section
    if experience_header:
        experience_div = soup.new_tag("div", id="experience")
        next_sibling = experience_header.find_next_sibling()
        while next_sibling:
            experience_div.append(next_sibling.extract())
            next_sibling = experience_header.find_next_sibling()
        experience_header.insert_after(experience_div)
        if verbose:
            print("✅ Tagged experience section")

    # Step 5: Wrap remaining content as footer
    footer_div = soup.new_tag("div", id="footer")
    for el in list(body.children):
        if el.name != "div":
            footer_div.append(el.extract())
    body.append(footer_div)
    if verbose:
        print("✅ Tagged footer section")

    return str(soup)

def inject_section(soup, section_id, lines, header_text=None, verbose=False):
    target = soup.find(id=section_id)
    if not target:
        if verbose:
            print(f"⚠️ Section '{section_id}' not found.")
        return

    target.clear()

    # Optional header
    if header_text:
        header_tag = soup.new_tag("p")
        strong = soup.new_tag("strong")
        strong.string = header_text
        header_tag.append(strong)
        target.append(header_tag)

    # Format content
    if all(line.startswith("-") for line in lines):
        ul = soup.new_tag("ul")
        for line in lines:
            li = soup.new_tag("li")
            li.string = line.lstrip("- ").strip()
            ul.append(li)
        target.append(ul)
    else:
        for line in lines:
            p = soup.new_tag("p")
            p.string = line.strip()
            target.append(p)

    if verbose:
        print(f"✅ Injected '{section_id}' with header '{header_text}'")

def wrap_html(body_content: str, title="Optimized CV") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
{body_content}
</body>
</html>"""

def inject_sections(template_html: str, sections: dict, verbose=False) -> str:
    """
    sections: a dict with keys 'summary', 'skills', 'experience', each
    value is an HTML string (e.g. '<ul><li>…</li></ul>')
    """
    soup = BeautifulSoup(template_html, "html.parser")

    for key, html_fragment in sections.items():
        placeholder = soup.find("div", id=key)
        if not placeholder:
            if verbose:
                print(f"❌ No <div id='{key}'> found.")
            continue

        # Clear out old children
        placeholder.clear()

        # Parse the new snippet and append its nodes
        frag_soup = BeautifulSoup(html_fragment, "html.parser")
        for node in frag_soup.contents:
            placeholder.append(node)

        if verbose:
            print(f"✅ Replaced content in #{key}")

    return str(soup)