import re
from typing import List, Dict


FREE_EMAIL_PROVIDERS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "aol.com",
}


def _find_amount(s: str):
    if not s:
        return None

    s = s.replace(",", "")

    m = re.search(r"(?:₹|rs\.?|inr|\$)\s*([0-9]+)", s, re.I)
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


def _domain_from_email(email: str) -> str:
    email = (email or "").strip().lower()
    if "@" not in email:
        return ""
    return email.split("@")[-1].strip()


def _contains_any(text: str, phrases: List[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _has_safe_payment_context(text: str) -> bool:
    safe_phrases = [
        "no registration fee",
        "no registration fees",
        "no fee required",
        "no fees required",
        "no charges to apply",
        "there are no charges",
        "free to apply",
        "no payment required",
        "no application fee",
        "do not pay",
        "dont pay",
        "don't pay",
        "never pay",
        "no money required",
        "no upfront payment",
        "no processing fee",
    ]

    return _contains_any(text, safe_phrases)


def _has_payment_request(text: str) -> bool:
    if _has_safe_payment_context(text):
        return False

    risky_phrases = [
        "security deposit",
        "training fee",
        "registration fee",
        "application fee",
        "processing fee",
        "refundable fee",
        "pay registration",
        "pay fee",
        "pay now",
        "pay immediately",
        "payment required",
        "payment before joining",
        "payment before selection",
        "deposit required",
        "send money",
        "wire money",
        "bank transfer",
        "upi payment",
        "advance payment",
        "pay to confirm",
        "pay to get interview",
        "pay for offer letter",
        "pay for onboarding",
    ]

    return _contains_any(text, risky_phrases)


def _has_registration_fee(text: str) -> bool:
    if _has_safe_payment_context(text):
        return False

    risky_phrases = [
        "registration fee",
        "application fee",
        "processing fee",
        "pay registration",
        "pay fee",
        "fee required",
        "refundable fee",
    ]

    return _contains_any(text, risky_phrases)


def _has_urgency_pressure(text: str) -> bool:
    safe_phrases = [
        "within 5 days",
        "within five days",
        "within 7 days",
        "within seven days",
        "deadline",
        "application deadline",
        "assessment deadline",
    ]

    if _contains_any(text, safe_phrases):
        return False

    risky_phrases = [
        "urgent",
        "immediately",
        "asap",
        "join immediately",
        "start immediately",
        "urgent hiring",
        "reply immediately",
        "pay today",
        "limited slots",
        "today only",
    ]

    return _contains_any(text, risky_phrases)


def _has_wfh_easy_money_claim(text: str) -> bool:
    risky_phrases = [
        "work from home and earn",
        "earn from home",
        "easy money",
        "earn money daily",
        "daily payout",
        "no work required",
        "earn 5000 daily",
        "earn 10000 daily",
    ]

    if _contains_any(text, risky_phrases):
        return True

    # "work from home" alone is not always scam.
    if "work from home" in text and (
        "earn" in text or "no experience required" in text or "easy" in text
    ):
        return True

    return False


def _has_spammy_message(text: str) -> bool:
    risky_phrases = [
        "winner",
        "click here",
        "limited slots",
        "selected without interview",
        "guaranteed job",
        "guaranteed selection",
    ]

    if _contains_any(text, risky_phrases):
        return True

    # "Congratulations" alone is common in real hiring, so only flag it with risky context.
    if "congratulations" in text and (
        "pay" in text
        or "fee" in text
        or "whatsapp" in text
        or "selected without interview" in text
    ):
        return True

    if text.count("!") >= 3:
        return True

    return False


def _has_vague_job_description(job_text: str) -> bool:
    job_text = (job_text or "").lower().strip()

    if len(job_text) < 80:
        return True

    keywords = [
        "responsibilities",
        "requirements",
        "location",
        "company",
        "role",
        "experience",
        "skills",
        "qualification",
        "ctc",
        "salary",
        "interview",
        "developer",
        "engineer",
        "intern",
    ]

    keywords_present = sum(1 for k in keywords if k in job_text)

    return keywords_present <= 1


def _has_no_company_details(job_text: str, email: str) -> bool:
    job_text = (job_text or "").lower()
    domain = _domain_from_email(email)

    has_company_text = any(
        x in job_text
        for x in [
            "company",
            "about us",
            "technologies",
            "solutions",
            "private limited",
            "pvt ltd",
            "ltd",
            "inc",
            "corp",
            "official",
            "careers portal",
            "website",
            "http",
        ]
    )

    has_company_email = bool(domain) and domain not in FREE_EMAIL_PROVIDERS

    return not has_company_text and not has_company_email


def detect_red_flags(
    job_text: str,
    recruiter_message: str,
    email: str,
    salary: str,
) -> List[Dict]:
    flags = []

    job_text = (job_text or "").lower()
    recruiter_message = (recruiter_message or "").lower()
    email = (email or "").strip()
    salary = (salary or "").lower()

    combined = f"{job_text} {recruiter_message}".strip()

    def add(title, severity, reason):
        flags.append(
            {
                "title": title,
                "severity": severity,
                "reason": reason,
            }
        )

    if _has_payment_request(combined):
        add(
            "Upfront Payment / Deposit Requested",
            "high",
            "The message asks or mentions sending money or paying a fee before selection or onboarding.",
        )

    if _has_registration_fee(combined):
        add(
            "Registration Fee Required",
            "high",
            "The message asks the candidate to pay a registration fee.",
        )

    domain = _domain_from_email(email)
    if domain in FREE_EMAIL_PROVIDERS:
        add(
            "Free Email Provider Used",
            "medium",
            f"Recruiter email uses a free provider ({domain}) instead of a company domain.",
        )

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

    if _has_vague_job_description(job_text):
        add(
            "Vague Job Description",
            "high",
            "The job posting lacks clear responsibilities, requirements, or company/location details.",
        )

    if _has_urgency_pressure(combined):
        add(
            "Immediate Joining Pressure",
            "medium",
            "The message pressures candidates to join or respond immediately, which is a common scam tactic.",
        )

    if _has_wfh_easy_money_claim(combined):
        add(
            "Work-from-Home / Easy Money Claims",
            "medium",
            "The listing promises easy earnings or work-from-home schemes often used by scammers.",
        )

    if _has_spammy_message(combined):
        add(
            "Spammy / Poorly Written Message",
            "low",
            "The message contains spammy language, excessive punctuation, or poor grammar.",
        )

    if _has_no_company_details(job_text, email):
        add(
            "No Company Details",
            "medium",
            "The posting does not provide verifiable company information such as website, company name, or domain.",
        )

    seen = set()
    deduped = []

    for flag in flags:
        if flag["title"] not in seen:
            deduped.append(flag)
            seen.add(flag["title"])

    return deduped