from flask import Flask
import os
from app.models import db  

def create_app():
    app = Flask(__name__)

    # --- Config ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, '..', 'app.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'fahim-fyp-secret-key-2025'

    # --- Init DB ---
    db.init_app(app)

    # --- Routes ---
    from app.routes import main
    app.register_blueprint(main)

    # --- Tables Creation ---
    with app.app_context():
        db.create_all()

    return app