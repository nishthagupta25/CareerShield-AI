from typing import Dict, List


def get_safety_label(scam_score: float) -> str:
    if scam_score >= 70:
        return "High Risk"
    if scam_score >= 35:
        return "Needs Verification"
    return "Looks Safe"

def generate_career_verdict(
    recommendation: str,
    scam_score: float,
    red_flags: List[Dict],
    ml_prediction: str,
) -> str:
    if recommendation == "Insufficient Data":
        return (
            "Insufficient Data: Please provide a complete job description before relying on this analysis."
        )

    if recommendation == "Needs Resume Review":
        return (
            "Needs Resume Review: The job appears suitable for safety analysis, but the resume text is not detailed enough to judge your fit."
        )

    safety = get_safety_label(scam_score)

    if recommendation == "Avoid":
        return (
            f"{safety}: This opportunity looks risky. "
            f"CareerShield detected {len(red_flags)} warning signs and the ML model predicts it as {ml_prediction}."
        )

    if recommendation == "Apply with Caution":
        return (
            "Needs Verification: This opportunity has some risk signals. "
            "Verify the company website, recruiter identity, and job details before applying."
        )

    return (
        f"{safety}: This opportunity appears reasonably safe based on available information. "
        "Still verify the company website before sharing personal documents."
    )


def generate_recruiter_view(
    matching_skills: List[str],
    missing_skills: List[str],
    resume_match_score: float,
) -> str:
    if resume_match_score == 0 and not matching_skills:
        return (
            "CareerShield could not evaluate your resume because it does not contain enough meaningful information. "
            "Please add your skills, projects, education, and experience for a personalized analysis."
        )

    if resume_match_score >= 75:
        base = "From a recruiter's perspective, your profile looks strongly aligned with this role."
    elif resume_match_score >= 50:
        base = "From a recruiter's perspective, your profile partially matches this role."
    else:
        base = "From a recruiter's perspective, your profile needs stronger alignment with this role."

    if matching_skills:
        base += f" Your strongest matching skills are: {', '.join(matching_skills[:5])}."

    if missing_skills:
        base += f" You should improve or highlight: {', '.join(missing_skills[:5])}."

    return base


def generate_skill_roadmap(missing_skills: List[str]) -> List[str]:
    if not missing_skills:
        return [
            "No major missing skills were detected. Focus on interview practice and project explanation."
        ]

    roadmap = []
    for skill in missing_skills[:5]:
        roadmap.append(
            f"Strengthen {skill} and add proof through a project, internship, or resume bullet."
        )

    return roadmap

def calculate_interview_readiness(
    resume_match_score: float,
    matching_skills: List[str],
    missing_skills: List[str],
) -> int:
    score = resume_match_score

    score += min(len(matching_skills) * 3, 15)
    score -= min(len(missing_skills) * 5, 25)

    return int(max(0, min(score, 100)))


def generate_interview_questions(job_skills: List[str]) -> List[str]:
    questions = []

    question_bank = {
        "Python": "Explain how you used Python in your projects.",
        "Machine Learning": "How do you train and evaluate a machine learning model?",
        "Deep Learning": "What is the difference between machine learning and deep learning?",
        "NLP": "How do text embeddings or NLP models help in understanding language?",
        "FastAPI": "How does FastAPI handle API requests?",
        "REST API": "What is a REST API and how have you used it?",
        "SQL": "Write a query to filter and aggregate data from a table.",
        "Docker": "Why is Docker useful for deployment?",
        "Git": "How do you use Git in project development?",
        "Backend Development": "How does the backend communicate with the frontend?",
        "Artificial Intelligence": "Where is AI used in your project?",
    }

    for skill in job_skills:
        if skill in question_bank:
            questions.append(question_bank[skill])

    if not questions:
      questions = [
        "Add a detailed job description to generate role-specific interview questions."
    ]

    return questions[:5]


def generate_career_intelligence(
    recommendation: str,
    scam_score: float,
    red_flags: List[Dict],
    ml_prediction: str,
    resume_match_score: float,
    matching_skills: List[str],
    missing_skills: List[str],
    job_skills: List[str],
) -> Dict:
    readiness = calculate_interview_readiness(
        resume_match_score,
        matching_skills,
        missing_skills,
    )

    return {
        "ai_career_verdict": generate_career_verdict(
            recommendation,
            scam_score,
            red_flags,
            ml_prediction,
        ),
        "ai_recruiter_view": generate_recruiter_view(
            matching_skills,
            missing_skills,
            resume_match_score,
        ),
        "interview_readiness_score": readiness,
        "skill_roadmap": generate_skill_roadmap(missing_skills),
        "likely_interview_questions": generate_interview_questions(job_skills),
    }