import streamlit as st
import os
import json
import io
import subprocess
import shutil

from bs4 import BeautifulSoup
from BL.Services.optimizer import adapt_cv
from Utils.html_tools import docx_to_html_with_styles, html_to_docx

# --- Constants ---
PATH_STORE = "cv_paths.json"
TEMP_DIR = "temp"
OUTPUT_HTML_PATH = os.path.join(TEMP_DIR, "output.html")
DOCX_OUTPUT_NAME = "optimized_cv.docx"
DOCX_OUTPUT_PATH = os.path.join(TEMP_DIR, "optimized_cv.docx")

# --- Load stored paths ---
def load_paths():
    if os.path.exists(PATH_STORE):
        with open(PATH_STORE, "r") as f:
            return json.load(f)
    return {"last_used": None, "history": []}

def save_paths(data):
    with open(PATH_STORE, "w") as f:
        json.dump(data, f, indent=2)

# --- Setup ---
os.makedirs(TEMP_DIR, exist_ok=True)
paths_data = load_paths()
cv_history = paths_data["history"]
last_used = paths_data["last_used"]
cv_path = None

# --- UI ---
st.set_page_config(page_title="CV Optimizer with OpenAI", layout="centered")
st.title("🧠 Format-Preserving CV Optimizer")

# --- File Picker ---
uploaded_file = st.file_uploader("📂 Upload Your CV (.docx)", type="docx")

if uploaded_file:
    temp_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if temp_path not in cv_history:
        cv_history.insert(0, temp_path)
    paths_data["last_used"] = temp_path
    paths_data["history"] = cv_history[:10]
    save_paths(paths_data)

    st.success(f"Sample CV loaded: {uploaded_file.name}")
    cv_path = temp_path

# --- Dropdown for previous paths ---
selected_path = st.selectbox("Choose a previously used CV path", options=[""] + cv_history)

if not uploaded_file and selected_path:
    if os.path.exists(selected_path):
        cv_path = selected_path
        st.info(f"Using stored CV path: {selected_path}")
    else:
        st.error("Stored path is invalid or file no longer exists.")

# --- Fallback to last used path ---
if not uploaded_file and not selected_path and last_used:
    if os.path.exists(last_used):
        cv_path = last_used
        st.info(f"Using last used CV path: {last_used}")
    else:
        st.error("Last used path is invalid or missing.")

# --- Job Description ---
job_description = st.text_area("Paste Job Description", height=200)

# --- Optimize Button ---
if st.button("Optimize CV"):
    if cv_path and job_description:
        # Step 1: Convert .docx to HTML
        input_html_path = os.path.join(TEMP_DIR, "input.html")
        docx_to_html_with_styles(cv_path, input_html_path)

        # Show original HTML
        with open(input_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        st.subheader("📄 Original CV Preview")
        st.components.v1.html(html, height=800, scrolling=True)

        # Step 2: Send raw resume to GPT
        optimized_text = adapt_cv(html, job_description)

        # Step 3: Inject GPT output into HTML
        soup = BeautifulSoup(html, "html.parser")
        target = soup.find("body")
        if target:
            target.clear()
            for line in optimized_text.split("\n"):
                if line.strip():
                    tag = soup.new_tag("p")
                    tag.string = line.strip()
                    target.append(tag)

        updated_html = str(soup)

        # Step 4: Save HTML to file
        with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(updated_html)


        # Show updated HTML
        st.subheader("📄 Updated CV Preview")
        st.components.v1.html(updated_html, height=800, scrolling=True)


        # Step 5: Convert HTML to .docx using Pandoc
        #pandoc_path = shutil.which("pandoc") or r"C:\Program Files\Pandoc\pandoc.exe"
        #subprocess.run([pandoc_path, OUTPUT_HTML_PATH, "-o", DOCX_OUTPUT])
        html_to_docx(OUTPUT_HTML_PATH, DOCX_OUTPUT_PATH)

        # Step 6: Show result and download
        st.subheader("🚀 Optimized CV Preview")
        st.text_area("Optimized Text", optimized_text, height=300)

        with open(DOCX_OUTPUT_PATH, "rb") as f:
            st.download_button(
                label="📥 Download Optimized CV (.docx)",
                data=f.read(),
                file_name=DOCX_OUTPUT_NAME,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Missing CV path or job description.")