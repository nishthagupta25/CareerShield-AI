from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from .services.ai_reasoning import generate_ai_reasoning, generate_ai_explanation
from .services.scam_detector import detect_red_flags
from .services.input_quality import build_input_quality_report
from .services.scoring import (
    calculate_trust_score,
    calculate_scam_risk,
    scam_risk_level,
    generate_final_recommendation,
    generate_explanation,
)
from .services.skill_extractor import extract_skills
from .services.resume_matcher import calculate_resume_match, detect_missing_skills
from .services.ml_predictor import predict_scam_probability
from .services.career_intelligence import generate_career_intelligence
from .services.model_info import get_model_summary
app = FastAPI(title="CareerShield AI Backend")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


class AnalyzeRequest(BaseModel):
    job_text: str = ""
    recruiter_message: str = ""
    email: str = ""
    salary: str = ""


class AnalyzeResumeRequest(BaseModel):
    resume_text: str = ""
    job_text: str = ""


class GenerateReportRequest(BaseModel):
    job_text: str = ""
    recruiter_message: str = ""
    email: str = ""
    salary: str = ""
    resume_text: str = ""


@app.post("/analyze-job")
async def analyze_job(payload: AnalyzeRequest) -> Dict:
    red_flags = detect_red_flags(
        payload.job_text, payload.recruiter_message, payload.email, payload.salary
    )
    trust = calculate_trust_score(red_flags)
    scam_score = calculate_scam_risk(red_flags)
    scam_level = scam_risk_level(scam_score)
    recommendation = generate_final_recommendation(trust, scam_score)
    explanation = generate_explanation(red_flags, trust, scam_score)
    return {
        "red_flags": red_flags,
        "red_flag_count": len(red_flags),
        "trust_score": trust,
        "scam_risk_score": scam_score,
        "scam_risk_level": scam_level,
        "recommendation": recommendation,
        "explanation": explanation,
    }


@app.post("/analyze-resume")
async def analyze_resume(payload: AnalyzeResumeRequest):
    score = calculate_resume_match(payload.resume_text, payload.job_text)
    skills_info = detect_missing_skills(payload.resume_text, payload.job_text)
    return {
        "resume_match_score": score,
        "matching_skills": skills_info["matching_skills"],
        "missing_skills": skills_info["missing_skills"],
        "resume_skills": skills_info["resume_skills"],
        "job_skills": skills_info["job_skills"],
    }

