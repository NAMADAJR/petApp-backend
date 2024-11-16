from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin  
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Association Tables
user_pet = db.Table('user_pet',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('pet_id', db.Integer, db.ForeignKey('pet.id'), primary_key=True),
)

# User Model
class User(db.Model, SerializerMixin):
    __tablename__ = 'user'
    serialize_only = ('id', 'name', 'email', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.DateTime)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with pets
    pets = db.relationship('Pet', secondary=user_pet, back_populates='owners')

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

    @validates('email')
    def validate_email(self, key, value):
        if "@" not in value:
            raise ValueError("Invalid email format.")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'pets': [pet.to_dict() for pet in self.pets],
        }

# Pet Model
class Pet(db.Model, SerializerMixin):
    __tablename__ = 'pet'
    serialize_only = ('id', 'name', 'type', 'owners', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100))
    gender = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    
    # Relationships
    owners = db.relationship('User', secondary=user_pet, back_populates='pets')
    health_records = db.relationship('HealthRecord', back_populates='pet', lazy='dynamic')
    appointments = db.relationship('Appointment', back_populates='pet', lazy='dynamic')
    vaccinations = db.relationship('Vaccination', back_populates='pet', lazy='dynamic')
    weight_records = db.relationship('WeightRecord', back_populates='pet', lazy='dynamic')
    activity_records = db.relationship('ActivityRecord', back_populates='pet', lazy='dynamic')

    food_allergies = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'breed': self.breed,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat(),
            'food_allergies': self.food_allergies,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
# HealthRecord Model
class HealthRecord(db.Model, SerializerMixin):
    __tablename__ = 'health_record'
    serialize_only = ('id', 'pet_id', 'type', 'description', 'date', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False) 
    pet = db.relationship('Pet', back_populates='health_records')
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    veterinary = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat(),
            'veterinary': self.veterinary,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

# Appointment Model
class Appointment(db.Model, SerializerMixin):
    __tablename__ = 'appointment'
    serialize_only = ('id', 'pet_id', 'type', 'date', 'status', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)  
    pet = db.relationship('Pet', back_populates='appointments')
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(10))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'type': self.type,
            'date': self.date.isoformat(),
            'status': self.status,
            'priority': self.priority,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

# Vaccination Model
class Vaccination(db.Model, SerializerMixin):
    __tablename__ = 'vaccination'
    serialize_only = ('id', 'pet_id', 'name', 'date', 'next_due', 'status', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)  
    pet = db.relationship('Pet', back_populates='vaccinations')
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    next_due = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'name': self.name,
            'date': self.date.isoformat(),
            'next_due': self.next_due.isoformat(),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

# WeightRecord Model
class WeightRecord(db.Model, SerializerMixin):
    __tablename__ = 'weight_record'
    serialize_only = ('id', 'pet_id', 'weight', 'unit', 'date', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)  
    pet = db.relationship('Pet', back_populates='weight_records')
    weight = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(5), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'weight': self.weight,
            'unit': self.unit,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

# ActivityRecord Model
class ActivityRecord(db.Model, SerializerMixin):
    __tablename__ = 'activity_record'
    serialize_only = ('id', 'pet_id', 'activity', 'duration', 'intensity', 'date', 'created_at', 'updated_at')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)  
    pet = db.relationship('Pet', back_populates='activity_records')
    activity = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    intensity = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pet_id': self.pet_id,
            'activity': self.activity,
            'duration': self.duration,
            'intensity': self.intensity,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
