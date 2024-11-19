from datetime import datetime
from uuid import uuid4
from faker import Faker
from models import db, User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord
from app import *


fake = Faker()

def seed_db():
    # Drop all existing records in the tables
    db.session.query(ActivityRecord).delete()
    db.session.query(WeightRecord).delete()
    db.session.query(Vaccination).delete()
    db.session.query(Appointment).delete()
    db.session.query(HealthRecord).delete()
    db.session.query(Pet).delete()
    db.session.query(User).delete()
    
    db.session.commit()  # Commit changes to the database

    # Create sample users
    users = []
    for _ in range(5):  # Creating 5 users
        user = User(
            id=str(uuid4()),
            name=fake.name(),
            email=fake.unique.email(),
            password='hashed_password_here',
            email_verified=fake.date_time_this_decade(),
            image=fake.image_url(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        users.append(user)
        db.session.add(user)

    db.session.commit()  # Commit after user creation

    # Create sample pets
    pets = []
    for user in users:
        for _ in range(2):  # Each user can have 2 pets
            pet = Pet(
                id=str(uuid4()),
                name=fake.first_name(),
                type=fake.random_element(elements=('Dog', 'Cat', 'Bird', 'Reptile')),
                breed=fake.random_element(elements=('Bulldog', 'Siamese', 'Poodle', 'Tabby', 'Beagle')),
                gender=fake.random_element(elements=('Male', 'Female')),
                date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=15),
                owner_id=user.id,
                food_allergies=fake.random_element(elements=(None, {'Wheat': True, 'Chicken': False})),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            pets.append(pet)
            db.session.add(pet)

    db.session.commit()  # Commit after pet creation

    # Create sample health records for each pet
    for pet in pets:
        health_record = HealthRecord(
            id=str(uuid4()),
            pet_id=pet.id,
            type=fake.random_element(elements=('Checkup', 'Vaccination')),
            description=fake.sentence(),
            date=fake.date_time_this_year(),
            veterinary=fake.company(),
            notes=fake.text(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(health_record)

    db.session.commit()  # Commit health records

    # Create sample appointments for each pet
    for pet in pets:
        appointment = Appointment(
            id=str(uuid4()),
            user_id=pet.owner_id,
            pet_id=pet.id,
            type=fake.random_element(elements=('Vaccination', 'Checkup')),
            date=fake.date_time_this_year(),
            location=fake.address(),
            status=fake.random_element(elements=('Completed', 'Pending', 'Cancelled')),
            priority=fake.random_element(elements=('High', 'Medium', 'Low')),
            notes=fake.text(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(appointment)

    db.session.commit()  # Commit appointments

    # Create sample vaccinations for each pet
    for pet in pets:
        vaccination = Vaccination(
            id=str(uuid4()),
            pet_id=pet.id,
            name=fake.random_element(elements=('Rabies', 'FVRCP', 'Bordetella')),
            date=fake.date_time_this_year(),
            next_due=fake.date_time_this_year(),
            status=fake.random_element(elements=('Completed', 'Upcoming')),
            notes=fake.text(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(vaccination)

    db.session.commit()  # Commit vaccinations

    # Create sample weight records for each pet
    for pet in pets:
        weight_record = WeightRecord(
            id=str(uuid4()),
            pet_id=pet.id,
            weight=fake.random_number(digits=2, fix_len=True) + 1,  # Weight between 1 and 99
            unit='kg',
            date=fake.date_time_this_year(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(weight_record)

    db.session.commit()  # Commit weight records

    # Create sample activity records for each pet
    for pet in pets:
        activity_record = ActivityRecord(
            id=str(uuid4()),
            pet_id=pet.id,
            type=fake.random_element(elements=('Walk', 'Playtime', 'Training')),
            value=fake.random_number(digits=1, fix_len=True) + 1,  # Activity hours or distance
            unit=fake.random_element(elements=('km', 'hours')),
            date=fake.date_time_this_year(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(activity_record)

    db.session.commit()  # Commit activity records

if __name__ == '__main__':
    with app.app_context():
        seed_db()