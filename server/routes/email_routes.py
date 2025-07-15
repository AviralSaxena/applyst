from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from models import db, User
import os
import json

email_bp = Blueprint('email_bp', __name__)

# Load client secrets from environment variables
CLIENT_SECRETS = {
    "web": {
        "client_id": os.getenv('GMAIL_CLIENT_ID'),
        "project_id": "applyst-tracker", # Placeholder
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv('GMAIL_CLIENT_SECRET'),
        "redirect_uris": [os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/auth/email/callback')]
    }
}

# Define the scopes needed for Gmail API access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@email_bp.route('/authorize', methods=['GET'])
# @jwt_required() # Uncomment if you want to ensure user is logged in before initiating OAuth
def authorize_gmail():
    """
    Initiates the Google OAuth 2.0 flow for Gmail API access.
    """
    # current_user_id = get_jwt_identity() # If jwt_required is enabled

    # Create a Flow instance from the client secrets
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/auth/email/callback')
    )

    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Request a refresh token
        include_granted_scopes='true'
    )
    # Store the state in session or a temporary database for verification later .....we'll just redirect. In a production app, you'd save `state`
    # linked to the user's session to prevent CSRF attacks.

    return jsonify({"authorization_url": authorization_url}), 200
    # return redirect(authorization_url) 
    # Or redirect directly if this is a browser request

@email_bp.route('/callback', methods=['GET'])
def oauth2callback():
    """
    Handles the callback from Google OAuth 2.0.
    Exchanges the authorization code for access and refresh tokens.
    """
    # Retrieve the authorization code from the request query parameters
    code = request.args.get('code')
    state = request.args.get('state') # Verify this state against the one generated in /authorize

    if not code:
        return jsonify({"message": "Authorization code not found"}), 400

    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:5000/auth/email/callback')
    )

    try:
        # Exchange the authorization code for credentials (access token, refresh token)
        flow.fetch_token(code=code)
        credentials = flow.credentials

      # In prod, link creds to user (e.g. get_jwt_identity). Just printing for now—don't do this in prod.

        return jsonify({
            "message": "Gmail authorization successful!",
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_expiry": credentials.expiry.isoformat() if credentials.expiry else None
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error during Gmail OAuth callback: {e}")
        return jsonify({"message": "Gmail authorization failed", "error": str(e)}), 500

    # Example of redirecting to a frontend success page:
    # return redirect(url_for('frontend.gmail_auth_success'))
    # Assuming a frontend route
