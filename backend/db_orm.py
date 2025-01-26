from app import app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)
with app.app_context():
    db.create_all()