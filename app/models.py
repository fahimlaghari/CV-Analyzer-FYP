from app import db
from datetime import datetime

class UserData(db.Model):
    __tablename__ = 'user_data'  # Professional naming convention
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(500))
    score = db.Column(db.Integer)
    email = db.Column(db.String(120))  # Future proofing
    phone = db.Column(db.String(20))   # Future proofing
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Candidate {self.filename}>'