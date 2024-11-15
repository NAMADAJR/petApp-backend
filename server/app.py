# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import uuid

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petpal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key

db.init_app(app)
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400
   
    hashed_password = generate_password_hash(data['password'])
    new_user = User(id=str(uuid.uuid4()), name=data['name'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    current_user_id = get_jwt_identity()
    data = request.json
    new_pet = Pet(
        id=str(uuid.uuid4()),
        name=data['name'],
        type=data['type'],
        breed=data.get('breed'),
        gender=data['gender'],
        date_of_birth=data['date_of_birth'],
        owner_id=current_user_id,
        food_allergies=data.get('food_allergies', [])
    )
    db.session.add(new_pet)
    db.session.commit()
    return jsonify({"message": "Pet added successfully", "pet_id": new_pet.id}), 201

@app.route('/pets', methods=['GET'])
@jwt_required()
def get_pets():
    current_user_id = get_jwt_identity()
    pets = Pet.query.filter_by(owner_id=current_user_id).all()
    return jsonify([{
        "id": pet.id,
        "name": pet.name,
        "type": pet.type,
        "breed": pet.breed,
        "gender": pet.gender,
        "date_of_birth": pet.date_of_birth.isoformat()
    } for pet in pets]), 200

@app.route('/appointments', methods=['POST'])
@jwt_required()
def add_appointment():
    data = request.json
    new_appointment = Appointment(
        id=str(uuid.uuid4()),
        pet_id=data['pet_id'],
        type=data['type'],
        date=data['date'],
        location=data['location'],
        status=data['status'],
        priority=data.get('priority'),
        notes=data.get('notes')
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"message": "Appointment added successfully", "appointment_id": new_appointment.id}), 201

@app.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    current_user_id = get_jwt_identity()
    pets = Pet.query.filter_by(owner_id=current_user_id).all()
    pet_ids = [pet.id for pet in pets]
    appointments = Appointment.query.filter(Appointment.pet_id.in_(pet_ids)).all()
    return jsonify([{
        "id": appointment.id,
        "pet_id": appointment.pet_id,
        "type": appointment.type,
        "date": appointment.date.isoformat(),
        "location": appointment.location,
        "status": appointment.status,
        "priority": appointment.priority,
        "notes": appointment.notes
    } for appointment in appointments]), 200

@app.route('/health-records', methods=['POST'])
@jwt_required()
def add_health_record():
    data = request.json
    new_record = HealthRecord(
        id=str(uuid.uuid4()),
        pet_id=data['pet_id'],
        type=data['type'],
        description=data['description'],
        date=data['date'],
        veterinary=data.get('veterinary'),
        notes=data.get('notes')
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"message": "Health record added successfully", "record_id": new_record.id}), 201

@app.route('/health-records/<pet_id>', methods=['GET'])
@jwt_required()
def get_health_records(pet_id):
    records = HealthRecord.query.filter_by(pet_id=pet_id).all()
    return jsonify([{
        "id": record.id,
        "type": record.type,
        "description": record.description,
        "date": record.date.isoformat(),
        "veterinary": record.veterinary,
        "notes": record.notes
    } for record in records]), 200

if __name__ == '__main__':
    app.run(debug=True)
