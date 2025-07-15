from flask import Blueprint, request, jsonify
from models import db, User
from app import bcrypt # Import bcrypt from app.py
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
import os

# Initialize JWTManager with the app (assuming app is created) this is usually is needed to be done after app is created, typically in app.py

jwt = JWTManager() # This will be initialized in app.py

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """
    Registers a new user.
    Expects JSON: { "username": "...", "email": "...", "password": "..." }
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "Missing username, email, or password"}), 400

    # Check if user already exists
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "User with that username or email already exists"}), 409

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login_user():
    """
    Logs in an existing user and returns an access token.
    Expects JSON: { "username": "...", "password": "..." }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Create an access token for the user
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# This is  just a placeholder for JWT initialization Usually in a real app, you'd initialize JWTManager in app.py after creating the app. 
# An example of how it would be initialized in app.py:
# from flask_jwt_extended import JWTManager
# jwt = JWTManager(app)
