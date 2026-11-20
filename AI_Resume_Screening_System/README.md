# AI-Based Resume Screening System (Non-Machine Learning Approach)

A Flask-based academic prototype that parses PDF/TXT resumes and ranks candidates against recruiter-defined job requirements using transparent, rule-based techniques. It does **not** use machine-learning models, transformer models, embeddings, or an LLM.

## Features

- Create job profiles with required skills, minimum experience, education, and certifications.
- Upload multiple PDF or TXT resumes for a job.
- Extract email, phone, likely name, education keywords, experience years, skills, and known certifications using regular expressions and predefined vocabularies.
- Compare extracted information against job requirements using exact keyword matching and `difflib.SequenceMatcher` fuzzy string similarity.
- Calculate a weighted score and rank candidates:
  - Skills: 50%
  - Experience: 25%
  - Education: 15%
  - Certifications: 10%
- Candidate detail page with matched/missing skills and component scores.
- Export screening results to CSV, Excel (.xlsx), and PDF.
- SQLAlchemy database layer. SQLite is configured by default for easy local evaluation; MySQL/PostgreSQL can be configured through `DATABASE_URL`.

## Technology stack

Python 3.8+, Flask, Flask-SQLAlchemy, PyPDF2, Python `re`, `difflib`, HTML, CSS, JavaScript, Bootstrap 5, SQLite (default), SQLAlchemy, ReportLab, openpyxl, pytest.

## Windows setup (PowerShell)

1. Install Python 3.10 or later.
2. Extract this ZIP and open a terminal in the extracted `AI_Resume_Screening_System` folder.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in that terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Start the application:

```powershell
python run.py
```

6. Open http://127.0.0.1:5000

The database tables are created automatically on first start.

## First demo (recommended)

1. Click **Create job**.
2. Use title: `Python Developer`.
3. Required skills: `Python, Flask, SQL, Git`.
4. Minimum experience: `1`.
5. Education: `B.Tech`.
6. Certifications: `NPTEL`.
7. Save the job.
8. Upload the two `.txt` files from `sample_resumes/`.
9. Open the candidate profiles and show the ranking and matching explanation.
10. Export Excel or PDF from the job results page.

For PDF demonstration, use a normal text-based PDF (not a scanned image). OCR is not included in this version.

## Database configuration

Default local database:

```env
DATABASE_URL=sqlite:///resume_screening.db
```

Copy `.env.example` to `.env` if you want to configure a database or secret key.

MySQL example (requires an appropriate driver such as `pymysql`):

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/resume_screening
```

PostgreSQL example (requires an appropriate driver such as `psycopg`):

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost/resume_screening
```

The default requirements file is intentionally lightweight for the SQLite demo. Install the matching MySQL/PostgreSQL driver separately if using those databases.

## How scoring works

Each component is scored from 0–100:

- Skill score = matched required skills / total required skills × 100.
- Experience score = min(actual years / required years, 1) × 100. If no experience is required, it is 100.
- Education score = 100 when the extracted education text matches the requested education string; otherwise 0. If no education is required, it is 100.
- Certification score = matched required certifications / total required certifications × 100. If none are required, it is 100.

Final score:

`(Skills × 0.50) + (Experience × 0.25) + (Education × 0.15) + (Certifications × 0.10)`

The weights are starter defaults and can be changed in `app/scoring.py`.

## Important limitations (state these honestly in a demo)

- This is a rule-based academic prototype, not a production recruitment platform.
- Resume parsing uses patterns and a small editable vocabulary; it will not understand every resume layout.
- The name is guessed from the first non-empty text line. Verify extracted fields.
- Experience extraction detects common expressions such as "2 years of experience"; complex employment timelines may not be calculated correctly.
- Education matching is text-based and may need manual review.
- Scanned/image-only PDFs are not OCR-processed.
- Fuzzy matching is string similarity, not semantic understanding.
- The app currently has no user authentication or role-based access control.
- The demo uses SQLite by default for easy setup. SQLAlchemy can connect to MySQL/PostgreSQL with a configured database URL and driver.
- Review all candidate information manually. A score is a decision-support signal, not a hiring decision. Automated scoring can reproduce bias if the requirements or vocabulary are biased.

## Project structure

```text
AI_Resume_Screening_System/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── parser.py
│   ├── scoring.py
│   ├── routes.py
│   ├── templates/
│   └── static/
├── sample_resumes/
├── tests/
├── uploads/
├── reports/
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

```powershell
pytest
```
