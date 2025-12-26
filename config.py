import os

class Config:
    # Security Key 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-for-fyp'
    
    # Database URI (MySQL)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/cv_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Max file size limit