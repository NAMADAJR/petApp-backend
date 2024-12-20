from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pets = db.relationship('Pet', back_populates='owner', lazy='dynamic')     
    

class Pet(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='pets')
    health_records = db.relationship('HealthRecord', back_populates='pet', lazy='dynamic')
    appointments = db.relationship('Appointment', back_populates='pet', lazy='dynamic')
    vaccinations = db.relationship('Vaccination', back_populates='pet', lazy='dynamic')
    weight_records = db.relationship('WeightRecord', back_populates='pet', lazy='dynamic')
    activity_records = db.relationship('ActivityRecord', back_populates='pet', lazy='dynamic')
    food_allergies = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HealthRecord(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    pet_id = db.Column(db.String(36), db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', back_populates='health_records')
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    veterinary = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    pet_id = db.Column(db.String(36), db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', back_populates='appointments')
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(10))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vaccination(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    pet_id = db.Column(db.String(36), db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', back_populates='vaccinations')
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    next_due = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeightRecord(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    pet_id = db.Column(db.String(36), db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', back_populates='weight_records')
    weight = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(5), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActivityRecord(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    pet_id = db.Column(db.String(36), db.ForeignKey('pet.id'), nullable=False)
    pet = db.relationship('Pet', back_populates='activity_records')
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Community(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # Unique ID
    title = db.Column(db.String(200), nullable=False)  # Title of the post
    description = db.Column(db.Text, nullable=False)  # Description of the post
    comment = db.Column(db.Text)  # Comment section
    picture = db.Column(db.String(255))  # URL of the picture
    gif = db.Column(db.String(255))  # URL of the GIF
    emoji = db.Column(db.String(50))  # Emoji as a string
    likes = db.Column(db.Integer, default=0)  # Number of likes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Post creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update time
