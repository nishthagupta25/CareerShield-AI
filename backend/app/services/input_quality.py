import re
from typing import Dict, List


JOB_KEYWORDS = [
    "job", "role", "responsibilities", "requirements", "skills", "experience",
    "developer", "engineer", "intern", "analyst", "manager", "salary",
    "apply", "interview", "company", "remote", "onsite", "hybrid",
    "python", "java", "javascript", "sql", "fastapi", "react", "node",
    "machine learning", "ai", "backend", "frontend", "cloud", "aws",
    "docker", "git", "database", "api"
]

RESUME_KEYWORDS = [
    "education", "experience", "project", "projects", "skills", "internship",
    "developer", "engineer", "github", "certification", "python", "java",
    "javascript", "sql", "fastapi", "react", "machine learning", "ai",
    "backend", "frontend", "cloud", "aws", "docker", "git", "api"
]


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z+#.-]*", (text or "").lower())


def _keyword_hits(text: str, keywords: List[str]) -> int:
    lower = (text or "").lower()
    return sum(1 for keyword in keywords if keyword in lower)


def _looks_like_garbage(tokens: List[str]) -> bool:
    if not tokens:
        return True

    if len(tokens) <= 3:
        return True

    unique_count = len(set(tokens))
    if len(tokens) >= 4 and unique_count <= 2:
        return True

    return False


def assess_text_quality(text: str, text_type: str = "job") -> Dict:
    tokens = _tokens(text)
    word_count = len(tokens)

    keywords = JOB_KEYWORDS if text_type == "job" else RESUME_KEYWORDS
    keyword_count = _keyword_hits(text, keywords)

    if not text or not text.strip():
        return {
            "is_valid": False,
            "quality": "Missing",
            "reason": f"No {text_type} text was provided.",
            "word_count": 0,
            "keyword_count": 0,
        }

    if _looks_like_garbage(tokens) and keyword_count == 0:
        return {
            "is_valid": False,
            "quality": "Invalid",
            "reason": f"The {text_type} text does not contain enough meaningful information.",
            "word_count": word_count,
            "keyword_count": keyword_count,
        }

    if word_count < 8 and keyword_count == 0:
        return {
            "is_valid": False,
            "quality": "Insufficient",
            "reason": f"The {text_type} text is too short for reliable analysis.",
            "word_count": word_count,
            "keyword_count": keyword_count,
        }

    return {
        "is_valid": True,
        "quality": "Valid",
        "reason": f"The {text_type} text contains enough information for analysis.",
        "word_count": word_count,
        "keyword_count": keyword_count,
    }


def build_input_quality_report(job_text: str, resume_text: str) -> Dict:
    job_quality = assess_text_quality(job_text, "job")
    resume_quality = assess_text_quality(resume_text, "resume")

    return {
        "job_text_quality": job_quality,
        "resume_text_quality": resume_quality,
        "job_input_valid": job_quality["is_valid"],
        "resume_input_valid": resume_quality["is_valid"],
    }