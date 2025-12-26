from flask import Blueprint, render_template, request, current_app, redirect, url_for, session, flash
from app import db
from app.models import UserData
from app.utils import extract_text_from_pdf, extract_skills, get_job_links, calculate_score
import os
import time

main = Blueprint('main', __name__)

# --- HOME PAGE ---
@main.route('/', methods=['GET', 'POST'])
def home():
    extracted_text = ""
    found_skills = []
    recommended_jobs = []
    resume_score = 0
    
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return redirect(request.url)
        
        file = request.files['cv_file']
        
        if file.filename != '' and file.filename.endswith('.pdf'):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "temp_cv.pdf")
            file.save(file_path)

            try:
                extracted_text = extract_text_from_pdf(file_path)
                found_skills = extract_skills(extracted_text)
                resume_score = calculate_score(len(found_skills))
                recommended_jobs = get_job_links(found_skills)
                
                # Save to DB
                skills_str = ", ".join(found_skills)
                new_entry = UserData(filename=file.filename, skills=skills_str, score=resume_score)
                db.session.add(new_entry)
                db.session.commit()
                
            except Exception as e:
                print(f"Error: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)

            time.sleep(2) # Animation Delay

    return render_template('index.html', 
                         text=extracted_text, 
                         skills=found_skills, 
                         jobs=recommended_jobs,
                         score=resume_score)

# --- LOGIN PAGE (New) ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded Password for FYP (Simple & Secure)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('main.admin'))
        else:
            error = "Wrong Username or Password!"
            
    return render_template('login.html', error=error)

# --- LOGOUT (New) ---
@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.home'))

# --- PROTECTED ADMIN PANEL ---
# --- PROTECTED ADMIN PANEL (Crash Proof) ---
@main.route('/admin')
def admin():
    # 1. Security Check
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    try:
        # 2. Data Fetching
        data = UserData.query.order_by(UserData.upload_date.desc()).all()
        total_cvs = len(data)
        avg_score = 0

        # 3. Safe Calculation (Error se bachne k liye)
        if total_cvs > 0:
            # Sirf wo scores lo jo None (khali) na hon
            valid_scores = [d.score for d in data if d.score is not None]
            if valid_scores:
                avg_score = round(sum(valid_scores) / len(valid_scores))

        # 4. Stats Dictionary
        stats = {
            'total': total_cvs,
            'avg_score': avg_score
        }
        
        return render_template('admin.html', data=data, stats=stats)

    except Exception as e:
        # Agar koi bhi error aaye to Terminal mein print karo
        print(f"❌ Admin Error: {e}")
        return f"Error loading Admin Panel: {e}"