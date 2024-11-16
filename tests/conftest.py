import pytest
from server.app import create_app, db, User, Pet
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    # Create a new app instance with testing configurations
    app = create_app(test_config={'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'TESTING': True})
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_db(app):
    # Create all tables in the test database
    db.create_all()

    # Sample data setup
    hashed_password = generate_password_hash("password")
    user = User(id="1", name="John Doe", email="john.doe@example.com", password=hashed_password)
    pet = Pet(id="1", name="Fluffy", type="Cat", gender="Male", date_of_birth="2020-01-01", owner_id=user.id)
    
    db.session.add(user)
    db.session.add(pet)
    db.session.commit()

    yield db  # Allow tests to access the database

    db.session.remove()
    db.drop_all()  # Cleanup the database after tests
