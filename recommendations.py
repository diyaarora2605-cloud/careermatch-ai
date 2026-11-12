def build_career_recommendations(profile, matches):
    roles = []
    if matches is not None and not matches.empty:
        for _, row in matches.head(5).iterrows():
            roles.append({"title": row["title"], "reason": f"{int(row['match_score'])}% calculated fit in this sample catalogue; review the listed skill gaps before applying."})
    if not roles:
        roles = [{"title":"Entry-level analyst / associate roles","reason":"A broad starting point while you build evidence of your skills."}]
    resume = [
        "Add a short 2–3 line summary tailored to the role you want.",
        "Show measurable outcomes: scale, time saved, accuracy, users or business impact.",
        "For every project, explain the problem, your contribution, tools used and result.",
        "Keep dates, headings, tense and bullet formatting consistent.",
        "Only list skills you can confidently explain in an interview."
    ]
    if not profile.get("projects"): resume.insert(1, "Add 2 relevant projects with working links or screenshots.")
    if not profile.get("certifications"): resume.append("Add credible role-relevant certifications only after completing the learning.")
    linkedin = [
        "Use a clear headline: target role + strongest skills + domain.",
        "Write an About section with your strengths, evidence and the roles you are seeking.",
        "Add projects, certificates and a clean resume to the Featured section.",
        "Request recommendations from mentors, teammates or instructors who know your work."
    ]
    certifications = [
        "Google Career Certificates (choose a role-aligned data, IT support or project track).",
        "Microsoft Learn role-based learning paths for Azure, Power BI or fundamentals.",
        "AWS Skill Builder foundational learning for cloud-oriented roles.",
        "For AI/data roles, complete a practical Python, SQL and ML course with a portfolio project."
    ]
    projects = [
        "Build a resume-to-job matching tool and explain its scoring method.",
        "Create a dashboard from a public dataset with clear business insights.",
        "Build a small end-to-end project using a documented dataset and publish the code.",
        "Write a case study explaining the problem, decisions, limitations and results."
    ]
    interview = [
        "Prepare a 60-second introduction and 2 STAR-format achievement stories.",
        "Practice explaining every resume skill and project without reading notes.",
        "Review role fundamentals, basic SQL / Python where relevant, and scenario questions.",
        "Prepare thoughtful questions about the team, success measures and learning support."
    ]
    plan = [
        {"Week":"1","Focus":"Choose a target role; revise resume summary and project bullets.","Deliverable":"Role-specific resume draft"},
        {"Week":"2","Focus":"Learn the top 1–2 missing skills from your chosen job match.","Deliverable":"Learning notes + practice exercises"},
        {"Week":"3","Focus":"Build or improve one project that demonstrates those skills.","Deliverable":"Portfolio project with README"},
        {"Week":"4","Focus":"Update LinkedIn; practice interview questions; apply selectively.","Deliverable":"Updated profile + application tracker"}
    ]
    return {"roles":roles,"resume":resume,"linkedin":linkedin,"certifications":certifications,
            "projects":projects,"interview":interview,"plan":plan}
