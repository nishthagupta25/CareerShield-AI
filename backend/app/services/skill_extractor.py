from typing import Dict, List, Set
import spacy
from spacy.matcher import PhraseMatcher


# Standard skill name -> possible phrases/synonyms
SKILL_ONTOLOGY: Dict[str, List[str]] = {
    "Python": ["python", "python programming"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "JavaScript": ["javascript", "js"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],

    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express.js": ["express", "express.js"],
    "FastAPI": ["fastapi", "fast api"],
    "Flask": ["flask"],
    "Django": ["django"],

    "REST API": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
        "api development",
        "backend api",
        "backend apis",
        "scalable apis",
        "api services",
    ],

    "Backend Development": [
        "backend",
        "backend development",
        "backend services",
        "server side",
        "server-side development",
        "ml backend engineer",
    ],

    "Frontend Development": [
        "frontend",
        "frontend development",
        "responsive ui",
        "web ui",
    ],

    "SQL": [
        "sql",
        "mysql",
        "postgresql",
        "relational database",
        "relational databases",
        "sql databases",
        "database queries",
    ],

    "MongoDB": ["mongodb", "mongo db", "nosql"],

    "Machine Learning": [
        "machine learning",
        "ml",
        "ml models",
        "predictive models",
        "model development",
        "classification models",
        "recommendation systems",
    ],

    "Deep Learning": [
        "deep learning",
        "neural networks",
        "cnn",
        "rnn",
        "lstm",
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "ai",
        "ai applications",
        "ai engineer",
        "intelligent systems",
    ],

    "NLP": [
        "nlp",
        "natural language processing",
        "text classification",
        "text analytics",
        "language models",
        "transformers",
        "sentence transformers",
    ],

    "Computer Vision": [
        "computer vision",
        "image processing",
        "object detection",
    ],

    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "Scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Hugging Face": ["hugging face", "huggingface", "transformers library"],

    "Docker": [
        "docker",
        "containerization",
        "containers",
        "containerized",
    ],

    "Git": ["git", "github", "version control"],
    "AWS": ["aws", "amazon web services"],
    "Cloud": ["cloud", "cloud deployment", "cloud services"],

    "Data Analysis": [
        "data analysis",
        "analytics",
        "data analytics",
        "dashboard development",
    ],

    "Data Visualization": [
        "data visualization",
        "visualization",
        "power bi",
        "tableau",
        "dashboards",
    ],

    "Statistics": ["statistics", "statistical analysis"],
    "Excel": ["excel", "microsoft excel"],

    "Model Deployment": [
        "model deployment",
        "deploy models",
        "deployed models",
        "deploying machine learning applications",
        "ml deployment",
    ],
}


_nlp = spacy.blank("en")
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")


def _build_matcher() -> None:
    for standard_skill, phrases in SKILL_ONTOLOGY.items():
        patterns = [_nlp.make_doc(phrase) for phrase in phrases]
        _matcher.add(standard_skill, patterns)


_build_matcher()


def extract_skills(text: str) -> List[str]:
    """
    Extracts normalized technical skills from resume/job text.

    Uses:
    - spaCy PhraseMatcher
    - skill ontology
    - synonym normalization

    Example:
    "containerization" -> Docker
    "predictive models" -> Machine Learning
    "relational databases" -> SQL
    """

    if not text:
        return []

    doc = _nlp(text)
    matches = _matcher(doc)

    found: Set[str] = set()

    for match_id, start, end in matches:
        skill_name = _nlp.vocab.strings[match_id]
        found.add(skill_name)

    return sorted(found)