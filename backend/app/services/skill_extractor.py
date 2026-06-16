import re
from typing import List

SKILLS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "SQL",
    "MongoDB",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "FastAPI",
    "Flask",
    "Git",
    "Docker",
    "AWS",
]


def extract_skills(text: str) -> List[str]:
    """Return a list of matched skills from the provided text.

    Matching is case-insensitive and uses simple regex heuristics to catch
    common variations (e.g., "nodejs" / "node.js").
    """
    if not text:
        return []

    txt = text.lower()
    found = set()

    for skill in SKILLS:
        s = skill.lower()
        pattern = None
        if s == "c++":
            pattern = r"\bc\+\+\b"
        elif s == "node.js":
            pattern = r"\bnode(?:\.js|js)?\b"
        elif s == "scikit-learn":
            pattern = r"scikit[- ]?learn"
        elif s in ("machine learning", "deep learning", "computer vision"):
            pattern = r"\b" + re.escape(s) + r"\b"
        else:
            pattern = r"\b" + re.escape(s) + r"\b"

        if re.search(pattern, txt, flags=re.IGNORECASE):
            found.add(skill)

    # return deterministic sorted list
    return sorted(found)
