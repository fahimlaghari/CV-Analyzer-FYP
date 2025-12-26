from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

# Initialize Extensions (Global Variables)
db = SQLAlchemy()

def create_app():
    # Flask App banaya
    app = Flask(__name__)
    
    # Config load ki
    app.config.from_object(Config)
    
    # Database connect kiya
    db.init_app(app)
    
    # Context push kiya (Technical requirement)
    with app.app_context():
        # Models import kiye taake tables ban jayen
        from app import models
        db.create_all()
        
        # Folder check (Uploads folder)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

    # Routes register kiye
    from app import routes
    app.register_blueprint(routes.main)

    return app