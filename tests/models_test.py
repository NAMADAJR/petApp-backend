# models_test.py# models_test.py
import pytest
from datetime import datetime
from uuid import uuid4
from app import db, app, User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord

@pytest.fixture
def client():
    """Fixture for the Flask test client."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use an in-memory database for tests
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db.create_all()  # Set up the database before each test
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()  # Clean up the database after each test


# Utility function to create a user
def create_user(client, email="test@example.com", password="password123", name="Test User"):
    user = User(id=str(uuid4()), name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


# Test User model creation
def test_create_user(client):
    user = create_user(client)
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.id is not None
    assert user.created_at is not None


# Test Pet model creation
def test_create_pet(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    # Fetch the pet from the database
    fetched_pet = Pet.query.get(pet.id)
    assert fetched_pet.name == "Fluffy"
    assert fetched_pet.type == "Dog"
    assert fetched_pet.breed == "Golden Retriever"
    assert fetched_pet.owner_id == user.id
    assert fetched_pet.created_at is not None


# Test HealthRecord model creation
def test_create_health_record(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    health_record = HealthRecord(
        id=str(uuid4()),
        pet_id=pet.id,
        type="Vaccination",
        description="Rabies Vaccine",
        date=datetime(2024, 1, 1),
        veterinary="Dr. Smith",
        notes="First dose"
    )
    db.session.add(health_record)
    db.session.commit()

    # Fetch the health record
    fetched_health_record = HealthRecord.query.get(health_record.id)
    assert fetched_health_record.type == "Vaccination"
    assert fetched_health_record.description == "Rabies Vaccine"
    assert fetched_health_record.pet_id == pet.id
    assert fetched_health_record.date == datetime(2024, 1, 1)


# Test Appointment model creation
def test_create_appointment(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    appointment = Appointment(
        id=str(uuid4()),
        user_id=user.id,
        pet_id=pet.id,
        type="Vet Checkup",
        date=datetime(2024, 1, 15),
        location="Vet Clinic",
        status="Scheduled",
        priority="High",
        notes="Annual checkup"
    )
    db.session.add(appointment)
    db.session.commit()

    # Fetch the appointment
    fetched_appointment = Appointment.query.get(appointment.id)
    assert fetched_appointment.type == "Vet Checkup"
    assert fetched_appointment.date == datetime(2024, 1, 15)
    assert fetched_appointment.pet_id == pet.id


# Test Vaccination model creation
def test_create_vaccination(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    vaccination = Vaccination(
        id=str(uuid4()),
        pet_id=pet.id,
        name="Rabies Vaccine",
        date=datetime(2024, 1, 1),
        next_due=datetime(2025, 1, 1),
        status="Scheduled",
        notes="First vaccination"
    )
    db.session.add(vaccination)
    db.session.commit()

    # Fetch the vaccination
    fetched_vaccination = Vaccination.query.get(vaccination.id)
    assert fetched_vaccination.name == "Rabies Vaccine"
    assert fetched_vaccination.date == datetime(2024, 1, 1)
    assert fetched_vaccination.pet_id == pet.id


# Test WeightRecord model creation
def test_create_weight_record(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    weight_record = WeightRecord(
        id=str(uuid4()),
        pet_id=pet.id,
        weight=25.5,
        unit="kg",
        date=datetime(2024, 1, 1)
    )
    db.session.add(weight_record)
    db.session.commit()

    # Fetch the weight record
    fetched_weight_record = WeightRecord.query.get(weight_record.id)
    assert fetched_weight_record.weight == 25.5
    assert fetched_weight_record.unit == "kg"
    assert fetched_weight_record.pet_id == pet.id


# Test ActivityRecord model creation
def test_create_activity_record(client):
    user = create_user(client)
    pet = Pet(
        id=str(uuid4()),
        name="Fluffy",
        type="Dog",
        breed="Golden Retriever",
        gender="Male",
        date_of_birth=datetime(2020, 1, 1),
        owner_id=user.id
    )
    db.session.add(pet)
    db.session.commit()

    activity_record = ActivityRecord(
        id=str(uuid4()),
        pet_id=pet.id,
        type="Walking",
        value=5.0,
        unit="km",
        date=datetime(2024, 1, 1)
    )
    db.session.add(activity_record)
    db.session.commit()

    # Fetch the activity record
    fetched_activity_record = ActivityRecord.query.get(activity_record.id)
    assert fetched_activity_record.value == 5.0
    assert fetched_activity_record.unit == "km"
    assert fetched_activity_record.pet_id == pet.id

