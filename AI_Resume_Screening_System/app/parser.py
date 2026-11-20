import re
from pathlib import Path
from PyPDF2 import PdfReader

# Editable starter vocabulary. Add domain-specific terms as required.
SKILL_VOCABULARY = [
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css",
    "react", "node.js", "express", "flask", "django", "fastapi", "streamlit",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "git", "github",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn",
    "machine learning", "data analysis", "data science", "excel", "power bi",
    "tableau", "rest api", "api", "docker", "linux", "aws", "azure",
    "communication", "teamwork", "problem solving", "project management",
    "deep learning", "nlp", "tensorflow", "pytorch", "bootstrap"
]

CERT_VOCABULARY = [
    "aws certified", "azure fundamentals", "google data analytics",
    "nptel", "hacktoberfest", "python certification", "udemy", "coursera"
]

DEGREE_PATTERNS = [
    r"\bB\.?\s?Tech\b", r"\bB\.?\s?E\.?\b", r"\bBachelor(?:'s)?\b",
    r"\bM\.?\s?Tech\b", r"\bM\.?\s?E\.?\b", r"\bMaster(?:'s)?\b",
    r"\bMBA\b", r"\bPh\.?\s?D\.?\b", r"\bBCA\b", r"\bMCA\b",
    r"\bB\.?\s?Sc\b", r"\bM\.?\s?Sc\b", r"\bDiploma\b"
]

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError("Only PDF and TXT resumes are supported in this version.")

def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()

def _unique_ci(items):
    seen, result = set(), []
    for item in items:
        key = item.casefold().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result

def extract_candidate_data(raw_text: str) -> dict:
    text = normalize_text(raw_text)
    email_match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I)
    phone_match = re.search(r"(?<!\w)(?:\+?\d{1,3}[-.\s]?)?(?:\d[-.\s]?){9,12}\d(?!\w)", text)

    found_skills = []
    lower = text.casefold()
    for skill in SKILL_VOCABULARY:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.casefold()) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found_skills.append(skill)

    found_certs = [cert for cert in CERT_VOCABULARY if cert.casefold() in lower]
    degree = ""
    for pattern in DEGREE_PATTERNS:
        match = re.search(pattern, text, re.I)
        if match:
            degree = match.group(0)
            break

    # Heuristic: use an explicit "X years" expression when present.
    years = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|work)", text, re.I)]
    years += [float(x) for x in re.findall(r"(?:experience|worked\s+for)[^\n]{0,35}?(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", text, re.I)]
    experience = max(years) if years else 0.0

    # A simple name guess from the first non-empty line; user can correct it in the UI later.
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    first_line = re.sub(r"[^A-Za-z .'-]", "", first_line).strip()
    if len(first_line) > 80 or "@" in first_line:
        first_line = ""

    return {
        "name": first_line or "Unknown",
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
        "education": degree,
        "experience_years": experience,
        "skills": _unique_ci(found_skills),
        "certifications": _unique_ci(found_certs),
        "raw_text": text,
    }
