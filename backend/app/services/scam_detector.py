import re
from typing import List, Dict


def _find_amount(s: str):
    if not s:
        return None
    # look for patterns like $50,000 or 50k or 50000
    s = s.replace(',', '')
    m = re.search(r"\$\s*([0-9]+)", s)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    m = re.search(r"([0-9]+)\s*[kK]", s)
    if m:
        try:
            return int(m.group(1)) * 1000
        except Exception:
            return None
    m = re.search(r"([0-9]{4,})", s)
    if m:
        try:
            return int(m.group(1))
        except Exception:
            return None
    return None


def detect_red_flags(job_text: str, recruiter_message: str, email: str, salary: str) -> List[Dict]:
    """Return a list of red-flag dicts for a given job posting / recruiter message."""
    flags = []
    job_text = (job_text or "").lower()
    recruiter_message = (recruiter_message or "").lower()
    email = (email or "").strip()
    salary = (salary or "").lower()

    combined = f"{job_text} {recruiter_message}"

    def add(title, severity, reason):
        flags.append({"title": title, "severity": severity, "reason": reason})

    # 1. Money/security deposit/training fee
    money_keywords = [
        "security deposit",
        "training fee",
        "pay",
        "deposit",
        "transfer",
        "wire",
        "send money",
        "upfront payment",
        "processing fee",
        "payment required",
        "payment before",
    ]
    if any(k in combined for k in money_keywords):
        add(
            "Upfront Payment / Deposit Requested",
            "high",
            "The message asks or mentions sending money or paying a fee before selection or onboarding.",
        )

    # 2. Registration fee
    if any(k in combined for k in ["registration fee", "register fee", "registration charges"]):
        add(
            "Registration Fee Required",
            "high",
            "The message asks the candidate to pay a registration fee.",
        )

    # 3. Gmail/Yahoo/Outlook instead of company domain
    if email:
        try:
            domain = email.split("@")[1].lower()
            free_providers = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"]
            if domain in free_providers:
                add(
                    "Free Email Provider Used",
                    "medium",
                    f"Recruiter email uses a free provider ({domain}) instead of a company domain.",
                )
        except Exception:
            pass

    # 4. Unrealistic salary
    amt = _find_amount(salary) or _find_amount(combined)
    if amt:
        if amt >= 100000:
            add(
                "Unrealistic Salary Offered",
                "high",
                f"The advertised salary amount ({amt}) looks unusually high and may be a lure.",
            )
        elif amt >= 50000:
            add(
                "Suspiciously High Salary",
                "medium",
                f"The advertised salary amount ({amt}) is high for many entry-level roles; verify the offer.",
            )

    # 5. Vague job description
    keywords_present = sum(1 for k in ["responsibilities", "requirements", "location", "company", "role", "experience", "skills"] if k in job_text)
    if len(job_text.strip()) < 100 or keywords_present <= 1:
        add(
            "Vague Job Description",
            "high",
            "The job posting lacks clear responsibilities, requirements, or company/location details.",
        )

    # 6. Urgent/immediate joining pressure
    urgent_phrases = ["urgent", "immediately", "asap", "join immediately", "start immediately", "urgent hiring"]
    if any(p in combined for p in urgent_phrases):
        add(
            "Immediate Joining Pressure",
            "medium",
            "The message pressures candidates to join or respond immediately, which is a common scam tactic.",
        )

    # 7. Work-from-home scam phrases
    wfh_phrases = ["work from home and earn", "earn from home", "easy money", "work from home", "no experience required"]
    if any(p in combined for p in wfh_phrases):
        add(
            "Work-from-Home / Easy Money Claims",
            "medium",
            "The listing promises easy earnings or work-from-home schemes often used by scammers.",
        )

    # 8. Poor grammar / spammy words
    spammy = ["congratulations", "winner", "click here", "apply now", "!!!", "limited slots"]
    if any(p in combined for p in spammy) or combined.count("!") >= 3:
        add(
            "Spammy / Poorly Written Message",
            "low",
            "The message contains spammy language, excessive punctuation, or poor grammar.",
        )

    # 9. No company details
    if "company" not in job_text and "about us" not in job_text and "http" not in job_text and (not email or ("@" in email and (email.split("@")[1] in ["gmail.com","yahoo.com","outlook.com","hotmail.com","aol.com"]))):
        add(
            "No Company Details",
            "medium",
            "The posting does not provide verifiable company information such as website, company name, or domain.",
        )

    # deduplicate by title
    seen = set()
    deduped = []
    for f in flags:
        if f["title"] not in seen:
            deduped.append(f)
            seen.add(f["title"])

    return deduped
