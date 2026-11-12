import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _split_skills(value):
    return {x.strip().lower() for x in re.split(r"[,;|]", str(value or "")) if x.strip()}

def _normalise_set(values):
    return {str(x).strip().lower() for x in (values or []) if str(x).strip()}

def _experience_score(candidate_text, level):
    text = candidate_text.lower()
    years = [int(x) for x in re.findall(r"(\d+)\+?\s+years?", text)]
    max_years = max(years) if years else (1 if re.search(r"\b(intern|internship|fresher|graduate)\b", text) else 0)
    expected = {"internship":0,"entry-level":0,"mid-level":2,"senior":5}.get(str(level).lower(), 0)
    if expected == 0:
        return 100.0 if max_years <= 2 else 80.0
    return min(100.0, max(0.0, (max_years / expected) * 100))

def _education_score(profile, job):
    text = (str(job.get("education","")) + " " + str(job.get("description",""))).lower()
    if not text.strip():
        return 75.0
    education = " ".join(profile.get("education", [])).lower()
    if not education:
        return 30.0
    degree_terms = ["bachelor","b.tech","btech","b.sc","bsc","master","m.tech","mba","diploma","graduate"]
    req = [t for t in degree_terms if t in text]
    if not req:
        return 80.0
    return 100.0 if any(t in education for t in req) else 45.0

def _role_score(resume_text, job):
    corpus = [resume_text[:12000], f"{job.get('title','')} {job.get('description','')} {job.get('responsibilities','')}"]
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1,2), max_features=5000).fit_transform(corpus)
        sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        sim = 0.0
    return min(100.0, sim * 100.0)

def match_jobs(resume_text, profile, jobs, preferences=None):
    preferences = preferences or {}
    candidate_skills = _normalise_set(profile.get("technical_skills", []) + profile.get("soft_skills", []))
    rows = []
    for _, job in jobs.iterrows():
        required = _split_skills(job.get("skills",""))
        overlap = candidate_skills & required
        missing = required - candidate_skills
        skills_score = (len(overlap) / max(1, len(required))) * 100
        experience_score = _experience_score(resume_text, job.get("experience_level","Entry-level"))
        education_score = _education_score(profile, job)
        role_score = _role_score(resume_text, job)
        preference_score = 100.0
        preferred_location = str(preferences.get("location","")).strip().lower()
        if preferred_location:
            loc = str(job.get("location","")).lower()
            preference_score = 100.0 if preferred_location in loc or "remote" in loc else 35.0
        preferred_mode = preferences.get("work_mode","Any")
        if preferred_mode and preferred_mode != "Any":
            preference_score = (preference_score + (100 if str(job.get("work_mode","")).lower() == preferred_mode.lower() else 35)) / 2
        preferred_level = preferences.get("experience","Any")
        if preferred_level and preferred_level != "Any":
            preference_score = (preference_score + (100 if str(job.get("experience_level","")).lower() == preferred_level.lower() else 45)) / 2
        score = (skills_score*.40 + experience_score*.20 + education_score*.15 +
                 role_score*.15 + preference_score*.10)
        why = (f"Your profile shares {len(overlap)} of {len(required)} listed skills with this role. "
               f"The text relevance score is {role_score:.0f}/100; experience and education signals are also included.")
        row = job.to_dict()
        row.update({"match_score": round(float(np.clip(score,0,100)),1),
                    "skills_score": skills_score, "experience_score": experience_score,
                    "education_score": education_score, "role_score": role_score,
                    "preference_score": preference_score, "matching_skills": sorted(overlap),
                    "missing_skills": sorted(missing), "why_suitable": why})
        rows.append(row)
    return __import__("pandas").DataFrame(rows).sort_values("match_score", ascending=False).reset_index(drop=True)

def filter_jobs(jobs, title="", company="", location="", work_mode="Any",
                experience="Any", employment_type="Any", skills=""):
    df = jobs.copy()
    for col, query in [("title",title),("company",company),("location",location)]:
        if query:
            df = df[df[col].astype(str).str.contains(query, case=False, na=False, regex=False)]
    if work_mode != "Any": df = df[df.work_mode == work_mode]
    if experience != "Any": df = df[df.experience_level == experience]
    if employment_type != "Any": df = df[df.employment_type == employment_type]
    if skills:
        terms = [x.strip().lower() for x in skills.split(",") if x.strip()]
        df = df[df.skills.astype(str).apply(lambda s: all(t in s.lower() for t in terms))]
    return df.reset_index(drop=True)
