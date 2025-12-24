# 📄 CV Analyzer & Job Recommendation System

## 📌 Project Overview
This is a Final Year Project (FYP) developed to help students and job seekers analyze their resumes. The system extracts text from uploaded PDF resumes, identifies key technical and soft skills, calculates a "Resume Strength Score," and recommends real-time jobs from LinkedIn and Indeed.

## 🚀 Key Features
- **PDF Parsing:** Extracts text automatically from PDF documents.
- **Skill Extraction:** Identifies 100+ technical and soft skills using NLP techniques.
- **Smart Scoring:** Calculates a resume score (0-100) based on skill density.
- **Job Recommendation:** Generates real-time search links for LinkedIn & Indeed.
- **Database Integration:** Saves user data, skills, and scores in **MySQL Database**.
- **Admin Dashboard:** A secured panel to view uploaded CV statistics.

## 🛠️ Tech Stack
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Backend:** Python (Flask)
- **Database:** MySQL (via XAMPP)
- **Libraries:** PDFMiner.six, PyMySQL, SQLAlchemy

## ⚙️ How to Run Locally

1. **Clone the Project**
   Extract the folder to your desired location.

2. **Install Dependencies**
   Open terminal and run:
   ```bash
   pip install -r requirements.txt