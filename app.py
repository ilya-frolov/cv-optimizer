import streamlit as st
import os
import json

from BL.Services.optimizer import adapt_cv
from Utils.formatter import clean_section, parse_gpt_resume
from Utils.html_tools import (
    html_to_docx,
    inject_sections
)

# --- Constants ---
PATH_STORE = "cv_paths.json"
TEMP_DIR = "temp"
TEMPLATE_PATH = "templates/cv_template_Scientist.htm"  # Your Word-exported .htm file
OUTPUT_HTML_PATH = os.path.join(TEMP_DIR, "output.html")
DOCX_OUTPUT_NAME = "optimized_cv.docx"
DOCX_OUTPUT_PATH = os.path.join(TEMP_DIR, DOCX_OUTPUT_NAME)

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

# --- Optimize CV ---
if st.button("Optimize CV"):
    if cv_path and job_description:
        # Step 1: Load HTML template
        if not os.path.exists(TEMPLATE_PATH):
            st.error("Missing cv_template.htm in templates folder.")
            st.stop()

        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template_html = f.read()

        st.subheader("📄 Original CV Template Preview")
        st.components.v1.html(template_html, height=800, scrolling=True)

        # Step 2: Send template + job description to GPT
        optimized_text = adapt_cv(template_html, job_description)

        try:
            parsed_sections = parse_gpt_resume(optimized_text)
        except Exception as e:
            st.error("Failed to parse GPT output. Please check formatting.")
            st.stop()

        # Clean parsed sections: convert lists to strings
        parsed_sections = {
            key: clean_section(value)
            for key, value in parsed_sections.items()
        }

        # ensure keys are lowercase: 'summary', 'skills', 'experience'
        parsed_sections = { k.lower(): v for k, v in parsed_sections.items() }

        # Step 3: Inject GPT output into template
        injected_html = inject_sections(template_html, parsed_sections, verbose=True)

        # Step 4: Save updated HTML to file
        with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(injected_html)

        # Step 5: Show updated HTML
        st.subheader("📄 Updated CV Preview")
        st.components.v1.html(injected_html, height=800, scrolling=True)

        # Step 6: Convert HTML to .docx using Pandoc
        html_to_docx(OUTPUT_HTML_PATH, DOCX_OUTPUT_PATH)

        # Step 7: Show result and download
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