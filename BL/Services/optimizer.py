from Clients.openai_client import call_openai

prompt_template = lambda resume_string, jd_string: f"""
You are a professional resume optimization expert specializing in tailoring resumes to specific job descriptions. Your task is to optimize my resume to match the job description provided.

### Guidelines:
1. Relevance:  
   - Prioritize experiences, skills, and achievements that are **directly relevant** to the job description.  
   - Remove or minimize irrelevant details to keep the resume **concise and targeted**.
   - Limit the Professional Experience section to the **2–4 most relevant roles**.
   - Limit bullet points under each role to **3-5 high-impact statements**.

2. Action-Driven Results:  
   - Use **strong action verbs** and emphasize **quantifiable results** (percentages, savings, efficiency gains, etc.).  

3. Keyword Optimization:  
   - Integrate **keywords and phrases** from the job description naturally to optimize for ATS (Applicant Tracking Systems).  

4. Formatting:  
   - Preserve the **structure, tone, and formatting** of my original resume (same sections, order, and style).
   - Output only the **resume text itself**. Do not include notes, explanations, or additional commentary.
   - Ensure the final resume does not exceed **two pages**.

---

### Input:
- My resume:  
{resume_string}

- The job description:  
{jd_string}

---

### Output:  
Tailored Resume:  
   - A version of my resume in the **same format as the original** but rewritten to emphasize relevance to the job description. 
   - Uses **concise, action-driven language** with measurable impact where possible.  
   - Optimized for **ATS** while remaining professional and readable.
"""

def adapt_cv(cv_text: str, job_description: str) -> str:
    prompt = prompt_template(cv_text, job_description)
    raw_output = call_openai(prompt)

    # Remove trailing GPT commentary if present
    cutoff_phrases = [
        "This resume was tailored", 
        "Structured to highlight", 
        "Optimized for ATS", 
        "This version emphasizes"
    ]

    for phrase in cutoff_phrases:
        if phrase in raw_output:
            raw_output = raw_output.split(phrase)[0].strip()
            break

    return raw_output