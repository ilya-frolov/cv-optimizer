import streamlit as st
import requests

API_URL = "http://cv-optimizer-api:5000/optimize"

st.set_page_config(page_title="CV Optimizer with OpenAI", layout="centered")
st.title("🧠 Format-Preserving CV Optimizer")

# --- Upload CV and Job Description---
uploaded_file = st.file_uploader("📂 Upload Your CV (.docx)", type="docx")
job_description = st.text_area("Paste Job Description", height=200)

# --- Optimize Button ---
if st.button("Optimize CV"):
    if not uploaded_file or not job_description:
        st.warning("Please upload a CV and provide a job description.")
        st.stop()

    # Prepare multipart request
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue())
    }
    data = {
        "job_description": job_description
    }

    with st.spinner("Optimizing your CV..."):
        response = requests.post(API_URL, files=files, data=data)

    if response.status_code == 200:
        st.success("✅ Optimization complete!")

        # Download button
        st.download_button(
            label="📥 Download Optimized CV (.docx)",
            data=response.content,
            file_name="optimized_cv.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("❌ Optimization failed. Please check the backend logs.")