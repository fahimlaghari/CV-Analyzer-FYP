import pdfplumber
from pdfminer.high_level import extract_text
import re
import urllib.parse

# List of skills to detect
DB_SKILLS = [
    'Python', 'Java', 'C++', 'C#', 'C', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Go', 'Rust', 'Matlab',
    'HTML', 'HTML5', 'CSS', 'CSS3', 'JavaScript', 'JS', 'TypeScript', 
    'React', 'ReactJS', 'React.js', 'Angular', 'AngularJS', 'Vue', 'Next.js', 
    'Node.js', 'NodeJS', 'Express', 'Django', 'Flask', 'Laravel', 'Bootstrap', 'Tailwind', 'jQuery',
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Firebase',
    'Machine Learning', 'Deep Learning', 'Data Science', 'Pandas', 'NumPy', 'TensorFlow', 'Keras', 'PyTorch', 
    'Excel', 'Power BI', 'Tableau',
    'Git', 'GitHub', 'Docker', 'AWS', 'Azure', 'Linux', 'Jira', 'Figma', 'Canva', 'Photoshop',
    'Communication', 'Teamwork', 'Leadership', 'Problem Solving', 'Time Management', 'English', 'Urdu', 
    'Writing', 'Presentation'
]

def extract_text_from_pdf(file_path):
    # Try reading with pdfplumber first (good for columns)
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception:
        pass

    # Fallback to pdfminer if text is empty
    if not text or len(text) < 50:
        try:
            text = extract_text(file_path)
        except Exception:
            pass
            
    return text

def extract_skills(text):
    found_skills = []
    # clean text for better matching
    text_lower = text.lower().replace('|', ' ').replace('•', ' ').replace('\n', ' ')
    
    for skill in DB_SKILLS:
        # check for exact word match
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        
        # special handling for C++ and C#
        if skill in ['C++', 'C#', '.NET']:
            if f" {skill.lower()} " in f" {text_lower} ": 
                found_skills.append(skill)
        elif re.search(pattern, text_lower):
            found_skills.append(skill)
                
    return list(set(found_skills))

def calculate_score(skills_count):
    if skills_count == 0:
        return 0
    
    # 5 points per skill
    score = skills_count * 5
    
    # bonus points
    if skills_count > 5:
        score += 10
    if skills_count > 10:
        score += 10
        
    return min(score, 100)

def get_job_links(skills):
    jobs = []
    if not skills:
        return jobs
        
    # get top 3 skills
    for skill in skills[:3]:
        safe_skill = urllib.parse.quote(skill)
        jobs.append({
            "title": f"{skill} Jobs",
            "company": "LinkedIn",
            "link": f"https://www.linkedin.com/jobs/search/?keywords={safe_skill}",
            "site": "LinkedIn"
        })
        jobs.append({
            "title": f"Hiring: {skill}",
            "company": "Indeed PK",
            "link": f"https://pk.indeed.com/jobs?q={safe_skill}",
            "site": "Indeed"
        })
    return jobs

def match_job_description(cv_text, job_description):
    if not job_description:
        return None, []
    
    # helper function to clean text
    def clean(text):
        return set(text.lower().replace('|', ' ').replace('\n', ' ').split())

    cv_words = clean(cv_text)
    jd_words = clean(job_description)
    
    # find intersection
    common_words = cv_words.intersection(jd_words)
    
    if len(jd_words) == 0:
        match_percentage = 0
    else:
        match_percentage = round((len(common_words) / len(jd_words)) * 100)
    
    # find missing skills from our DB list
    missing_raw = jd_words - cv_words
    db_skills_lower = [s.lower() for s in DB_SKILLS]
    
    missing_keywords = [word for word in missing_raw if word in db_skills_lower]
    
    return match_percentage, missing_keywords