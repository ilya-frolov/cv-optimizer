from Clients.openai_client import call_openai

prompt_template = lambda resume_string, jd_string: f"""
You are a professional resume optimization expert. Extract and rewrite only three sections from my resume to align with the provided job description:

1. **SUMMARY** - concise professional profile, goes after the contact information and before any section headers (no section title in source, but output must have "## SUMMARY").
2. **SKILLS** - extract either 'Core Competencies' or 'Technical Skills', whichever is present. List 6–10 keyword-rich skills.
3. **EXPERIENCE** — extract 'Professional Experience'. Include **2–4 most relevant roles**, each with **3–5 high-impact, results-focused** bullet points.

### Guidelines:
   - Focus on experiences, skills, and achievements **directly relevant** to the job description.  
   - Remove or minimize irrelevant details to keep the resume **concise and targeted**.
   - Use **strong action verbs** and emphasize **quantifiable results** (percentages, savings, efficiency gains, etc.) where possible.  
   - Naturally integrate **keywords and phrases** from the job description for ATS optimization.  
   - Format as plain text with section headers in ALL CAPS, prefixed with "##".
   - Use “-” for bullets.
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