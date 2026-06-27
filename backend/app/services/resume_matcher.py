from typing import Dict, List
from .skill_extractor import extract_skills
import re
import math


def _cosine_sim_from_counts(a: Dict[str, int], b: Dict[str, int]) -> float:
    # compute cosine similarity between two term-frequency dicts
    common = set(a.keys()) | set(b.keys())
    dot = sum(a.get(k, 0) * b.get(k, 0) for k in common)
    norma = math.sqrt(sum(v * v for v in a.values()))
    normb = math.sqrt(sum(v * v for v in b.values()))
    if norma == 0 or normb == 0:
        return 0.0
    return dot / (norma * normb)


def _simple_tokenize(text: str) -> List[str]:
    txt = (text or "").lower()
    # keep basic word tokens
    tokens = re.findall(r"\b[a-z0-9#+\.\-]+\b", txt)
    return tokens


def calculate_resume_match(resume_text: str, job_text: str) -> float:
    """
    Calculates semantic resume-job similarity using Sentence Transformer embeddings.
    Falls back to simple token cosine similarity if embedding model fails.
    """
    if not resume_text or not job_text:
        return 0.0

    try:
        from .semantic_engine import semantic_similarity
        return semantic_similarity(resume_text, job_text)

    except Exception:
        toks_a = _simple_tokenize(resume_text)
        toks_b = _simple_tokenize(job_text)

        if not toks_a or not toks_b:
            return 0.0

        freq_a = {}
        freq_b = {}

        for t in toks_a:
            freq_a[t] = freq_a.get(t, 0) + 1

        for t in toks_b:
            freq_b[t] = freq_b.get(t, 0) + 1

        sim = _cosine_sim_from_counts(freq_a, freq_b)
        return round(float(sim * 100.0), 2)


def detect_missing_skills(resume_text: str, job_text: str) -> Dict[str, List[str]]:
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))

    matching = sorted(list(resume_skills & job_skills))
    missing = sorted(list(job_skills - resume_skills))

    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "resume_skills": sorted(list(resume_skills)),
        "job_skills": sorted(list(job_skills)),
    }