@app.post("/generate-report")
async def generate_report(payload: GenerateReportRequest):
    input_quality = build_input_quality_report(payload.job_text, payload.resume_text)
    job_input_valid = input_quality["job_input_valid"]
    resume_input_valid = input_quality["resume_input_valid"]
    model_summary = get_model_summary()

    # CASE 1: invalid job input => no ML/rules pretending
    if not job_input_valid:
        return {
            "red_flags": [],
            "trust_score": 0,
            "scam_risk_score": 0,
            "scam_risk_level": "Insufficient Data",
            "rule_scam_score": 0,
            "ml_prediction": "Not Available",
            "ml_scam_probability": 0,
            "model_confidence": 0,
            "recommendation": "Insufficient Data",
            "explanation": input_quality["job_text_quality"]["reason"],
            "resume_match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "resume_skills": [],
            "job_skills": [],
            "opportunity_score": 0,
            "ai_career_verdict": (
                "Insufficient Data: Please provide a proper job description with role, "
                "responsibilities, required skills, company details, and hiring process."
            ),
            "ai_recruiter_view": (
                "CareerShield cannot evaluate this opportunity because the job description "
                "does not contain enough meaningful information."
            ),
            "interview_readiness_score": 0,
            "skill_roadmap": [
                "Add a complete job description to receive a meaningful skill roadmap."
            ],
            "likely_interview_questions": [
                "Add a detailed job description to generate role-specific interview questions."
            ],
            "ai_reasoning": [input_quality["job_text_quality"]["reason"]],
            "ai_explanation": {
                "why_safe": [],
                "why_attention": [input_quality["job_text_quality"]["reason"]],
                "final_summary": (
                    "CareerShield AI could not analyze this opportunity because the job input is insufficient."
                ),
            },
            "model_summary": model_summary,
            "input_quality": input_quality,
            "job_input_valid": job_input_valid,
            "resume_input_valid": resume_input_valid,
        }

    # CASE 2: valid job input => analyze job safety
    red_flags = detect_red_flags(
        payload.job_text,
        payload.recruiter_message,
        payload.email,
        payload.salary,
    )

    trust = calculate_trust_score(red_flags)
    rule_scam_score = calculate_scam_risk(red_flags)

    ml_result = predict_scam_probability(
        payload.job_text,
        payload.recruiter_message,
    )

    ml_scam_probability = ml_result["scam_probability"]
    scam_score = round((rule_scam_score * 0.6) + (ml_scam_probability * 0.4), 2)

    scam_level = scam_risk_level(scam_score)
    recommendation = generate_final_recommendation(trust, scam_score)
    explanation = generate_explanation(red_flags, trust, scam_score)

    job_only_skills = detect_missing_skills("", payload.job_text)

    # Resume logic
    if resume_input_valid:
        resume_score = calculate_resume_match(payload.resume_text, payload.job_text)
        skills_info = detect_missing_skills(payload.resume_text, payload.job_text)
    else:
        resume_score = 0
        skills_info = {
            "matching_skills": [],
            "missing_skills": job_only_skills["job_skills"],
            "resume_skills": [],
            "job_skills": job_only_skills["job_skills"],
        }

    # If resume is invalid, job may be safe, but full candidate fit cannot be claimed
    if not resume_input_valid:
        recommendation = "Needs Resume Review"
        explanation = (
            "The job opportunity appears low risk, but the resume text is insufficient for resume-job matching."
        )

    job_quality_score = max(0, 100 - scam_score)
    opportunity = trust * 0.35 + resume_score * 0.35 + job_quality_score * 0.30
    opportunity_score = round(min(max(opportunity, 0), 100), 2)

    if not resume_input_valid:
        opportunity_score = min(opportunity_score, 45)

    career_ai = generate_career_intelligence(
        recommendation=recommendation,
        scam_score=scam_score,
        red_flags=red_flags,
        ml_prediction=ml_result["ml_prediction"],
        resume_match_score=resume_score,
        matching_skills=skills_info["matching_skills"],
        missing_skills=skills_info["missing_skills"],
        job_skills=skills_info["job_skills"],
    )
    if recommendation == "Avoid":
        career_ai["skill_roadmap"] = [
           "Do not focus on preparing for this opportunity. First verify the company, recruiter identity, and hiring process."
       ]
        career_ai["likely_interview_questions"] = [
        "No interview preparation is recommended until this opportunity is independently verified."
       ]
    ai_reasoning = generate_ai_reasoning(
        trust_score=trust,
        scam_score=scam_score,
        ml_prediction=ml_result["ml_prediction"],
        ml_probability=ml_result["scam_probability"],
        red_flags=red_flags,
        resume_score=resume_score,
        matching_skills=skills_info["matching_skills"],
        missing_skills=skills_info["missing_skills"],
    )

    ai_explanation = generate_ai_explanation(
        trust_score=trust,
        scam_score=scam_score,
        ml_prediction=ml_result["ml_prediction"],
        ml_probability=ml_result["scam_probability"],
        red_flags=red_flags,
        resume_score=resume_score,
        matching_skills=skills_info["matching_skills"],
        missing_skills=skills_info["missing_skills"],
    )

    if not resume_input_valid:
        ai_reasoning = [
            "The job description contains enough information for safety analysis.",
            "The resume text does not contain enough meaningful information for profile matching.",
            "CareerShield can detect job risk, but cannot evaluate candidate fit without a proper resume.",
        ]
        ai_explanation = {
            "why_safe": [
                "The job description contains enough information for job safety analysis."
            ],
            "why_attention": [
                "The resume text is insufficient, so resume match and interview readiness cannot be evaluated properly.",
                "Add skills, projects, education, and experience for personalized career insights.",
            ],
            "final_summary": (
                "The job opportunity can be checked for safety, but CareerShield needs a complete resume to evaluate your fit."
            ),
        }

    return {
        "red_flags": red_flags,
        "trust_score": trust,
        "scam_risk_score": scam_score,
        "scam_risk_level": scam_level,
        "rule_scam_score": rule_scam_score,
        "ml_prediction": ml_result["ml_prediction"],
        "ml_scam_probability": ml_result["scam_probability"],
        "model_confidence": ml_result["model_confidence"],
        "recommendation": recommendation,
        "explanation": explanation,
        "resume_match_score": resume_score,
        "matching_skills": skills_info["matching_skills"],
        "missing_skills": skills_info["missing_skills"],
        "resume_skills": skills_info["resume_skills"],
        "job_skills": skills_info["job_skills"],
        "opportunity_score": opportunity_score,
        "ai_career_verdict": career_ai["ai_career_verdict"],
        "ai_recruiter_view": career_ai["ai_recruiter_view"],
        "interview_readiness_score": career_ai["interview_readiness_score"],
        "skill_roadmap": career_ai["skill_roadmap"],
        "likely_interview_questions": career_ai["likely_interview_questions"],
        "ai_reasoning": ai_reasoning,
        "ai_explanation": ai_explanation,
        "model_summary": model_summary,
        "input_quality": input_quality,
        "job_input_valid": job_input_valid,
        "resume_input_valid": resume_input_valid,
    }