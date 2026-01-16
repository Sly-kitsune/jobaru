from .ollama_client import generate_json

def analyze_job_fit(resume_text, job_description, model):
    """
    Analyzes how well the resume matches the job description.
    Returns extracted skills and a fit score.
    """
    prompt = f"""
    You are an expert career coach and recruiter.
    
    1. Analyze the RESUME and JOB DESCRIPTION below.
    2. Extract key skills from the resume that match the job.
    3. Identify missing skills.
    4. Provide a match score (0-100).
    
    RESUME:
    {resume_text[:4000]}
    
    JOB DESCRIPTION:
    {job_description[:4000]}
    
    Output JSON format:
    {{
        "match_score": 85,
        "matched_skills": ["Python", "AWS"],
        "missing_skills": ["Docker"],
        "analysis": "Brief analysis of fit..."
    }}
    """
    return generate_json(prompt, model=model)

def generate_application_materials(resume_text, job_description, fit_analysis, model):
    """
    Generates a cover letter and email based on the fit analysis.
    """
    prompt = f"""
    You are a professional copywriter for job applications.
    
    Using the RESUME and JOB DESCRIPTION provided, write a compelling Cover Letter and an Introduction Email.
    Highlight the matched skills: {fit_analysis.get('matched_skills', [])}.
    Address the missing skills if possible by emphasizing adaptability or related experience.
    
    RESUME:
    {resume_text[:4000]}
    
    JOB DESCRIPTION:
    {job_description[:4000]}
    
    Output JSON format:
    {{
        "cover_letter": "Dear Hiring Manager...",
        "intro_email": "Subject: Application for [Role]... Body: ..."
    }}
    """
    result = generate_json(prompt, model=model)
    
    # Sanitization to ensure string outputs
    if isinstance(result, dict):
        # Sanitize cover_letter
        cl = result.get("cover_letter")
        if isinstance(cl, dict):
             result["cover_letter"] = cl.get("text") or cl.get("body") or str(cl)
        elif not isinstance(cl, str):
             result["cover_letter"] = str(cl) if cl else ""

        # Sanitize intro_email
        email = result.get("intro_email")
        if isinstance(email, dict):
             result["intro_email"] = email.get("text") or email.get("body") or str(email)
        elif not isinstance(email, str):
             result["intro_email"] = str(email) if email else ""

    return result

def process_job_application(resume_text, job_description, model="llama3"):
    """
    Orchestrates the full application process.
    """
    print("  - Analyzing fit...")
    analysis = analyze_job_fit(resume_text, job_description, model)
    
    if "error" in analysis:
        return {"error": "Analysis failed", "details": analysis}

    print("  - Drafting application materials...")
    materials = generate_application_materials(resume_text, job_description, analysis, model)
    
    if "error" in materials:
        return {"error": "Generation failed", "details": materials}
        
    return {
        "status": "ready",
        "analysis": analysis,
        "materials": materials
    }

def suggest_roles_from_resume(resume_text, model="mistral"):
    """
    Analyzes the resume and suggests top 3 job titles.
    """
    prompt = f"""
    You are an expert career consultant.
    Analyze the RESUME provided below and list the top 3 most suitable job titles this candidate should apply for.
    Rules:
    - Provide ONLY the job titles as a comma-separated list.
    - Be specific (e.g., "Senior Python Developer" instead of just "Developer").
    - Do not output any other text or explanation.

    RESUME:
    {resume_text[:4000]}
    """
    
    # We use generate_json generically but here we just want text.
    # However, our ollama_client returns JSON usually.
    # Let's use a simpler prompt wrapper or just parse the "response" key if using raw endpoint?
    # Our extract_json checks for json blocks. Let's ask for JSON to be safe.
    
    json_prompt = f"""
    Analyze the RESUME and suggest 3 job titles.
    Output JSON format:
    {{
        "roles": ["Role 1", "Role 2", "Role 3"]
    }}
    
    RESUME:
    {resume_text[:4000]}
    """
    result = generate_json(json_prompt, model=model)
    if isinstance(result, dict) and "roles" in result:
        return result["roles"]
    return ["Python Developer"] # Fallback
