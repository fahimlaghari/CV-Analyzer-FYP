from flask import Blueprint, render_template, request, current_app, redirect, url_for, session
from app import db
from app.models import UserData
from app.utils import extract_text_from_pdf, extract_skills, get_job_links, calculate_score, match_job_description
import os
import time

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    extracted_text = ""
    found_skills = []
    recommended_jobs = []
    resume_score = 0
    jd_match = None
    missing_keywords = []
    
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return redirect(request.url)
        
        file = request.files['cv_file']
        job_description = request.form.get('job_description')
        
        if file.filename != '' and file.filename.endswith('.pdf'):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "temp_cv.pdf")
            file.save(file_path)

            try:
                extracted_text = extract_text_from_pdf(file_path)
                found_skills = extract_skills(extracted_text)
                resume_score = calculate_score(len(found_skills))
                recommended_jobs = get_job_links(found_skills)
                
                if job_description:
                    jd_match, missing_keywords = match_job_description(extracted_text, job_description)

                skills_str = ", ".join(found_skills)
                new_entry = UserData(filename=file.filename, skills=skills_str, score=resume_score)
                db.session.add(new_entry)
                db.session.commit()
                
            except Exception:
                pass
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

            time.sleep(2)

    return render_template('index.html', 
                         text=extracted_text, 
                         skills=found_skills, 
                         jobs=recommended_jobs,
                         score=resume_score,
                         jd_match=jd_match,
                         missing_keywords=missing_keywords)

@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'fahim' and password == 'Fahim@2025':
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('main.admin'))
        else:
            error = "Invalid Credentials"
            
    return render_template('login.html', error=error)

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.home'))

@main.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    try:
        data = UserData.query.order_by(UserData.upload_date.desc()).all()
        
        total_cvs = len(data)
        avg_score = 0
        
        if total_cvs > 0:
            valid_scores = [d.score for d in data if d.score is not None]
            if valid_scores:
                avg_score = round(sum(valid_scores) / len(valid_scores))
        
        stats = {
            'total': total_cvs,
            'avg_score': avg_score
        }
        
        return render_template('admin.html', data=data, stats=stats)

    except Exception:
        return "Error loading dashboard"

@main.route('/build-resume', methods=['GET', 'POST'])
def build_resume():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        skills = request.form.get('skills')
        experience = request.form.get('experience')
        education = request.form.get('education')
        template_choice = request.form.get('template')
        
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'role': role,
            'skills': skills.split(',') if skills else [],
            'experience': experience,
            'education': education,
            'template': template_choice
        }
        
        return render_template('resume_preview.html', data=user_data)

    return render_template('builder_form.html')