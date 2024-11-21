# app_test.py
# app_test.py
import json
import pytest
from app import app, db, User, Pet  # Import your Flask app and models

@pytest.fixture
def client():
    # Set up the app for testing (use an in-memory database)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'qwerty123456716253e'
    
    # Set up the database
    db.create_all()
    
    with app.test_client() as client:
        yield client
    
    # Teardown
    db.drop_all()


# 1. Test User Registration
def test_register(client):
    # User registration endpoint test
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert b'User registered successfully' in response.data


# 2. Test User Login (Login returns JWT token)
def test_login(client):
    # First, register a user
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    client.post('/register', json=data)
    
    # Then log the user in
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)


# 3. Test Add Pet (requires JWT token)
def test_add_pet(client):
    # Register and login user to get JWT token
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    client.post('/register', json=data)
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    login_response = client.post('/login', json=login_data)
    access_token = json.loads(login_response.data)['access_token']
    
    # Add Pet
    pet_data = {
        'name': 'Buddy',
        'type': 'Dog',
        'breed': 'Labrador',
        'gender': 'Male',
        'date_of_birth': '2015-06-15'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = client.post('/pets', json=pet_data, headers=headers)
    assert response.status_code == 201
    assert b'Pet added successfully' in response.data


# 4. Test Get Pets (requires JWT token)
def test_get_pets(client):
    # Register and login user to get JWT token
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    client.post('/register', json=data)
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    login_response = client.post('/login', json=login_data)
    access_token = json.loads(login_response.data)['access_token']
    
    # Add a pet
    pet_data = {
        'name': 'Buddy',
        'type': 'Dog',
        'breed': 'Labrador',
        'gender': 'Male',
        'date_of_birth': '2015-06-15'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    client.post('/pets', json=pet_data, headers=headers)
    
    # Get pets
    response = client.get('/pets', headers=headers)
    assert response.status_code == 200
    assert len(json.loads(response.data)) > 0  # Should have at least 1 pet


# 5. Test Update Pet (requires JWT token)
def test_update_pet(client):
    # Register and login user to get JWT token
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    client.post('/register', json=data)
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    login_response = client.post('/login', json=login_data)
    access_token = json.loads(login_response.data)['access_token']
    
    # Add a pet
    pet_data = {
        'name': 'Buddy',
        'type': 'Dog',
        'breed': 'Labrador',
        'gender': 'Male',
        'date_of_birth': '2015-06-15'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    add_pet_response = client.post('/pets', json=pet_data, headers=headers)
    pet_id = json.loads(add_pet_response.data)['id']
    
    # Update the pet's details
    updated_pet_data = {
        'name': 'Buddy Updated',
        'type': 'Dog',
        'breed': 'Labrador',
        'gender': 'Male',
        'date_of_birth': '2015-06-15'
    }
    
    response = client.put(f'/pets/{pet_id}', json=updated_pet_data, headers=headers)
    assert response.status_code == 200
    assert b'Pet updated successfully' in response.data


# 6. Test Delete Pet (requires JWT token)
def test_delete_pet(client):
    # Register and login user to get JWT token
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    client.post('/register', json=data)
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    login_response = client.post('/login', json=login_data)
    access_token = json.loads(login_response.data)['access_token']
    
    # Add a pet
    pet_data = {
        'name': 'Buddy',
        'type': 'Dog',
        'breed': 'Labrador',
        'gender': 'Male',
        'date_of_birth': '2015-06-15'
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    add_pet_response = client.post('/pets', json=pet_data, headers=headers)
    pet_id = json.loads(add_pet_response.data)['id']
    
    # Delete the pet
    response = client.delete(f'/pets/{pet_id}', headers=headers)
    assert response.status_code == 200
    assert b'Pet deleted successfully' in response.data

