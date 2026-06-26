from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from .services.ai_reasoning import generate_ai_reasoning, generate_ai_explanation
from .services.scam_detector import detect_red_flags
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

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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
    # rule-based scam analysis
    red_flags = detect_red_flags(
        payload.job_text,
        payload.recruiter_message,
        payload.email,
        payload.salary,
    )

    trust = calculate_trust_score(red_flags)
    rule_scam_score = calculate_scam_risk(red_flags)

    # ML scam prediction
    ml_result = predict_scam_probability(
        payload.job_text,
        payload.recruiter_message,
    )

    ml_scam_probability = ml_result["scam_probability"]

    # hybrid scam score = rule engine + ML model
    scam_score = round((rule_scam_score * 0.6) + (ml_scam_probability * 0.4), 2)

    scam_level = scam_risk_level(scam_score)
    recommendation = generate_final_recommendation(trust, scam_score)
    explanation = generate_explanation(red_flags, trust, scam_score)

    # resume analysis
    resume_score = calculate_resume_match(payload.resume_text, payload.job_text)
    skills_info = detect_missing_skills(payload.resume_text, payload.job_text)

    # job quality and opportunity score
    job_quality_score = max(0, 100 - scam_score)
    opportunity = trust * 0.35 + resume_score * 0.35 + job_quality_score * 0.30
    opportunity_score = round(min(max(opportunity, 0), 100), 2)

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
    model_summary = get_model_summary()
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
    }