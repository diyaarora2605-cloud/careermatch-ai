import streamlit as st

def _get_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return ""

def generate_ai_insights(resume_text, profile, mode="resume"):
    api_key = _get_api_key()
    if not api_key:
        return ("### AI provider not configured\n"
                "Groq is optional. Add `GROQ_API_KEY` in Streamlit Secrets to enable generated narrative insights. "
                "The resume extraction, match scores, filters and recommendations continue to work without it.")
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        if mode == "career":
            instruction = ("Act as a practical career coach. Give concise, evidence-based role suggestions, "
                           "resume and LinkedIn improvements, project ideas and interview preparation. "
                           "Do not invent qualifications or claim a job is live.")
        else:
            instruction = ("Review this resume as a recruiter. Identify strengths, missing evidence, weak sections, "
                           "and 5 concrete improvements. Do not invent facts or infer sensitive traits.")
        prompt = f"{instruction}\n\nDetected profile: {profile}\n\nResume text:\n{resume_text[:9000]}"
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            temperature=0.35,
            max_tokens=1100
        )
        return response.choices[0].message.content or "No AI response was returned."
    except Exception as exc:
        return f"AI insights could not be generated: {exc}. Core CareerMatch features remain available."
