import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_very_secret_key_default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/applyst.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Extensions ---
from models import db # Import db from models.py
db.init_app(app) # Initialize db with the Flask app

bcrypt = Bcrypt(app)

# --- Register Blueprints (Routes) ---
# Import blueprints from the routes directory
from routes.auth_routes import auth_bp
from routes.application_routes import application_bp
from routes.email_routes import email_bp # Assuming we'll add an email specific route for OAuth callback

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(application_bp, url_prefix='/api/applications')
app.register_blueprint(email_bp, url_prefix='/auth/email') # For handling email OAuth callbacks

# --- Database Initialization (for initial setup) ---
# This block is for creating tables if they don't exist.
# In a real-world app, you'd use Flask-Migrate for migrations.
@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

# --- Basic Route for testing ---
@app.route('/')
def home():
    """
    Home route to check if the server is running.
    """
    return jsonify({"message": "Welcome to AppLyst API!"})

# --- Error Handling ---
@app.errorhandler(404)
def not_found(error):
    """
    Handles 404 Not Found errors.
    """
    return jsonify({"error": "Not Found", "message": "The requested URL was not found on the server."}), 404

@app.errorhandler(500)
def internal_server_error(error):
    """
    Handles 500 Internal Server Errors.
    """
    app.logger.error(f"Server Error: {error}")
    return jsonify({"error": "Internal Server Error", "message": "Something went wrong on the server."}), 500

if __name__ == '__main__':
    # This block is for running the app directly.
    # For production, use a WSGI server like Gunicorn.
    app.run(debug=True) # debug=True enables reloader and debugger
