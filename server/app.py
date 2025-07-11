from flask import Flask, request, jsonify  # Flask core imports
from flask_cors import CORS  # Allows frontend (Streamlit) to access this backend
from models import db, Application  # Import database and Application model
import os

# Create a Flask app instance
app = Flask(__name__)

# Enable CORS so client and server can communicate (especially across ports)
CORS(app)

# Set up database path (SQLite stored in same directory)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

# Turn off unnecessary tracking warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with Flask app
db.init_app(app)

# Create database tables if they don’t exist
with app.app_context():
    db.create_all()

# GET endpoint: Fetch all applications
@app.route("/api/applications", methods=["GET"])
def get_applications():
    apps = Application.query.all()  # Get all records from the table
    return jsonify([
        {
            "id": app.id,
            "company": app.company,
            "position": app.position,
            "status": app.status,
            "email": app.email,
            "received_date": app.received_date.strftime("%Y-%m-%d")  # Convert datetime to string
        }
        for app in apps
    ])

# POST endpoint: Add new application app route 
@app.route("/api/applications", methods=["POST"])
def add_application():
    data = request.get_json()  # Parse JSON data from request
    new_app = Application(
        company=data["company"],
        position=data["position"],
        status=data["status"],
        email=data.get("email")  # Optional: may be None
    )
    db.session.add(new_app)     # Add to session (staging area)
    db.session.commit()         # Save to DB
    return jsonify({"message": "Application saved successfully."}), 201  # HTTP 201 = Created

# Run the Flask server

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Default port is 5000 
