# CareerMatch AI

**Find the right job. Match your potential.**

CareerMatch AI is a Streamlit resume analyzer and job-fit explorer for students, graduates and professionals. It parses PDF/DOCX resumes, extracts skill and section signals, ranks a built-in illustrative job dataset, analyzes skill gaps and suggests career-development actions.

> **Important:** Jobs in `data/sample_jobs.csv` are sample records for testing the application. They are not live vacancies, and the sample application links lead to general career-search pages. Verify every real vacancy, eligibility requirement and salary with the employer.

## Features

- PDF and DOCX resume text extraction.
- Heuristic extraction of technical skills, programming languages, tools, soft skills, education, experience, projects and certifications.
- Weighted job-fit score:
  - Skills: 40%
  - Experience: 20%
  - Education: 15%
  - Role/text relevance: 15%
  - Location and preferences: 10%
- TF-IDF vectorization and cosine similarity for role/text relevance.
- Search filters for title, company, location, work mode, experience, employment type and skills.
- Ranked recommendations, skill gap roadmap, career suggestions and Plotly visualizations.
- Optional Groq-generated narrative insights. All core features work without a Groq key.
- No login or database required. Resume content is held in the current Streamlit session.

## Run locally

Python 3.10–3.12 is recommended.

```bash
# 1. Clone or download this repository
cd careermatch-ai

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

The app opens at the local URL shown in your terminal, usually `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository named `careermatch-ai`.
2. Upload the complete project folder, preserving the folder structure.
3. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
4. Select **Create app**, choose the repository and branch, and set the main file path to `app.py` (or `careermatch-ai/app.py` if the repository contains the parent folder).
5. Deploy. Streamlit installs packages from `requirements.txt`.
6. Open the app URL after deployment and test with a text-based PDF or DOCX resume.

Keep `.streamlit/secrets.toml` out of GitHub. It is ignored by `.gitignore`.

## Optional Groq API setup

1. Create an API key in your Groq account.
2. In Streamlit Community Cloud, open your app's **Settings → Secrets**.
3. Add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

4. Save the secrets and reboot the app if needed.

For local use, create `.streamlit/secrets.toml` with the same TOML entry. Never commit this file or expose your key in screenshots, source code or public repositories. Groq is optional; the app remains functional without it.

## Project structure

```text
careermatch-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py
│   ├── job_matcher.py
│   ├── skill_analyzer.py
│   ├── recommendations.py
│   └── ai_engine.py
├── data/
│   └── sample_jobs.csv
└── .streamlit/
    └── config.toml
```

## Matching methodology and limitations

The score is a transparent heuristic, not a hiring decision or probability of selection. Skills use overlap against the job's listed skills. Experience and education are inferred from resume text and sample job metadata. Role relevance uses TF-IDF and cosine similarity. Preference fit uses the location, work-mode and experience preferences selected in the app.

Resume parsing is rule-based and can miss unusual headings, tables, abbreviations or skills not included in the built-in vocabulary. Scanned/image-only PDFs need OCR before upload. Always review the extracted profile and correct your resume before relying on a match score.

## Adding a real job API later

Replace or extend `load_jobs()` in `app.py` with a provider-specific adapter that returns the same columns as `data/sample_jobs.csv`. Respect each provider's terms, rate limits, attribution and data licensing. Never label cached/sample data as live. Keep API credentials in Streamlit Secrets.

## Privacy

There is no user account, external resume database or persistent resume storage in this project. Uploaded content is processed in the running Streamlit session and may be subject to the hosting platform's operational logging and retention. Do not upload confidential or sensitive documents unless you are comfortable with the hosting provider's policies.
