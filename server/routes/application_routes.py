from flask import Blueprint, request, jsonify
from models import db, JobApplication, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

application_bp = Blueprint('application_bp', __name__)

@application_bp.route('/', methods=['POST'])
@jwt_required()
def add_application():
    """
    Adds a new job application for the authenticated user.
    Expects JSON: { "company_name": "...", "job_title": "...", "job_posting_url": "...", "notes": "..." }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    company_name = data.get('company_name')
    job_title = data.get('job_title')
    job_posting_url = data.get('job_posting_url')
    notes = data.get('notes')

    if not company_name or not job_title:
        return jsonify({"message": "Company name and job title are required"}), 400

    new_application = JobApplication(
        user_id=current_user_id,
        company_name=company_name,
        job_title=job_title,
        job_posting_url=job_posting_url,
        notes=notes,
        status='Applied', # Default status
        application_date=datetime.utcnow(),
        last_status_update=datetime.utcnow()
    )
    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": "Application added successfully", "application": new_application.to_dict()}), 201

@application_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_applications():
    """
    Retrieves all job applications for the authenticated user.
    """
    current_user_id = get_jwt_identity()
    applications = JobApplication.query.filter_by(user_id=current_user_id).all()
    return jsonify([app.to_dict() for app in applications]), 200

@application_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """
    Retrieves a specific job application by ID for the authenticated user.
    """
    current_user_id = get_jwt_identity()
    application = JobApplication.query.filter_by(id=app_id, user_id=current_user_id).first()

    if not application:
        return jsonify({"message": "Application not found or unauthorized"}), 404

    return jsonify(application.to_dict()), 200

@application_bp.route('/<int:app_id>', methods=['PUT'])
@jwt_required()
def update_application(app_id):
    """
    Updates an existing job application for the authenticated user.
    Expects JSON with fields to update (e.g., "status": "Interview", "notes": "..." )
    """
    current_user_id = get_jwt_identity()
    application = JobApplication.query.filter_by(id=app_id, user_id=current_user_id).first()

    if not application:
        return jsonify({"message": "Application not found or unauthorized"}), 404

    data = request.get_json()
    updated = False

    if 'company_name' in data:
        application.company_name = data['company_name']
        updated = True
    if 'job_title' in data:
        application.job_title = data['job_title']
        updated = True
    if 'status' in data:
        application.status = data['status']
        application.last_status_update = datetime.utcnow() # Update timestamp on status change
        updated = True
    if 'job_posting_url' in data:
        application.job_posting_url = data['job_posting_url']
        updated = True
    if 'notes' in data:
        application.notes = data['notes']
        updated = True
    # Skip: email_thread_id is auto-set by scanner, not manually updated

    if updated:
        db.session.commit()
        return jsonify({"message": "Application updated successfully", "application": application.to_dict()}), 200
    else:
        return jsonify({"message": "No valid fields provided for update"}), 400

@application_bp.route('/<int:app_id>', methods=['DELETE'])
@jwt_required()
def delete_application(app_id):
    """
    Deletes a job application for the authenticated user.
    """
    current_user_id = get_jwt_identity()
    application = JobApplication.query.filter_by(id=app_id, user_id=current_user_id).first()

    if not application:
        return jsonify({"message": "Application not found or unauthorized"}), 404

    db.session.delete(application)
    db.session.commit()

    return jsonify({"message": "Application deleted successfully"}), 200
