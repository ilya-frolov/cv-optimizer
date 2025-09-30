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