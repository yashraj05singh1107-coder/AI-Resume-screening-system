from types import SimpleNamespace
from app.scoring import calculate_score

def test_weighted_rule_based_score():
    job = SimpleNamespace(required_skills="Python, Flask", min_experience=2,
                          education_requirement="B.Tech", certifications="NPTEL")
    candidate = SimpleNamespace(skills="Python, Flask", experience_years=2,
                                 education="B.Tech", certifications="NPTEL")
    result = calculate_score(candidate, job)
    assert result["total_score"] == 100.0
    assert result["skill_score"] == 100.0

def test_missing_skill_reduces_skill_score():
    job = SimpleNamespace(required_skills="Python, Flask", min_experience=0,
                          education_requirement="", certifications="")
    candidate = SimpleNamespace(skills="Python", experience_years=0,
                                 education="", certifications="")
    result = calculate_score(candidate, job)
    assert result["skill_score"] == 50.0
