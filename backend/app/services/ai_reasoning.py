from typing import Dict, List


def _titles(red_flags: list) -> List[str]:
    return [str(flag.get("title", "")) for flag in red_flags if isinstance(flag, dict)]


def generate_ai_explanation(
    trust_score: float,
    scam_score: float,
    ml_prediction: str,
    ml_probability: float,
    red_flags: list,
    resume_score: float,
    matching_skills: list,
    missing_skills: list,
) -> Dict:
    flag_titles = _titles(red_flags)

    why_safe = []
    why_attention = []

    # Safety / scam reasoning
    if scam_score < 35:
        why_safe.append("Overall fraud risk is low based on the hybrid rule-based and ML analysis.")
    elif scam_score < 65:
        why_attention.append("The opportunity has moderate risk signals, so company verification is recommended.")
    else:
        why_attention.append("The opportunity has high fraud risk and should be avoided unless independently verified.")

    if "Likely Genuine" in ml_prediction:
        confidence = round(100 - ml_probability)
        why_safe.append(f"The ML classifier predicts this opportunity as genuine with {confidence}% confidence.")
    else:
        why_attention.append(f"The ML classifier predicts scam-like language with {round(ml_probability)}% scam probability.")

    if len(red_flags) == 0:
        why_safe.append("No major red flags were detected in the recruiter message or job posting.")
    else:
        why_attention.append(f"{len(red_flags)} warning sign(s) were detected by the rule engine.")

    # Specific red flag explanation
    for title in flag_titles:
        title_lower = title.lower()

        if "free email" in title_lower:
            why_attention.append("The recruiter email appears to use a free email provider instead of an official company domain.")
        elif "payment" in title_lower or "deposit" in title_lower:
            why_attention.append("The opportunity mentions payment or deposit before selection, which is a strong scam indicator.")
        elif "registration" in title_lower:
            why_attention.append("A registration fee is requested, which is unsafe for legitimate hiring.")
        elif "salary" in title_lower:
            why_attention.append("The salary appears unusually high compared to the provided job details.")
        elif "vague" in title_lower:
            why_attention.append("The job description is not detailed enough, so role responsibilities should be verified.")
        elif "immediate" in title_lower:
            why_attention.append("The recruiter message creates urgency, which is commonly used in scam communication.")
        elif "company" in title_lower:
            why_attention.append("Company details are incomplete or difficult to verify.")

    # Resume explanation
    if resume_score >= 75:
        why_safe.append("Your resume shows strong alignment with this opportunity.")
    elif resume_score >= 45:
        why_safe.append("Your resume partially matches the job requirements.")
        why_attention.append("Improving missing skills could increase your interview readiness.")
    else:
        why_attention.append("Your resume match is low, so this role may require stronger profile customization.")

    if matching_skills:
        why_safe.append(
            f"Your profile matches key skills such as {', '.join(matching_skills[:5])}."
        )

    if missing_skills:
        why_attention.append(
            f"Missing or weakly represented skills include {', '.join(missing_skills[:5])}."
        )

    # Final summary
    if scam_score >= 70:
        final_summary = (
            "CareerShield AI recommends avoiding this opportunity because multiple scam indicators "
            "or ML-based risk signals were detected."
        )
    elif scam_score >= 35:
        final_summary = (
            "CareerShield AI recommends applying with caution. The opportunity may be genuine, "
            "but verification is needed before sharing documents or personal details."
        )
    else:
        final_summary = (
            "CareerShield AI considers this opportunity reasonably safe based on the available information, "
            "while still recommending basic company verification before applying."
        )

    return {
        "why_safe": why_safe[:4],
        "why_attention": why_attention[:4],
        "final_summary": final_summary,
    }


def generate_ai_reasoning(
    trust_score: float,
    scam_score: float,
    ml_prediction: str,
    ml_probability: float,
    red_flags: list,
    resume_score: float,
    matching_skills: list,
    missing_skills: list,
):
    explanation = generate_ai_explanation(
        trust_score=trust_score,
        scam_score=scam_score,
        ml_prediction=ml_prediction,
        ml_probability=ml_probability,
        red_flags=red_flags,
        resume_score=resume_score,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
    )

    combined = []
    combined.extend(explanation["why_safe"])
    combined.extend(explanation["why_attention"])
    combined.append(explanation["final_summary"])
    return combined[:10]