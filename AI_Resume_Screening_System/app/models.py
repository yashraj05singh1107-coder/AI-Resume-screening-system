from datetime import datetime
from app import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default="")
    required_skills = db.Column(db.Text, default="")
    min_experience = db.Column(db.Float, default=0)
    education_requirement = db.Column(db.String(160), default="")
    certifications = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidates = db.relationship("Candidate", backref="job", cascade="all, delete-orphan")

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    name = db.Column(db.String(160), default="Unknown")
    email = db.Column(db.String(254), default="")
    phone = db.Column(db.String(50), default="")
    education = db.Column(db.String(255), default="")
    experience_years = db.Column(db.Float, default=0)
    skills = db.Column(db.Text, default="")
    certifications = db.Column(db.Text, default="")
    resume_filename = db.Column(db.String(255), nullable=False)
    resume_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.relationship("ScreeningResult", backref="candidate", uselist=False,
                             cascade="all, delete-orphan")

class ScreeningResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidate.id"), unique=True, nullable=False)
    skill_score = db.Column(db.Float, default=0)
    experience_score = db.Column(db.Float, default=0)
    education_score = db.Column(db.Float, default=0)
    certification_score = db.Column(db.Float, default=0)
    total_score = db.Column(db.Float, default=0)
    matched_skills = db.Column(db.Text, default="")
    missing_skills = db.Column(db.Text, default="")
    explanation = db.Column(db.Text, default="")
    screened_at = db.Column(db.DateTime, default=datetime.utcnow)
