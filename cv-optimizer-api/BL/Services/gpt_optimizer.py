from Clients.openai_client import call_openai

prompt_template = lambda resume_string, jd_string: f"""
You are a professional resume optimization expert. Extract and rewrite only three sections from my resume to align with the provided job description:

1. **SUMMARY** - extract and rewrite 'Summary'.
2. **SKILLS** - extract and rewrite either 'Core Competencies' or 'Technical Skills', whichever is present.
   - Organize the skills into into 3-6 thematic groups with short headers (e.g., "Machine Learning & AI", "Programming & Frameworks", "Simulation & Visualization", etc.).
   - Do not use any Markdown or formatting symbols (like *, _, or ) — plain text only.
   - Within each group, include 3-6 concise, keyword-rich skills separated by commas.
   - Reflect both technical breadth and research depth, not just single keywords if section is called 'Core Competencies'.
3. **EXPERIENCE** – extract 'Professional Experience'. For each role, include:
   - A header line with the role title, company, , and dates **exactly as in the original resume**.
   - 3–5 concise, high-impact bullet points emphasizing results, metrics, or technical relevance to the job description.
   - Prefix each role with a tag like "### ROLE1", "### ROLE2", etc.

### Guidelines:
   - Focus on experiences, skills, and achievements **directly relevant** to the job description.  
   - Remove or minimize irrelevant details to keep the resume **concise and targeted**.
   - Use **strong action verbs** and emphasize **quantifiable results** (percentages, savings, efficiency gains, etc.) where possible.  
   - Naturally integrate **keywords and phrases** from the job description for ATS optimization.  
   - Format as plain text with section headers in ALL CAPS, prefixed with "##".
   - SUMMARY must be a single paragraph (no bullets).
   - SKILLS: list skills thematic groups with “-”, and place inside keyword-rich skills separated by commas inside "()" for each group.
   - EXPERIENCE: for each role list bullet points using “-”.
   - Do not modify the role header lines (title, company, dates) — they must remain **verbatim** for downstream injection.
   - Output must contain exactly these three sections in this order: SUMMARY, SKILLS, EXPERIENCE.
   - Do not include any other sections (Education, Certifications, etc.).

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