from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy  # Database library
from datetime import datetime            # Time save karne k liye
import os
from utils import extract_text_from_pdf, extract_skills, get_job_links, calculate_score

app = Flask(__name__)

# --- DATABASE CONFIGURATION (MySQL XAMPP) ---
# Format: mysql+pymysql://username:password@server/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cv_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE TABLE DESIGN ---
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    skills = db.Column(db.String(500))
    score = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CV {self.filename}>'

# Upload folder setting
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# App shuru hone se pehle Database create karein
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    extracted_text = ""
    found_skills = []
    recommended_jobs = []
    resume_score = 0
    
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return "No file uploaded"
        
        file = request.files['cv_file']
        
        if file.filename != '' and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_cv.pdf")
            file.save(file_path)

            # --- UTILS LOGIC ---
            extracted_text = extract_text_from_pdf(file_path)
            found_skills = extract_skills(extracted_text)
            resume_score = calculate_score(len(found_skills))
            recommended_jobs = get_job_links(found_skills)
            
            # --- SAVE TO DATABASE ---
            try:
                skills_str = ", ".join(found_skills)
                
                new_entry = UserData(
                    filename=file.filename,
                    skills=skills_str,
                    score=resume_score
                )
                db.session.add(new_entry)
                db.session.commit()
                print("✅ Data Saved to Database Successfully!")
            except Exception as e:
                print(f"❌ Database Error: {e}")

            if os.path.exists(file_path):
                os.remove(file_path)

    return render_template('index.html', 
                         text=extracted_text, 
                         skills=found_skills, 
                         jobs=recommended_jobs,
                         score=resume_score)

# --- NEW UPDATED ADMIN PAGE (Statistics wala) ---
@app.route('/admin')
def admin():
    try:
        # 1. Sara Data nikala
        all_data = UserData.query.order_by(UserData.upload_date.desc()).all()
        
        # 2. Total CVs ginti ki
        total_cvs = len(all_data)
        
        # 3. Average Score nikala
        if total_cvs > 0:
            total_score = sum(entry.score for entry in all_data)
            avg_score = round(total_score / total_cvs)
        else:
            avg_score = 0
            
    except Exception as e:
        all_data = []
        total_cvs = 0
        avg_score = 0
        print(f"Error: {e}")
        
    # Ab hum data k sath sath 'total' aur 'average' bhi bhej rahe hain HTML ko
    return render_template('admin.html', data=all_data, total=total_cvs, average=avg_score)

if __name__ == '__main__':
    app.run(debug=True)