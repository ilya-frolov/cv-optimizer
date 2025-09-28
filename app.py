import streamlit as st
import openai
import docx

# Set your OpenAI API key
openai.api_key = "your-api-key-here"

# Function to extract text from a Word document
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to optimize CV using OpenAI
def optimize_cv(cv_text):
    prompt = f"Improve this CV for a software engineering role:\n\n{cv_text}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Streamlit UI
st.title("🧠 CV Optimizer with OpenAI")
uploaded_file = st.file_uploader("Upload your CV (.docx)", type="docx")

if uploaded_file:
    cv_text = extract_text_from_docx(uploaded_file)
    st.subheader("📄 Original CV Text")
    st.text(cv_text)

    if st.button("Optimize CV"):
        optimized = optimize_cv(cv_text)
        st.subheader("🚀 Optimized CV")
        st.text(optimized)