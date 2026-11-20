# Project explanation and viva preparation

## 1. Project objective
The application helps an HR user organize resume screening. The recruiter defines a job's requirements, uploads candidate resumes, and receives a ranked list with a breakdown of how each score was calculated.

## 2. Why is it called non-machine-learning?
The implementation does not train or load an ML model. It uses:
- Regular expressions to locate patterns such as email, phone, degree labels, and experience-year phrases.
- A predefined skill/certification vocabulary to find known terms.
- Exact matching and `difflib.SequenceMatcher` to compare strings.
- A deterministic weighted formula to calculate scores.

The word "AI" in the project title follows the approved synopsis title; technically, this prototype is rule-based and non-ML.

## 3. Main workflow
1. HR creates a job profile.
2. Job data is stored in the database.
3. HR uploads one or more PDF/TXT resumes.
4. PyPDF2 extracts text from text-based PDFs; TXT files are read directly.
5. Parser normalizes text and extracts structured fields.
6. Extracted candidate details are stored.
7. Scoring module compares candidate attributes with job requirements.
8. Screening result is stored.
9. Dashboard sorts candidates by total score.
10. HR can open candidate details or export CSV, Excel, and PDF reports.

## 4. Explain the weighted formula
Skills 50%, experience 25%, education 15%, certifications 10%. The weights sum to 100%. The final score is a weighted average of the four component scores. A missing required skill reduces the skill component. A candidate with more than the required years receives at most 100% for experience.

## 5. What is fuzzy matching?
Fuzzy matching compares two strings and estimates how similar they are. Here `difflib.SequenceMatcher` gives a similarity ratio between 0 and 1. The matching function accepts a requirement when the best available candidate term reaches the threshold (default 0.82). This helps with small spelling variations; it is not semantic similarity.

## 6. Database tables
- Job: title, description, skills, experience, education, certifications.
- Candidate: extracted personal/education/experience/skill data and uploaded resume path.
- ScreeningResult: component scores, total score, matched/missing skills, and explanation.

## 7. Important limitations to disclose
- Scanned PDFs need OCR, which is not implemented.
- Resume formats vary; regex and vocabularies need tuning.
- Candidate name and experience are heuristic extractions and should be verified.
- No authentication is implemented in this MVP.
- SQLite is the default local database; MySQL/PostgreSQL can be configured with SQLAlchemy.
- Scores should support human review, not replace it.

## 8. Likely viva questions

**Q: Is this machine learning?**  
A: No. This version uses regex, predefined keyword matching, fuzzy string comparison, and a weighted rule-based scoring formula. It does not train or load a model.

**Q: How do you extract skills?**  
A: We maintain a vocabulary of skills. The parser normalizes resume text and checks each skill using case-insensitive regular expressions with word boundaries.

**Q: How do you rank candidates?**  
A: Each candidate receives four component scores. We apply the configured weights, calculate the total, and sort candidates in descending order.

**Q: What is the role of the database?**  
A: It stores job requirements, candidate information, uploaded resume references, and screening scores so results remain available after restarting the application.

**Q: What happens if a skill is missing?**  
A: It is added to the missing-skills list and lowers the skill match percentage.

**Q: What are the limitations?**  
A: The parser depends on text extraction and predefined patterns. It may miss information in unusual layouts or scanned PDFs. Human review is required.

**Q: Why use Flask?**  
A: Flask is a lightweight Python web framework that handles routes, requests, file uploads, and rendering HTML templates.

**Q: Why use SQLAlchemy?**  
A: It provides a database abstraction layer, allowing the same models to work with SQLite, MySQL, or PostgreSQL when the appropriate driver and connection URL are configured.
