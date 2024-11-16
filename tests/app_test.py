import pytest
from flask_jwt_extended import create_access_token
from server.app import create_app, db
from server.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    # Create the app using the factory function
    app = create_app()

    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory DB for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret'

    # Set up the database
    with app.app_context():
        db.create_all()  # Create in-memory database tables

    yield app  # Yield the app instance to the test client

    # Cleanup after tests
    with app.app_context():
        db.drop_all()  # Drop the in-memory database tables

@pytest.fixture
def client(app):
    # Use the app fixture to create the test client
    return app.test_client()

@pytest.fixture
def test_user(app):
    # Create a test user
    user = User(
        name="testuser",
        email="test@example.com",
        password=generate_password_hash("hashedpassword")  # Using hashed password
    )
    # Ensure the user is added to the session
    with app.app_context():
        db.session.add(user)
        db.session.commit()  # Commit the session to bind the user to the session
    return user

@pytest.fixture
def access_token(test_user):
    # Generate a JWT for the test user
    return create_access_token(identity=test_user.id)

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Pet App Database"

def test_register(client):
    response = client.post('/register', json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

def test_add_pet(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post('/pets', json={
        "name": "Buddy",
        "type": "Dog",
        "breed": "Golden Retriever",
        "gender": "Male",
        "date_of_birth": "2020-01-01"
    }, headers=headers)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Pet added successfully"
