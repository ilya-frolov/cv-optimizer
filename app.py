import streamlit as st
import os
import json
import io
from BL.Services.optimizer import adapt_cv
from Models.cv_model import extract_cv_text
from Utils.formatter import text_to_docx

# --- Constants ---
PATH_STORE = "cv_paths.json"
TEMP_DIR = "temp"

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
st.title("🧠 CV Optimizer")

# --- File Picker ---
uploaded_file = st.file_uploader("📂 Open Sample CV (.docx)", type="docx")

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
        cv_text = extract_cv_text(cv_path)
        optimized_text = adapt_cv(cv_text, job_description)
        st.subheader("🚀 Optimized CV")
        st.text_area("Result", optimized_text, height=300)

        # --- Download Button ---
        doc = text_to_docx(optimized_text)
        buffer = io.BytesIO()
        doc.save(buffer)
        st.download_button(
            label="📥 Download Optimized CV (.docx)",
            data=buffer.getvalue(),
            file_name="optimized_cv.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.text_area("Raw GPT Output", optimized_text, height=300)
    else:
        st.warning("Missing CV path or job description.")