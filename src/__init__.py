from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
    with app.app_context():
        from .models import models  # This imports the models
        db.create_all()
