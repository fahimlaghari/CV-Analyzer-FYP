from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    skills = db.Column(db.Text)
    score = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)