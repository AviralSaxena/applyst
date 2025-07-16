from flask import Blueprint, request, jsonify
from models import db, JobApplication, User # Assuming User is needed for get_jwt_identity which references user_id
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

# Create a Blueprint for application-related routes.
# This helps organize routes and allows them to be registered with the main Flask app.
application_bp = Blueprint('application_bp', __name__)

@application_bp.route('/', methods=['POST'])
@jwt_required() # Decorator to ensure only authenticated users can access this route
def add_application():
    """
    Adds a new job application for the authenticated user.
    Expects JSON: { "company_name": "...", "job_title": "...", "job_posting_url": "...", "notes": "..." }
    """
    current_user_id = get_jwt_identity() # Get the identity of the current user from the JWT token
    data = request.get_json() # Get JSON data from the request body

    # Extract data fields, providing None as default if not present
    company_name = data.get('company_name')
    job_title = data.get('job_title')
    job_posting_url = data.get('job_posting_url')
    notes = data.get('notes')

    # Basic input validation
    if not company_name or not job_title:
        return jsonify({"message": "Company name and job title are required"}), 400

    # Create a new JobApplication instance
    new_application = JobApplication(
        user_id=current_user_id,
        company_name=company_name,
        job_title=job_title,
        job_posting_url=job_posting_url,
        notes=notes,
        status='Applied', # Default status for a new application
        application_date=datetime.utcnow(), # Set application date to current UTC time
        last_status_update=datetime.utcnow() # Set last status update to current UTC time
    )
    db.session.add(new_application) # Add the new application to the database session
    db.session.commit() # Commit the transaction to save to the database

    # Return success response with the new application's data
    return jsonify({"message": "Application added successfully", "application": new_application.to_dict()}), 201

@application_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_applications():
    """
    Retrieves all job applications for the authenticated user.
    """
    current_user_id = get_jwt_identity()
    # Query all applications belonging to the current user
    applications = JobApplication.query.filter_by(user_id=current_user_id).all()
    # Return a list of application dictionaries
    return jsonify([app.to_dict() for app in applications]), 200

@application_bp.route('/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """
    Retrieves a specific job application by ID for the authenticated user.
    """
    current_user_id = get_jwt_identity()
    # Query a specific application by ID and user ID to ensure ownership
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
    # Find the application to update, ensuring it belongs to the current user
    application = JobApplication.query.filter_by(id=app_id, user_id=current_user_id).first()

    if not application:
        return jsonify({"message": "Application not found or unauthorized"}), 404

    data = request.get_json()
    updated = False # Flag to track if any field was actually updated

    # Update fields if they are present in the request data
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
    # email_thread_id is typically managed by an automated scanner/service, not direct user update

    if updated:
        db.session.commit() # Commit changes to the database
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
    # Find the application to delete, ensuring it belongs to the current user
    application = JobApplication.query.filter_by(id=app_id, user_id=current_user_id).first()

    if not application:
        return jsonify({"message": "Application not found or unauthorized"}), 404

    db.session.delete(application) # Mark the application for deletion
    db.session.commit() # Commit the deletion to the database

    return jsonify({"message": "Application deleted successfully"}), 200
