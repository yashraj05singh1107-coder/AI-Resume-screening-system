from difflib import SequenceMatcher

WEIGHTS = {"skills": 0.50, "experience": 0.25, "education": 0.15, "certifications": 0.10}

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").casefold(), (b or "").casefold()).ratio()

def split_terms(value: str):
    return [x.strip() for x in (value or "").replace("\n", ",").split(",") if x.strip()]

def match_terms(required, available, threshold=0.82):
    matched, missing = [], []
    available = [x.strip() for x in available if x.strip()]
    for requirement in required:
        best = max((similarity(requirement, item) for item in available), default=0)
        if best >= threshold:
            matched.append(requirement)
        else:
            missing.append(requirement)
    return matched, missing

def calculate_score(candidate, job):
    required_skills = split_terms(job.required_skills)
    candidate_skills = split_terms(candidate.skills)
    matched, missing = match_terms(required_skills, candidate_skills)
    skill_score = (len(matched) / len(required_skills) * 100) if required_skills else 100.0

    required_exp = float(job.min_experience or 0)
    actual_exp = float(candidate.experience_years or 0)
    experience_score = 100.0 if required_exp <= 0 else min(actual_exp / required_exp, 1) * 100

    education_score = 100.0 if not (job.education_requirement or "").strip() else (
        100.0 if similarity(job.education_requirement, candidate.education) >= 0.72
        or job.education_requirement.casefold() in (candidate.education or "").casefold()
        else 0.0
    )

    required_certs = split_terms(job.certifications)
    candidate_certs = split_terms(candidate.certifications)
    cert_matched, _ = match_terms(required_certs, candidate_certs)
    cert_score = (len(cert_matched) / len(required_certs) * 100) if required_certs else 100.0

    total = (
        skill_score * WEIGHTS["skills"] +
        experience_score * WEIGHTS["experience"] +
        education_score * WEIGHTS["education"] +
        cert_score * WEIGHTS["certifications"]
    )
    explanation = (
        f"Matched {len(matched)} of {len(required_skills)} required skills; "
        f"experience {actual_exp:g}/{required_exp:g} years; "
        f"education {'matched' if education_score else 'not matched'}; "
        f"certifications matched {len(cert_matched)} of {len(required_certs)}."
    )
    return {
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "certification_score": round(cert_score, 2),
        "total_score": round(total, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "explanation": explanation,
    }
