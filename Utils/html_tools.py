import subprocess
import shutil

pandoc_path = shutil.which("pandoc") or r"C:\Program Files\Pandoc\pandoc.exe"

def docx_to_html_with_styles(docx_path: str, html_path: str):
    subprocess.run([
        pandoc_path,
        docx_path,
        "-f", "docx",
        "-t", "html",
        "-s",  # standalone HTML
        "-o", html_path
    ])
    
def html_to_docx(html_path: str, output_path: str):
    subprocess.run([pandoc_path, html_path, "-o", output_path])
