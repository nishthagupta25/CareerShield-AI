from typing import List, Dict


def calculate_trust_score(red_flags: List[Dict]) -> int:
    score = 100
    for f in red_flags:
        sev = f.get("severity", "low").lower()
        if sev == "high":
            score -= 18
        elif sev == "medium":
            score -= 10
        else:
            score -= 5
    if score < 0:
        score = 0
    return score


def calculate_scam_risk(red_flags: List[Dict]) -> int:
    risk = 0
    for f in red_flags:
        sev = f.get("severity", "low").lower()
        if sev == "high":
            risk += 20
        elif sev == "medium":
            risk += 10
        else:
            risk += 5
    if risk > 100:
        risk = 100
    return risk


def scam_risk_level(score: int) -> str:
    if score <= 30:
        return "Low"
    if score <= 65:
        return "Medium"
    return "High"


def generate_final_recommendation(trust_score: int, scam_risk: int) -> str:
    level = scam_risk_level(scam_risk)
    if level == "High" or trust_score < 40:
        return "Avoid"
    if level == "Medium" or trust_score < 70:
        return "Apply with Caution"
    return "Safe to Apply"


def generate_explanation(red_flags: List[Dict], trust_score: int, scam_risk: int) -> str:
    if not red_flags:
        return "No red flags detected; the posting appears legitimate based on heuristics."
    top = [f["title"] for f in red_flags[:3]]
    return f"Detected {len(red_flags)} red flags including: {', '.join(top)}. Trust score: {trust_score}. Risk: {scam_risk}."
