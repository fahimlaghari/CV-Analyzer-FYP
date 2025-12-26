import pdfplumber
from pdfminer.high_level import extract_text
import re
import urllib.parse

# --- SKILLS CONFIGURATION ---
# Listing all major tech stacks here.
# Added variations like ReactJS/React to catch inconsistencies.
DB_SKILLS = [
    # Core Programming
    'Python', 'Java', 'C++', 'C#', 'C', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Go', 'Rust', 'Matlab',
    
    # Web Tech (Frontend/Backend)
    'HTML', 'HTML5', 'CSS', 'CSS3', 'JavaScript', 'JS', 'TypeScript', 
    'React', 'ReactJS', 'React.js', 'Angular', 'AngularJS', 'Vue', 'Next.js', 
    'Node.js', 'NodeJS', 'Express', 'Django', 'Flask', 'Laravel', 'Bootstrap', 'Tailwind', 'jQuery',
    
    # Databases
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Firebase', 'Redis',
    
    # Data Science & AI
    'Machine Learning', 'Deep Learning', 'Data Science', 'Pandas', 'NumPy', 'TensorFlow', 'Keras', 'PyTorch', 
    'Excel', 'Power BI', 'Tableau',
    
    # DevOps & Tools
    'Git', 'GitHub', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux', 'Jira', 'Figma', 'Canva', 'Photoshop',
    
    # Soft Skills
    'Communication', 'Teamwork', 'Leadership', 'Problem Solving', 'Time Management', 'English', 'Urdu', 
    'Writing', 'Presentation', 'Critical Thinking'
]

def extract_text_from_pdf(file_path):
    """
    Hybrid extraction: Tries pdfplumber first (better for columns),
    fallbacks to pdfminer if that fails.
    """
    text = ""
    
    # Method 1: Try pdfplumber (Good for Canva/Modern layouts)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        # Just logging error, will try next method
        print(f"pdfplumber failed: {e}")

    # Method 2: Fallback to pdfminer if text is empty or too short
    # This handles older or weirdly encoded PDFs
    if not text or len(text) < 50:
        try:
            text = extract_text(file_path)
        except Exception:
            pass # Agar ye b fail hua to empty string return hogi
            
    return text

def extract_skills(text):
    found_skills = []
    
    # PRE-PROCESSING (Crucial Step)
    # converting to lower case to make matching easier
    text_lower = text.lower()
    
    # Replacing separators with spaces is important.
    # Otherwise 'PHP|Java' becomes one word and detection fails.
    text_lower = text_lower.replace('|', ' ')
    text_lower = text_lower.replace('•', ' ')
    text_lower = text_lower.replace('/', ' ')
    text_lower = text_lower.replace(',', ' ')
    text_lower = text_lower.replace('\n', ' ') # removing line breaks
    
    # Debug print to check what the code is actually reading
    # print(f"DEBUG TEXT: {text_lower[:100]}...") 
    
    for skill in DB_SKILLS:
        # Handling special cases like C++ and C# which contain symbols
        if skill in ['C++', 'C#', '.NET']:
            # checking with spaces to avoid partial matches
            if f" {skill.lower()} " in f" {text_lower} ": 
                found_skills.append(skill)
        else:
            # Using Regex for strict whole-word matching
            # This prevents 'Java' matching inside 'Javascript'
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
                
    # Using set to remove duplicates, then converting back to list
    return list(set(found_skills))

def calculate_score(skills_count):
    # Base logic: 0 skills = 0 score (No free marks)
    if skills_count == 0:
        return 0
    
    # 5 points per skill
    score = skills_count * 5
    
    # Adding bonus for versatility
    if skills_count > 5:
        score += 10
    if skills_count > 10:
        score += 10
        
    # Capping score at 100
    if score > 100:
        score = 100
        
    return score

def get_job_links(skills):
    jobs = []
    if not skills:
        return jobs
        
    # Pick top 3 skills to generate links
    top_skills = skills[:3]
    
    for skill in top_skills:
        safe_skill = urllib.parse.quote(skill)
        
        # Generating dynamic links for LinkedIn and Indeed
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