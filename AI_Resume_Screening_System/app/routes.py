import csv
import io
import os
import uuid
from pathlib import Path
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename
from app import db
from app.models import Job, Candidate, ScreeningResult
from app.parser import extract_text, extract_candidate_data
from app.scoring import calculate_score, split_terms

bp = Blueprint("main", __name__)
ALLOWED_EXTENSIONS = {"pdf", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    total_candidates = Candidate.query.count()
    return render_template("index.html", jobs=jobs, total_candidates=total_candidates)

@bp.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Please enter a job title.", "danger")
            return redirect(url_for("main.new_job"))
        job = Job(
            title=title,
            description=request.form.get("description", "").strip(),
            required_skills=request.form.get("required_skills", "").strip(),
            min_experience=max(float(request.form.get("min_experience") or 0), 0),
            education_requirement=request.form.get("education_requirement", "").strip(),
            certifications=request.form.get("certifications", "").strip(),
        )
        db.session.add(job)
        db.session.commit()
        flash("Job requirement saved.", "success")
        return redirect(url_for("main.job_detail", job_id=job.id))
    return render_template("job_form.html")

@bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    candidates = Candidate.query.filter_by(job_id=job.id).all()
    candidates.sort(key=lambda c: c.result.total_score if c.result else 0, reverse=True)
    return render_template("job_detail.html", job=job, candidates=candidates)

@bp.route("/jobs/<int:job_id>/upload", methods=["POST"])
def upload_resumes(job_id):
    job = Job.query.get_or_404(job_id)
    files = request.files.getlist("resumes")
    if not files or all(not f.filename for f in files):
        flash("Choose at least one PDF or TXT resume.", "warning")
        return redirect(url_for("main.job_detail", job_id=job.id))
    success, errors = 0, []
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    for file in files:
        if not file.filename:
            continue
        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: unsupported file type")
            continue
        safe_name = secure_filename(file.filename)
        stored_name = f"{uuid.uuid4().hex}_{safe_name}"
        path = upload_dir / stored_name
        file.save(path)
        try:
            text = extract_text(str(path))
            if not text.strip():
                raise ValueError("No selectable text found (scanned PDFs need OCR, which is not included).")
            data = extract_candidate_data(text)
            candidate = Candidate(
                job_id=job.id, name=data["name"], email=data["email"], phone=data["phone"],
                education=data["education"], experience_years=data["experience_years"],
                skills=", ".join(data["skills"]), certifications=", ".join(data["certifications"]),
                resume_filename=safe_name, resume_path=str(path)
            )
            db.session.add(candidate)
            db.session.flush()
            score = calculate_score(candidate, job)
            result = ScreeningResult(
                candidate_id=candidate.id, skill_score=score["skill_score"],
                experience_score=score["experience_score"], education_score=score["education_score"],
                certification_score=score["certification_score"], total_score=score["total_score"],
                matched_skills=", ".join(score["matched_skills"]),
                missing_skills=", ".join(score["missing_skills"]), explanation=score["explanation"]
            )
            db.session.add(result)
            success += 1
        except Exception as exc:
            db.session.rollback()
            path.unlink(missing_ok=True)
            errors.append(f"{safe_name}: {exc}")
    db.session.commit()
    if success:
        flash(f"Processed {success} resume(s) and calculated rankings.", "success")
    for error in errors:
        flash(error, "danger")
    return redirect(url_for("main.job_detail", job_id=job.id))

@bp.route("/candidates/<int:candidate_id>")
def candidate_detail(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    return render_template("candidate_detail.html", candidate=candidate)

@bp.route("/jobs/<int:job_id>/export.csv")
def export_csv(job_id):
    job = Job.query.get_or_404(job_id)
    candidates = Candidate.query.filter_by(job_id=job.id).all()
    candidates.sort(key=lambda c: c.result.total_score if c.result else 0, reverse=True)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Candidate", "Email", "Phone", "Education", "Experience (years)",
                     "Skills", "Certifications", "Skill score", "Experience score",
                     "Education score", "Certification score", "Total score", "Matched skills", "Missing skills"])
    for rank, c in enumerate(candidates, 1):
        r = c.result
        writer.writerow([rank, c.name, c.email, c.phone, c.education, c.experience_years, c.skills,
                         c.certifications, r.skill_score if r else 0, r.experience_score if r else 0,
                         r.education_score if r else 0, r.certification_score if r else 0,
                         r.total_score if r else 0, r.matched_skills if r else "", r.missing_skills if r else ""])
    data = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    return send_file(data, mimetype="text/csv", as_attachment=True,
                     download_name=f"job_{job.id}_screening.csv")

@bp.route("/jobs/<int:job_id>/export.xlsx")
def export_xlsx(job_id):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    job = Job.query.get_or_404(job_id)
    candidates = Candidate.query.filter_by(job_id=job.id).all()
    candidates.sort(key=lambda c: c.result.total_score if c.result else 0, reverse=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Candidate Ranking"
    ws.append(["Rank", "Candidate", "Email", "Phone", "Education", "Experience (years)",
               "Skills", "Certifications", "Skill %", "Experience %", "Education %",
               "Certification %", "Overall %", "Matched skills", "Missing skills"])
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="243B53")
    for rank, c in enumerate(candidates, 1):
        r = c.result
        ws.append([rank, c.name, c.email, c.phone, c.education, c.experience_years, c.skills,
                   c.certifications, r.skill_score if r else 0, r.experience_score if r else 0,
                   r.education_score if r else 0, r.certification_score if r else 0,
                   r.total_score if r else 0, r.matched_skills if r else "", r.missing_skills if r else ""])
    for column in ws.columns:
        letter = column[0].column_letter
        ws.column_dimensions[letter].width = min(max(max(len(str(cell.value or "")) for cell in column) + 2, 12), 34)
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(stream, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name=f"job_{job.id}_screening.xlsx")

@bp.route("/jobs/<int:job_id>/export.pdf")
def export_pdf(job_id):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    job = Job.query.get_or_404(job_id)
    candidates = Candidate.query.filter_by(job_id=job.id).all()
    candidates.sort(key=lambda c: c.result.total_score if c.result else 0, reverse=True)
    stream = io.BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=landscape(A4), rightMargin=24, leftMargin=24)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Resume Screening Report — {job.title}", styles["Title"]),
             Paragraph(f"Required skills: {job.required_skills or 'Not specified'}", styles["Normal"]),
             Spacer(1, 12)]
    data = [["Rank", "Candidate", "Email", "Skills %", "Experience %", "Education %", "Cert. %", "Overall %"]]
    for rank, c in enumerate(candidates, 1):
        r = c.result
        data.append([str(rank), c.name, c.email or "-", f"{r.skill_score:.1f}" if r else "0",
                     f"{r.experience_score:.1f}" if r else "0", f"{r.education_score:.1f}" if r else "0",
                     f"{r.certification_score:.1f}" if r else "0", f"{r.total_score:.1f}" if r else "0"])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#243b53")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("PADDING", (0,0), (-1,-1), 6)
    ]))
    story.append(table)
    doc.build(story)
    stream.seek(0)
    return send_file(stream, mimetype="application/pdf", as_attachment=True,
                     download_name=f"job_{job.id}_screening.pdf")

@bp.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum upload size is 10 MB per request.", "danger")
    return redirect(url_for("main.index"))
