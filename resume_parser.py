import io
import re
from collections import OrderedDict

SKILL_GROUPS = {
    "programming_languages": ["python","java","javascript","typescript","c","c++","c#","php","r","sql","html","css"],
    "tools": ["excel","power bi","tableau","git","github","docker","kubernetes","aws","azure","gcp","linux","jira","figma","tensorflow","pytorch","scikit-learn","streamlit","pandas","numpy"],
    "technical_skills": ["machine learning","deep learning","data analysis","data visualization","nlp","natural language processing","artificial intelligence","cloud computing","cybersecurity","networking","database management","rest api","api development","web development","software testing","automation testing","manual testing","devops","data structures","prompt engineering"],
    "soft_skills": ["communication","leadership","teamwork","problem solving","problem-solving","adaptability","time management","critical thinking","creativity","collaboration","presentation","analytical thinking"]
}
SECTION_PATTERNS = {
    "Education": r"\b(education|academic background|qualifications)\b",
    "Experience": r"\b(experience|employment|work history|internship)\b",
    "Projects": r"\b(projects|personal projects|academic projects)\b",
    "Certifications": r"\b(certifications|certificates|courses|training)\b",
    "Skills": r"\b(skills|technical skills|core competencies)\b",
    "Contact": r"(@|phone|mobile|contact)"
}

def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:
            raise ValueError(f"Unable to read PDF. It may be damaged or password-protected. Details: {exc}")
    elif ext == "docx":
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            chunks = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    chunks.append(" | ".join(cell.text for cell in row.cells))
            text = "\n".join(chunks)
        except Exception as exc:
            raise ValueError(f"Unable to read DOCX file. Details: {exc}")
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX resume.")
    return re.sub(r"[ \t]+", " ", text).strip()

def _find_terms(text, terms):
    low = text.lower()
    found = []
    for term in terms:
        pattern = r"(?<![a-z0-9+#])" + re.escape(term.lower()) + r"(?![a-z0-9+#])"
        if re.search(pattern, low):
            found.append(term.title() if term not in ["c","c++","c#","r","sql","html","css","aws","gcp","api","nlp"] else term.upper())
    return list(OrderedDict.fromkeys(found))

def analyze_resume(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Resume text is empty.")
    result = {}
    for group, terms in SKILL_GROUPS.items():
        result[group] = _find_terms(text, terms)
    result["technical_skills"] = list(OrderedDict.fromkeys(result["technical_skills"] + result["programming_languages"] + result["tools"]))
    lines = [line.strip(" •\t-") for line in text.splitlines() if line.strip()]
    result["education"] = [line[:220] for line in lines if re.search(r"\b(b\.?tech|bachelor|master|degree|university|college|diploma|12th|10th|bsc|msc|mba|gn?du)\b", line, re.I)][:8]
    result["experience"] = [line[:220] for line in lines if re.search(r"\b(intern|developer|analyst|engineer|manager|trainer|worked|experience|company|years?)\b", line, re.I)][:10]
    result["projects"] = [line[:220] for line in lines if re.search(r"\b(project|built|developed|created|designed|implemented)\b", line, re.I)][:10]
    result["certifications"] = [line[:220] for line in lines if re.search(r"\b(certified|certification|certificate|course completion|coursera|udemy)\b", line, re.I)][:10]
    result["section_checks"] = [{"section": name, "present": bool(re.search(pattern, text, re.I))}
                                for name, pattern in SECTION_PATTERNS.items()]
    present = [x["section"] for x in result["section_checks"] if x["present"]]
    missing = [x["section"] for x in result["section_checks"] if not x["present"]]
    result["summary"] = (
        f"The resume contains {len(result['technical_skills'])} detectable technical/tool skills "
        f"and {len(result['soft_skills'])} soft skills. Sections identified: {', '.join(present) or 'none clearly identified'}. "
        f"Consider strengthening or adding: {', '.join(missing) or 'quantified achievements and role-specific keywords'}. "
        "Automated extraction is an aid; verify the detected items and ensure each skill is supported by evidence."
    )
    return result
