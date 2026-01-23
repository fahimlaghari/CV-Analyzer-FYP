from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.utils import secure_filename
from app.models import db, UserData, Contact

from app.utils import extract_text_from_pdf, extract_text_from_docx, extract_skills, calculate_score, get_job_recommendations
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return redirect(url_for('main.home'))
    
    file = request.files['resume']
    if file.filename == '':
        return redirect(url_for('main.home'))

    
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        
        text = ""
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(filepath)

        
        skills = extract_skills(text)
        score = calculate_score(skills)
        jobs = get_job_recommendations(skills)

        new_data = UserData(filename=filename, skills=", ".join(skills), score=score)
        db.session.add(new_data)
        db.session.commit()
        
        return render_template('index.html', skills=skills, score=score, filename=filename, jd_match=None, jobs=jobs)
    
    return redirect(url_for('main.home'))

@main.route('/build-resume')
def build_resume():
    return render_template('builder_form.html')


@main.route('/ai-write', methods=['POST'])
def ai_write():
    
    data = request.get_json()
    job_title = data.get('job_title', 'Professional')

    summary = f"Highly motivated {job_title} with experience in developing scalable solutions. Adept at problem-solving and teamwork."
    desc = "• Developed and maintained code for various applications.\n• Collaborated with cross-functional teams to define features.\n• Optimized application performance and fixed bugs."

    return jsonify({'summary': summary, 'description': desc})

@main.route('/generate-cv', methods=['POST'])
def generate_cv():
    profile_pic_filename = None
    if 'profile_pic' in request.files:
        pic = request.files['profile_pic']
        if pic.filename != '':
            filename = secure_filename(pic.filename)
            pics_folder = os.path.join(current_app.root_path, 'static/profile_pics')
            os.makedirs(pics_folder, exist_ok=True)
            pic.save(os.path.join(pics_folder, filename))
            profile_pic_filename = filename

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    duration_text = ""
    
    if start_date and end_date:
        duration_text = f"{start_date} to {end_date}"
    elif start_date:
        duration_text = f"{start_date} - Present"
    else:
        duration_text = request.form.get('duration', '')

    data = {
        'name': request.form.get('name'),
        'designation': request.form.get('designation'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'summary': request.form.get('summary'),
        'skills': request.form.get('skills'),
        'company': request.form.get('company'),
        'duration': duration_text,
        'job_desc': request.form.get('job_desc'),
        'degree': request.form.get('degree'),
        'university': request.form.get('university'),
        'profile_pic': profile_pic_filename 
    }
    tid = request.form.get('template_id', '1')

    if tid == '1':
        return render_template('modern.html', data=data)
    elif tid == '2':
        return render_template('classic.html', data=data)
    elif tid == '3':
        return render_template('creative.html', data=data)
    else:
        return render_template('modern.html', data=data)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    success_msg = None
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            msg = request.form.get('message')
            new_msg = Contact(name=name, email=email, message=msg)
            db.session.add(new_msg)
            db.session.commit()
            success_msg = "Message sent successfully!"
        except Exception as e:
            success_msg = f"Error: {str(e)}"
    return render_template('contact.html', success=success_msg)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'fahim' and request.form.get('password') == 'Fahim@2025':
            session['logged_in'] = True
            return redirect(url_for('main.admin'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html')

@main.route('/admin')
def admin():
    if not session.get('logged_in'): return redirect(url_for('main.login'))
    try:
        cv_data = UserData.query.order_by(UserData.upload_date.desc()).all()
        messages = Contact.query.order_by(Contact.date_sent.desc()).all()
        return render_template('admin.html', data=cv_data, messages=messages, stats={'total': len(cv_data), 'total_msgs': len(messages)})
    except Exception as e:
        return f"Error: {str(e)}"

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('main.home'))
