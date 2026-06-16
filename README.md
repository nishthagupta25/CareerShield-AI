# 🛡️ CareerShield AI

### Detect Job Scams. Analyze Opportunities. Apply Smarter.

CareerShield AI is an AI-powered job opportunity analysis platform that helps students and job seekers identify recruitment scams, evaluate job opportunities, analyze recruiter credibility, and understand resume-job alignment before applying.

---

## 📸 Dashboard Preview

### Home Dashboard

![Dashboard](assets/dashboard.png)

### Analysis Results

![Analysis](assets/analysis.png)

---

## 🚨 Why CareerShield AI?

Every year, thousands of students and fresh graduates lose money, personal information, and valuable opportunities because of:

* Fake internships
* Registration fee scams
* Upfront payment frauds
* Fake recruiter emails
* Unrealistic salary promises
* Work-from-home scams

CareerShield AI acts as a first layer of verification before candidates apply.

---

## ✨ Key Features

### 🔍 Scam Detection Engine

Detects common recruitment scam patterns such as:

* Registration fee requests
* Upfront payment demands
* Free email providers
* Suspicious salary claims
* Vague job descriptions
* Missing company information
* Immediate joining pressure

### 📊 Opportunity Intelligence

Generates:

* Trust Score
* Scam Risk Score
* Resume Match Score
* Opportunity Score

### 🎯 Skill Gap Analysis

Identifies:

* Matching Skills
* Missing Skills
* Resume Gaps
* Improvement Areas

### 🤖 AI Career Advisor

Provides:

* Personalized recommendations
* Risk explanations
* Career guidance
* Resume improvement suggestions

### 📄 Professional PDF Reports

Export detailed analysis reports containing:

* Opportunity assessment
* Risk analysis
* Skill evaluation
* Career recommendations

---

## 📈 Example Analysis

### Input

Recruiter Email:
[recruiter@gmail.com](mailto:recruiter@gmail.com)

Salary:
₹95,000/month

Recruiter Message:
"Pay ₹499 registration fee to confirm your interview slot."

### Output

❌ Recommendation: Avoid

⚠️ Scam Risk Score: 100/100

🚩 Red Flags Detected:

* Registration Fee Required
* Free Email Provider
* Suspicious Salary
* Immediate Joining Pressure

---

## ⚙️ How It Works

```text
User Input
     │
     ▼
CareerShield Analysis Engine
     ├── Scam Detection
     ├── Resume Matching
     ├── Skill Extraction
     └── Opportunity Scoring
     │
     ▼
AI Career Advisor
     │
     ▼
Interactive Dashboard + PDF Report
```

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript

### Backend

* Python
* FastAPI
* Uvicorn

### Reporting

* ReportLab

---

## 📁 Project Structure

```text
CareerShield-AI/
│
├── assets/
│   ├── dashboard.png
│   └── analysis.png
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/nishthagupta25/CareerShield-AI.git
cd CareerShield-AI
```

### Setup Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

### Run Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

### Launch Frontend

Open:

```text
frontend/index.html
```

in your browser.

---

## 🚀 Future Enhancements (Version 2)

* ML-based scam classification
* Company verification engine
* Recruiter trust database
* LinkedIn job analysis
* Resume PDF parsing
* Analysis history dashboard
* NLP-powered resume parsing

---

## 👩‍💻 Developer

**Nishtha Gupta**

---

> Every opportunity deserves verification before application.
