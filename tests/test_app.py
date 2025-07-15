import pytest
from app import app, db, bcrypt # Import app, db, bcrypt from your main Flask app
from models import User, JobApplication
from flask_jwt_extended import create_access_token, JWTManager
import os

# Initialize JWTManager for testing purposes
# In a real app, this would be initialized in app.py
app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY', 'default_test_secret_key')
jwt = JWTManager(app)

@pytest.fixture(scope='module')
def test_client():
    """
    Configures the Flask app for testing and provides a test client.
    Uses an in-memory SQLite database for tests.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for tests
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key' # A separate secret key for tests

    with app.app_context():
        db.create_all() # Create tables for the in-memory database
        yield app.test_client() # Provide the test client
        db.session.remove()
        db.drop_all() # Drop tables after tests are done

@pytest.fixture(scope='function')
def authenticated_client(test_client):
    """
    Provides a test client authenticated as a dummy user.
    """
    with app.app_context():
        # Create a dummy user for testing
        hashed_password = bcrypt.generate_password_hash("testpassword").decode('utf-8')
        test_user = User(username="testuser", email="test@example.com", password_hash=hashed_password)
        db.session.add(test_user)
        db.session.commit()

        # Generate an access token for the dummy user
        access_token = create_access_token(identity=test_user.id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        yield test_client, headers # Yield the client and headers
        
        # Clean up the user after the test
        db.session.delete(test_user)
        db.session.commit()

class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_register_user(self, test_client):
        """Test user registration."""
        response = test_client.post('/auth/register', json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepassword"
        })
        assert response.status_code == 201
        assert "User registered successfully" in response.json['message']
        assert User.query.filter_by(username="newuser").first() is not None

    def test_register_existing_user(self, test_client):
        """Test registration with existing username/email."""
        test_client.post('/auth/register', json={
            "username": "existing",
            "email": "existing@example.com",
            "password": "password"
        })
        response = test_client.post('/auth/register', json={
            "username": "existing",
            "email": "another@example.com",
            "password": "password"
        })
        assert response.status_code == 409
        assert "User with that username or email already exists" in response.json['message']

    def test_login_user(self, test_client):
        """Test successful user login."""
        test_client.post('/auth/register', json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpassword"
        })
        response = test_client.post('/auth/login', json={
            "username": "loginuser",
            "password": "loginpassword"
        })
        assert response.status_code == 200
        assert "access_token" in response.json

    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid password."""
        test_client.post('/auth/register', json={
            "username": "baduser",
            "email": "bad@example.com",
            "password": "goodpassword"
        })
        response = test_client.post('/auth/login', json={
            "username": "baduser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json['message']

class TestApplicationRoutes:
    """Tests for job application routes."""

    def test_add_application(self, authenticated_client):
        """Test adding a new job application."""
        client, headers = authenticated_client
        response = client.post('/api/applications/', headers=headers, json={
            "company_name": "Test Company",
            "job_title": "Test Job"
        })
        assert response.status_code == 201
        assert "Application added successfully" in response.json['message']
        assert JobApplication.query.filter_by(company_name="Test Company").first() is not None

    def test_get_all_applications(self, authenticated_client):
        """Test retrieving all applications for a user."""
        client, headers = authenticated_client
        client.post('/api/applications/', headers=headers, json={
            "company_name": "Company A", "job_title": "Job A"
        })
        client.post('/api/applications/', headers=headers, json={
            "company_name": "Company B", "job_title": "Job B"
        })
        response = client.get('/api/applications/', headers=headers)
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['company_name'] == "Company A"

    def test_get_single_application(self, authenticated_client):
        """Test retrieving a single application by ID."""
        client, headers = authenticated_client
        add_response = client.post('/api/applications/', headers=headers, json={
            "company_name": "Single Company", "job_title": "Single Job"
        })
        app_id = add_response.json['application']['id']

        response = client.get(f'/api/applications/{app_id}', headers=headers)
        assert response.status_code == 200
        assert response.json['company_name'] == "Single Company"

    def test_update_application(self, authenticated_client):
        """Test updating an existing application."""
        client, headers = authenticated_client
        add_response = client.post('/api/applications/', headers=headers, json={
            "company_name": "Update Company", "job_title": "Update Job", "status": "Applied"
        })
        app_id = add_response.json['application']['id']

        response = client.put(f'/api/applications/{app_id}', headers=headers, json={
            "status": "Interview",
            "notes": "First interview scheduled."
        })
        assert response.status_code == 200
        assert response.json['application']['status'] == "Interview"
        assert response.json['application']['notes'] == "First interview scheduled."
        
        updated_app = JobApplication.query.get(app_id)
        assert updated_app.status == "Interview"

    def test_delete_application(self, authenticated_client):
        """Test deleting an application."""
        client, headers = authenticated_client
        add_response = client.post('/api/applications/', headers=headers, json={
            "company_name": "Delete Company", "job_title": "Delete Job"
        })
        app_id = add_response.json['application']['id']

        response = client.delete(f'/api/applications/{app_id}', headers=headers)
        assert response.status_code == 200
        assert "Application deleted successfully" in response.json['message']
        assert JobApplication.query.get(app_id) is None

    def test_unauthorized_access(self, test_client):
        """Test accessing protected routes without authentication."""
        response = test_client.get('/api/applications/')
        assert response.status_code == 401 # Unauthorized

        response = test_client.post('/api/applications/', json={
            "company_name": "Unauthorized", "job_title": "Unauthorized"
        })
        assert response.status_code == 401
