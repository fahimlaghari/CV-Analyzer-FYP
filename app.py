from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy  # Database library
from datetime import datetime            # Time save karne k liye
import os
from utils import extract_text_from_pdf, extract_skills, get_job_links, calculate_score

app = Flask(__name__)

# --- DATABASE CONFIGURATION (MySQL XAMPP) ---
# Ye line ab MySQL se connect karegi
# Format: mysql+pymysql://username:password@server/databasename
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cv_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE TABLE DESIGN ---
# Hum database ko bata rahe hain k humein kya kya save karna hai
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    skills = db.Column(db.String(500))  # Skills text ki tarah save hongi
    score = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CV {self.filename}>'

# Upload folder setting
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# App shuru hone se pehle Database create karein (Agar table nahi hai to bana dega)
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
            # File ko save kia
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_cv.pdf")
            file.save(file_path)

            # --- UTILS LOGIC ---
            extracted_text = extract_text_from_pdf(file_path)
            found_skills = extract_skills(extracted_text)
            resume_score = calculate_score(len(found_skills))
            recommended_jobs = get_job_links(found_skills)
            
            # --- SAVE TO MYSQL DATABASE ---
            try:
                # Skills list ko string mein convert kr k save kr rahe hain
                skills_str = ", ".join(found_skills)
                
                new_entry = UserData(
                    filename=file.filename,
                    skills=skills_str,
                    score=resume_score
                )
                db.session.add(new_entry)
                db.session.commit()
                print("✅ Data Saved to MySQL Database Successfully!")
            except Exception as e:
                print(f"❌ Database Error: {e}")

            # Temp file delete
            if os.path.exists(file_path):
                os.remove(file_path)

    return render_template('index.html', 
                         text=extracted_text, 
                         skills=found_skills, 
                         jobs=recommended_jobs,
                         score=resume_score)

# --- ADMIN PAGE (Data dekhne k liye) ---
@app.route('/admin')
def admin():
    # Saara data MySQL database se utha kar laye ga
    try:
        all_data = UserData.query.order_by(UserData.upload_date.desc()).all()
    except:
        all_data = []
        
    return render_template('admin.html', data=all_data)

if __name__ == '__main__':
    app.run(debug=True)