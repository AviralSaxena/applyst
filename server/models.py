from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy ORM (Object Relational Mapper)
from datetime import datetime  # Used to timestamp each entry

# Initialize the database object (linked to your Flask app in app.py)
db = SQLAlchemy()

# Define a model representing a job application record
class Application(db.Model):
    __tablename__ = 'applications'  # Optional: explicit table name

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    company = db.Column(db.String(120), nullable=False)  # Company name (required)
    position = db.Column(db.String(120), nullable=False)  # Job title (required)
    status = db.Column(db.String(50), nullable=False)  # Status: Applied, Interview, etc.
    email = db.Column(db.String(200))  # Optional: sender’s email address
    received_date = db.Column(db.DateTime, default=datetime.utcnow)  # Auto timestamp on entry

    def __repr__(self):
        return f"<Application {self.company} | {self.position} | {self.status}>"
