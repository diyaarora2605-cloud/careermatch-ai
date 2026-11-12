import re

def analyze_skill_gaps(profile, job):
    required = {x.strip().lower() for x in re.split(r"[,;|]", str(job.get("skills",""))) if x.strip()}
    have = {str(x).strip().lower() for x in profile.get("technical_skills", []) + profile.get("soft_skills", [])}
    possessed = sorted(required & have)
    missing = sorted(required - have)
    roadmap = []
    for skill in missing:
        if skill in {"python","sql","excel","communication","git"}:
            priority, duration = "High", "2–4 weeks of focused practice"
        elif skill in {"machine learning","power bi","tableau","aws","azure","docker","linux"}:
            priority, duration = "High", "4–6 weeks with a hands-on project"
        else:
            priority, duration = "Medium", "2–5 weeks depending on your starting level"
        action = f"Learn the fundamentals of {skill}, practice with guided exercises, then demonstrate it in a small portfolio project."
        roadmap.append({"skill": skill.title(), "priority": priority, "action": action, "time_estimate": duration})
    roadmap.sort(key=lambda x: (x["priority"] != "High", x["skill"]))
    return {"possessed": possessed, "missing": missing, "roadmap": roadmap}
