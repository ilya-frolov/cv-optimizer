from Clients.openai_client import call_openai

prompt_template = lambda resume_string, jd_string: f"""
You are a professional resume optimization expert. Extract and rewrite only three sections from my resume to align with the provided job description:

1. **SUMMARY** - extract 'Summary'.
2. **SKILLS** - extract either 'Core Competencies' or 'Technical Skills', whichever is present. List 6–10 keyword-rich skills.
3. **EXPERIENCE** – extract 'Professional Experience'. For each role, include:
   - A header line with the role title, company, and dates (keep as-is)
   - 3–5 high-impact bullet points
   - Prefix each role with a tag like "### ROLE1", "### ROLE2", etc.

### Guidelines:
   - Focus on experiences, skills, and achievements **directly relevant** to the job description.  
   - Remove or minimize irrelevant details to keep the resume **concise and targeted**.
   - Use **strong action verbs** and emphasize **quantifiable results** (percentages, savings, efficiency gains, etc.) where possible.  
   - Naturally integrate **keywords and phrases** from the job description for ATS optimization.  
   - Format as plain text with section headers in ALL CAPS, prefixed with "##".
   - SUMMARY must be a single paragraph (no bullets).
   - SKILLS: list 6–10 keyword-rich skills with “-”.
   - EXPERIENCE: for each role include 3–5 bullet points using “-”.
   - Output must contain exactly these three sections in this order: SUMMARY, SKILLS, EXPERIENCE.
   - Do not include any other sections (Education, Certifications, etc.).
   - Keep concise and professional (max two pages).

### Input:
- My resume: {resume_string}
- The job description: {jd_string}

### Output:  
Tailored Resume:
   - Return the tailored resume in plain text with three optimized sections.
"""

def adapt_cv(cv_text: str, job_description: str) -> str:
    prompt = prompt_template(cv_text, job_description)
    raw_output = call_openai(prompt)
    return raw_output