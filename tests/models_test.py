import pytest
from server.app import db
from datetime import datetime
from server.models import User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord  # adjust imports
from werkzeug.security import generate_password_hash

def test_user_creation(init_db):
    # Test user creation and validation
    hashed_password = generate_password_hash("password")  # Hash the password
    user = User(id="2", name="Jane Smith", email="jane.smith@example.com", password=hashed_password)
    db.session.add(user)
    db.session.commit()

    assert user.id == "2"
    assert user.name == "Jane Smith"
    assert user.email == "jane.smith@example.com"
    assert user.check_password("password")  # Test password check

def test_user_invalid_email(init_db):
    # Test invalid email format
    with pytest.raises(ValueError, match="Invalid email format."):
        user = User(id="3", name="Invalid Email", email="invalid-email", password="password")
        db.session.add(user)
        db.session.commit()

def test_pet_creation(init_db):
    # Test pet creation without owner_id
    pet = Pet(id="2", name="Buddy", type="Dog", gender="Male", date_of_birth="2019-05-01")
    db.session.add(pet)
    db.session.commit()

    assert pet.name == "Buddy"
    assert pet.type == "Dog"
    assert pet.gender == "Male"
    assert pet.date_of_birth == datetime(2019, 5, 1)

def test_pet_owners(init_db):
    # Test relationship between Pet and User
    user = User.query.get("2")  # Assuming user with id "2" exists
    pet = Pet.query.get("2")    # Assuming pet with id "2" exists
    
    # Establish relationship by appending pet to user's pets
    user.pets.append(pet)
    db.session.commit()

    assert pet in user.pets  # Check if the pet is now associated with the user
    assert user in pet.owners  # Check reverse relationship

def test_health_record_creation(init_db):
    # Test creating a health record for a pet
    pet = Pet.query.get("2")
    health_record = HealthRecord(id="1", pet_id=pet.id, type="Vaccination", description="Rabies shot", date=datetime.utcnow())
    db.session.add(health_record)
    db.session.commit()

    assert health_record.pet_id == pet.id
    assert health_record.type == "Vaccination"
    assert health_record.description == "Rabies shot"

def test_appointment_creation(init_db):
    # Test creating an appointment for a pet
    pet = Pet.query.get("2")
    appointment = Appointment(id="1", pet_id=pet.id, type="Checkup", date=datetime.utcnow(), status="Scheduled", location="Clinic")
    db.session.add(appointment)
    db.session.commit()

    assert appointment.pet_id == pet.id
    assert appointment.status == "Scheduled"
    assert appointment.location == "Clinic"

def test_vaccination_creation(init_db):
    # Test creating a vaccination for a pet
    pet = Pet.query.get("2")
    vaccination = Vaccination(id="1", pet_id=pet.id, name="Rabies", date=datetime.utcnow(), next_due=datetime.utcnow(), status="Done")
    db.session.add(vaccination)
    db.session.commit()

    assert vaccination.pet_id == pet.id
    assert vaccination.name == "Rabies"
    assert vaccination.status == "Done"

def test_weight_record_creation(init_db):
    # Test creating a weight record for a pet
    pet = Pet.query.get("2")
    weight_record = WeightRecord(id="1", pet_id=pet.id, weight=5.5, unit="kg", date=datetime.utcnow())
    db.session.add(weight_record)
    db.session.commit()

    assert weight_record.pet_id == pet.id
    assert weight_record.weight == 5.5
    assert weight_record.unit == "kg"

def test_activity_record_creation(init_db):
    # Test creating an activity record for a pet
    pet = Pet.query.get("2")
    activity_record = ActivityRecord(id="1", pet_id=pet.id, type="Walk", value=3.2, unit="km", date=datetime.utcnow())
    db.session.add(activity_record)
    db.session.commit()

    assert activity_record.pet_id == pet.id
    assert activity_record.type == "Walk"
    assert activity_record.value == 3.2
    assert activity_record.unit == "km"
