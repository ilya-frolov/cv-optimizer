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

def inject_by_data_tag(template_html: str, sections: dict, verbose=False) -> str:
    soup = BeautifulSoup(template_html, "html.parser")

    for key, html_fragment in sections.items():
        target = soup.find(attrs={"data-inject": key})
        if not target:
            if verbose:
                print(f"❌ No data-inject target for: {key}")
            continue

        # Clear and inject
        target.clear()
        fragment = BeautifulSoup(html_fragment, "html.parser")
        for node in fragment.contents:
            target.append(node)

        if verbose:
            print(f"✅ Injected: {key}")

    return str(soup)