from pathlib import Path
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.resume_parser import extract_resume_text, analyze_resume
from utils.job_matcher import match_jobs, filter_jobs
from utils.skill_analyzer import analyze_skill_gaps
from utils.recommendations import build_career_recommendations
from utils.ai_engine import generate_ai_insights

st.set_page_config(page_title="CareerMatch AI", page_icon="🎯", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:linear-gradient(135deg,#f7f8fc 0%,#f1f2fa 100%);}
.block-container {padding-top:1.6rem; padding-bottom:3rem; max-width:1400px;}
[data-testid="stSidebar"] {background:#10152f;}
[data-testid="stSidebar"] * {color:#f5f6ff;}
.hero {padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(115deg,#111936,#34266e 65%,#6945a8);color:white;margin-bottom:1.2rem;}
.hero h1 {font-family:Manrope,sans-serif;font-size:2.35rem;margin:0 0 .3rem 0;}
.hero p {color:#e2ddff;margin:0;font-size:1.02rem;}
.eyebrow {text-transform:uppercase;letter-spacing:2px;font-size:.72rem;color:#c9bdff;font-weight:700;}
.metric {background:white;border:1px solid #e9eaf3;border-radius:16px;padding:1.1rem 1.25rem;box-shadow:0 5px 18px rgba(25,30,70,.04);}
.metric-label {color:#6e7288;font-size:.83rem;}
.metric-value {font-family:Manrope,sans-serif;color:#171c3b;font-size:1.8rem;font-weight:800;}
.job-card {background:white;border:1px solid #e7e8f1;border-radius:16px;padding:1.1rem 1.2rem;margin:.55rem 0;}
.muted {color:#73778c;font-size:.88rem;}
.pill {display:inline-block;background:#f0edff;color:#5c43a5;padding:4px 9px;border-radius:20px;font-size:.75rem;margin:2px;}
.small-title {font-family:Manrope,sans-serif;color:#171c3b;font-size:1.15rem;font-weight:800;}
div[data-testid="stMetric"] {background:white;border:1px solid #e9eaf3;padding:14px;border-radius:14px;}
.stButton>button {border-radius:10px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_jobs():
    path = ROOT / "data" / "sample_jobs.csv"
    df = pd.read_csv(path).fillna("")
    for col in ["skills", "responsibilities"]:
        if col in df:
            df[col] = df[col].astype(str)
    return df

jobs = load_jobs()

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><div class="eyebrow">CAREERMATCH AI</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="muted">{note}</div></div>', unsafe_allow_html=True)

def ensure_state():
    defaults = {"resume_text": "", "resume_name": "", "analysis": None, "matches": None,
                "preferences": {"location": "", "work_mode": "Any", "experience": "Any"}}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
ensure_state()

with st.sidebar:
    st.markdown("## 🎯 CareerMatch AI")
    st.caption("Find the right job. Match your potential.")
    page = st.radio("NAVIGATION", ["Home Dashboard", "Upload Resume", "Resume Analysis",
                                  "Find Jobs", "Job Matches", "Skill Gap Analysis",
                                  "Career Recommendations"], label_visibility="collapsed")
    st.divider()
    st.caption("Your resume stays in this app session. Sample jobs are illustrative, not live vacancies.")
    if st.button("↻ Reset session", use_container_width=True):
        for key in ["resume_text", "resume_name", "analysis", "matches"]:
            st.session_state[key] = None if key in ["analysis", "matches"] else ""
        st.rerun()

if page == "Home Dashboard":
    hero("Find work that fits your potential.", "An intelligent starting point for your next career move.")
    a,b,c,d = st.columns(4)
    total = len(jobs)
    suitable = len(st.session_state.matches) if st.session_state.matches is not None else 0
    best = int(st.session_state.matches.iloc[0]["match_score"]) if suitable else 0
    with a: metric_card("Sample opportunities", total, "Illustrative dataset")
    with b: metric_card("Suitable matches", suitable, "Based on your latest resume")
    with c: metric_card("Best match", f"{best}%" if suitable else "—", "Calculated score")
    with d: metric_card("Resume status", "Ready" if st.session_state.resume_text else "Not uploaded",
                        st.session_state.resume_name or "Upload a PDF or DOCX")
    st.markdown("### Get started")
    x,y = st.columns([1.1,1])
    with x:
        st.markdown("#### 1. Add your resume")
        st.write("Upload a PDF or DOCX file. CareerMatch extracts skills, education, experience and projects.")
        if st.button("Upload resume →", type="primary"):
            st.session_state.nav_target = "Upload Resume"
            st.session_state["page_hint"] = "Upload Resume"
            st.info("Choose **Upload Resume** in the sidebar to continue.")
    with y:
        st.markdown("#### 2. Explore your matches")
        st.write("Compare your profile with the sample job dataset and understand what to improve.")
        if st.button("View job matches →"):
            st.info("Choose **Job Matches** in the sidebar.")
    st.markdown("### Opportunity overview")
    chart_left, chart_right = st.columns(2)
    with chart_left:
        mode_counts = jobs["work_mode"].value_counts().rename_axis("Work mode").reset_index(name="Jobs")
        fig_modes = px.bar(mode_counts, x="Work mode", y="Jobs", title="Sample jobs by work mode")
        st.plotly_chart(fig_modes, use_container_width=True)
    with chart_right:
        if st.session_state.matches is not None and not st.session_state.matches.empty:
            chart_data = st.session_state.matches.head(8).sort_values("match_score", ascending=True)
            fig_scores = px.bar(chart_data, x="match_score", y="title", orientation="h",
                                title="Your top calculated matches", labels={"match_score":"Match score (%)","title":"Role"},
                                range_x=[0,100])
            st.plotly_chart(fig_scores, use_container_width=True)
        else:
            exp_counts = jobs["experience_level"].value_counts().rename_axis("Experience level").reset_index(name="Jobs")
            fig_levels = px.pie(exp_counts, names="Experience level", values="Jobs", hole=.55,
                                title="Sample jobs by experience level")
            st.plotly_chart(fig_levels, use_container_width=True)
    st.markdown("### What you can do")
    cols = st.columns(3)
    for col, title, desc in zip(cols, ["Resume insights", "Skill gap analysis", "Career direction"],
                                ["Spot strengths and weak sections.", "Prioritize skills to close the gap.", "Explore roles, projects and interview topics."]):
        with col:
            st.markdown(f'<div class="metric"><div class="small-title">{title}</div><p class="muted">{desc}</p></div>', unsafe_allow_html=True)
    st.caption("Privacy note: this app does not save resumes to a database. Data is held in the current Streamlit session.")

elif page == "Upload Resume":
    hero("Upload your resume", "Start with your latest resume to get a personalized profile and job matches.")
    uploaded = st.file_uploader("Choose a resume", type=["pdf","docx"], help="Maximum recommended size: 10 MB.")
    if uploaded:
        if uploaded.size > 10 * 1024 * 1024:
            st.error("This file is larger than 10 MB. Please upload a smaller resume.")
        elif st.button("Analyze my resume", type="primary"):
            with st.spinner("Reading and analyzing your resume..."):
                try:
                    raw = extract_resume_text(uploaded.getvalue(), uploaded.name)
                    if len(raw.strip()) < 40:
                        st.error("Very little text was found. If this is a scanned PDF, use an OCR-enabled PDF or upload a DOCX.")
                    else:
                        profile = analyze_resume(raw)
                        st.session_state.resume_text = raw
                        st.session_state.resume_name = uploaded.name
                        st.session_state.analysis = profile
                        st.session_state.matches = match_jobs(raw, profile, jobs, st.session_state.preferences)
                        st.success("Resume analyzed successfully.")
                        st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    st.error(f"Could not analyze this file: {exc}")
    st.info("Supported formats: PDF and DOCX. Password-protected PDFs and image-only scans may not be readable.")

elif page == "Resume Analysis":
    hero("Resume analysis", "A structured snapshot of your experience, skills and resume completeness.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first from **Upload Resume**.")
    else:
        p = st.session_state.analysis or analyze_resume(st.session_state.resume_text)
        st.caption(f"Analyzed file: {st.session_state.resume_name}")
        c1,c2,c3 = st.columns(3)
        with c1: metric_card("Skills detected", len(p["technical_skills"]) + len(p["soft_skills"]), "Technical + soft skills")
        with c2: metric_card("Education entries", len(p["education"]), "Detected from resume text")
        with c3: metric_card("Experience signals", len(p["experience"]), "Roles / experience snippets")
        left,right = st.columns(2)
        with left:
            st.markdown("### Technical skills")
            st.write(", ".join(p["technical_skills"]) or "No clear technical skills detected.")
            st.markdown("### Programming languages")
            st.write(", ".join(p["programming_languages"]) or "Not clearly detected.")
            st.markdown("### Tools & technologies")
            st.write(", ".join(p["tools"]) or "Not clearly detected.")
            st.markdown("### Soft skills")
            st.write(", ".join(p["soft_skills"]) or "Not clearly detected.")
        with right:
            st.markdown("### Education")
            for item in p["education"]: st.write("• " + item)
            if not p["education"]: st.write("No education entry clearly detected.")
            st.markdown("### Certifications")
            for item in p["certifications"]: st.write("• " + item)
            if not p["certifications"]: st.write("No certification clearly detected.")
            st.markdown("### Projects")
            for item in p["projects"]: st.write("• " + item)
            if not p["projects"]: st.write("No project heading or project detail clearly detected.")
        st.markdown("### Resume completeness checks")
        for item in p["section_checks"]:
            (st.success if item["present"] else st.warning)(f'{item["section"]}: {"Found" if item["present"] else "Could not identify"}')
        st.markdown("### Professional analysis")
        st.write(p["summary"])
        if st.button("Generate AI-enhanced insights"):
            with st.spinner("Preparing insights..."):
                st.session_state.ai_insights = generate_ai_insights(st.session_state.resume_text, p)
        if st.session_state.get("ai_insights"):
            st.markdown(st.session_state.ai_insights)

elif page == "Find Jobs":
    hero("Explore opportunities", "Filter the illustrative job catalogue by role, skills and preferences.")
    f1,f2,f3 = st.columns(3)
    with f1: title_q = st.text_input("Job title or keyword")
    with f2: company_q = st.text_input("Company")
    with f3: location_q = st.text_input("Location")
    f4,f5,f6 = st.columns(3)
    with f4: mode = st.selectbox("Work mode", ["Any","Remote","Hybrid","On-site"])
    with f5: level = st.selectbox("Experience level", ["Any","Internship","Entry-level","Mid-level","Senior"])
    with f6: employment = st.selectbox("Employment type", ["Any","Full-time","Internship","Part-time","Contract"])
    skills_q = st.text_input("Skills (comma-separated)", placeholder="Python, SQL, communication")
    filtered = filter_jobs(jobs, title=title_q, company=company_q, location=location_q,
                           work_mode=mode, experience=level, employment_type=employment, skills=skills_q)
    st.write(f"**{len(filtered)} opportunities found**")
    if filtered.empty:
        st.info("No sample roles match these filters. Try removing a filter.")
    else:
        for _, job in filtered.iterrows():
            with st.container(border=True):
                st.markdown(f"**{job['title']}** · {job['company']}")
                st.caption(f"{job['location']} · {job['work_mode']} · {job['experience_level']} · {job['employment_type']}")
                st.write(job["description"])
                st.caption(f"Skills: {job['skills']} | Salary: {job['salary_range']}")
                if job.get("application_url"):
                    st.link_button("Visit company careers page", job["application_url"])

elif page == "Job Matches":
    hero("Your job matches", "Ranked using profile similarity and weighted fit signals—not keyword count alone.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first to calculate personalized matches.")
    else:
        with st.expander("Set matching preferences", expanded=True):
            p1,p2,p3 = st.columns(3)
            with p1: pref_location = st.text_input("Preferred location", value=st.session_state.preferences.get("location",""))
            with p2: pref_mode = st.selectbox("Preferred work mode", ["Any","Remote","Hybrid","On-site"], index=["Any","Remote","Hybrid","On-site"].index(st.session_state.preferences.get("work_mode","Any")))
            with p3: pref_level = st.selectbox("Experience level", ["Any","Internship","Entry-level","Mid-level","Senior"], index=["Any","Internship","Entry-level","Mid-level","Senior"].index(st.session_state.preferences.get("experience","Any")))
            if st.button("Update matches", type="primary"):
                st.session_state.preferences = {"location":pref_location,"work_mode":pref_mode,"experience":pref_level}
                st.session_state.matches = match_jobs(st.session_state.resume_text, st.session_state.analysis, jobs, st.session_state.preferences)
                st.rerun()
        matches = st.session_state.matches
        if matches is None:
            matches = match_jobs(st.session_state.resume_text, st.session_state.analysis, jobs, st.session_state.preferences)
            st.session_state.matches = matches
        if matches.empty:
            st.info("No jobs in the current sample dataset.")
        else:
            top = matches.iloc[0]
            c1,c2,c3 = st.columns(3)
            with c1: metric_card("Best match", f"{int(top.match_score)}%", top.title)
            with c2: metric_card("Roles above 60%", int((matches.match_score >= 60).sum()), "Potentially strong fit")
            with c3: metric_card("Roles analyzed", len(matches), "Sample dataset")
            for _, job in matches.iterrows():
                score = int(job["match_score"])
                with st.container(border=True):
                    st.markdown(f"### {job['title']} <span style='color:#6b50b5;font-size:1rem'>· {score}% match</span>", unsafe_allow_html=True)
                    st.caption(f"{job['company']} · {job['location']} · {job['work_mode']} · {job['experience_level']}")
                    st.progress(score/100)
                    st.write(job["why_suitable"])
                    x,y = st.columns(2)
                    with x:
                        st.markdown("**Matching skills**")
                        st.write(", ".join(job["matching_skills"]) or "No direct skill overlap detected.")
                    with y:
                        st.markdown("**Skills to build**")
                        st.write(", ".join(job["missing_skills"]) or "No key gaps detected from listed skills.")
                    st.caption(f"Score breakdown — Skills {job['skills_score']:.0f}/100 · Experience {job['experience_score']:.0f}/100 · Education {job['education_score']:.0f}/100 · Role relevance {job['role_score']:.0f}/100 · Preferences {job['preference_score']:.0f}/100")
                    if job.get("application_url"):
                        st.link_button("Explore role / company", job["application_url"])

elif page == "Skill Gap Analysis":
    hero("Skill gap analyzer", "See what you already bring and what to learn next.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first.")
    else:
        matches = st.session_state.matches
        if matches is None:
            matches = match_jobs(st.session_state.resume_text, st.session_state.analysis, jobs, st.session_state.preferences)
        target = st.selectbox("Choose a target role", matches["title"].tolist() if not matches.empty else jobs["title"].tolist())
        row = (matches[matches.title == target].iloc[0] if not matches.empty and target in matches.title.values
               else jobs[jobs.title == target].iloc[0])
        gap = analyze_skill_gaps(st.session_state.analysis, row)
        a,b = st.columns(2)
        with a:
            st.markdown("### Skills you have")
            st.write(", ".join(gap["possessed"]) or "No matching skills detected.")
        with b:
            st.markdown("### Skills to develop")
            st.write(", ".join(gap["missing"]) or "You cover the listed skills.")
        if gap["missing"]:
            st.markdown("### Suggested learning priorities")
            for item in gap["roadmap"]:
                with st.container(border=True):
                    st.markdown(f"**{item['skill']}** · {item['priority']} priority")
                    st.write(item["action"])
                    st.caption(item["time_estimate"])
        fig = px.pie(names=["Already have","To develop"], values=[len(gap["possessed"]),len(gap["missing"])],
                     hole=.62, title="Target role skill coverage")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Career Recommendations":
    hero("Your career growth plan", "Practical next steps based on your profile and the roles in this sample dataset.")
    if not st.session_state.resume_text:
        st.warning("Upload a resume first.")
    else:
        matches = st.session_state.matches
        if matches is None:
            matches = match_jobs(st.session_state.resume_text, st.session_state.analysis, jobs, st.session_state.preferences)
        recs = build_career_recommendations(st.session_state.analysis, matches)
        st.markdown("### Recommended job roles")
        for role in recs["roles"]: st.write(f"• **{role['title']}** — {role['reason']}")
        st.markdown("### Resume improvements")
        for item in recs["resume"]: st.write("• " + item)
        st.markdown("### LinkedIn improvements")
        for item in recs["linkedin"]: st.write("• " + item)
        st.markdown("### Relevant certifications / learning")
        for item in recs["certifications"]: st.write("• " + item)
        st.markdown("### Project ideas")
        for item in recs["projects"]: st.write("• " + item)
        st.markdown("### Interview preparation")
        for item in recs["interview"]: st.write("• " + item)
        st.markdown("### Suggested 4-week action plan")
        st.table(pd.DataFrame(recs["plan"]))
        if st.button("Generate AI career suggestions"):
            with st.spinner("Generating personalized suggestions..."):
                st.session_state.ai_career = generate_ai_insights(st.session_state.resume_text,
                                                                  st.session_state.analysis,
                                                                  mode="career")
        if st.session_state.get("ai_career"):
            st.markdown(st.session_state.ai_career)

st.markdown("---")
st.caption("CareerMatch AI · Prototype dataset for exploration only. Always verify vacancies, eligibility, salary and application links on the employer's official site.")
