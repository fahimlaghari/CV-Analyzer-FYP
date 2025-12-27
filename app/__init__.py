from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# Initialize Extensions (Global Variables)
db = SQLAlchemy()

def create_app():
    # Flask App 
    app = Flask(__name__)
    
    
    app.config.from_object(Config)
    
  
    db.init_app(app)
    
    
    with app.app_context():
        
        from app import models
        db.create_all()
        
        # Folder check (Uploads folder)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

    
    from app import routes
    app.register_blueprint(routes.main)

    return app