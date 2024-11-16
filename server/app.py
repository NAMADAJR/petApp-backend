from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
import uuid

app = Flask(__name__)
CORS(app)
#create db using postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:joshualee087@localhost/petApp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'qwerty123456716253e'

db.init_app(app)
CORS(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    user = User(id=str(uuid.uuid4()), name=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    data = request.get_json()
    pet_id = str(uuid.uuid4())
    name = data['name']
    type = data['type']
    breed = data['breed']
    gender = data['gender']
    date_of_birth = data['date_of_birth']

    pet = Pet(id=pet_id, name=name, type=type, breed=breed, gender=gender, date_of_birth=date_of_birth)
    db.session.add(pet)
    db.session.commit()
    return jsonify({'message': 'Pet added successfully'}), 201

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

@app.route('/pets/<pet_id>', methods=['GET'])
@jwt_required()
def get_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    return jsonify({
        "id": pet.id,
        "name": pet.name,
        "type": pet.type,
        "breed": pet.breed,
        "gender": pet.gender,
        "date_of_birth": pet.date_of_birth.isoformat()
        }), 200

@app.route('/pets/<pet_id>', methods=['PUT'])
@jwt_required()
def update_pet(pet_id):
    data = request.get_json()
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    pet.name = data['name']
    pet.type = data['type']
    pet.breed = data['breed']
    pet.gender = data['gender']
    pet.date_of_birth = data['date_of_birth']

    db.session.commit()
    return jsonify({'message': 'Pet updated successfully'}), 200

@app.route('/pets/<pet_id>', methods=['DELETE'])
@jwt_required()
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deleted successfully'}), 200

@app.route('/pets/<pet_id>/health_records', methods=['POST'])
@jwt_required()
def add_health_record(pet_id):
    data = request.get_json()
    health_record_id = str(uuid.uuid4())
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    type = data['type']
    description = data['description']
    date = data['date']
    veterinary = data['veterinary']
    notes = data['notes']

    health_record = HealthRecord(id=health_record_id, pet_id=pet_id, type=type, description=description, date=date, veterinary=veterinary, notes=notes)
    db.session.add(health_record)
    db.session.commit()
    return jsonify({'message': 'Health record added successfully'}), 201

@app.route('/pets/<pet_id>/health_records', methods=['GET'])
@jwt_required()
def get_health_records(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    health_records = HealthRecord.query.filter_by(pet_id=pet_id).all()
    return jsonify([{
        "id": record.id,
        "type": record.type,
        "description": record.description,
        "date": record.date.isoformat(),
        "veterinary": record.veterinary,
        "notes": record.notes
        } for record in health_records]), 200

@app.route('/pets/<pet_id>/health_records/<health_record_id>', methods=['GET'])
@jwt_required()
def get_health_record(pet_id, health_record_id):
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    health_record = HealthRecord.query.get(health_record_id)
    if health_record is None or health_record.pet_id != pet_id:
        return jsonify({'message': 'Health record not found'}), 404
    
    return jsonify({
        "id": health_record.id,
        "type": health_record.type,
        "description": health_record.description,
        "date": health_record.date.isoformat(),
        "veterinary": health_record.veterinary,
        "notes": health_record.notes
        }), 200

@app.route('/pets/<pet_id>/health_records/<health_record_id>', methods=['PUT'])
@jwt_required()
def update_health_record(pet_id, health_record_id):
    data = request.get_json()
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    health_record = HealthRecord.query.get(health_record_id)
    if health_record is None or health_record.pet_id != pet_id:
        return jsonify({'message': 'Health record not found'}), 404
    
    health_record.type = data['type']
    health_record.description = data['description']
    health_record.date = data['date']
    health_record.veterinary = data['veterinary']
    health_record.notes = data['notes']

    db.session.commit()
    return jsonify({'message': 'Health record updated successfully'}), 200

@app.route('/pets/<pet_id>/health_records/<health_record_id>', methods=['DELETE'])
@jwt_required()
def delete_health_record(pet_id, health_record_id):
    pet = Pet.query.get(pet_id)
    if pet is None or pet.owner_id != get_jwt_identity():
        return jsonify({'message': 'Pet not found'}), 404
    
    health_record = HealthRecord.query.get(health_record_id)
    if health_record is None or health_record.pet_id != pet_id:
        return jsonify({'message': 'Health record not found'}), 404
    
    db.session.delete(health_record)
    db.session.commit()
    return jsonify({'message': 'Health record deleted successfully'}), 200

@app.route('/Appointment', methods=['GET', 'POST'])
@jwt_required()
def appointment():
    if request.method == 'GET':
        current_user_id = get_jwt_identity()
        appointments = Appointment.query.filter_by(user_id=current_user_id).all()
        return jsonify([{
            "id": appointment.id,
            "pet_id": appointment.pet_id,
            "date": appointment.date.isoformat(),
            "time": appointment.time,
            "notes": appointment.notes
            } for appointment in appointments]), 200
    
    data = request.get_json()
    appointment_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    pet_id = data['pet_id']
    date = data['date']
    time = data['time']
    notes = data['notes']

    appointment = Appointment(id=appointment_id, user_id=user_id, pet_id=pet_id, date=date, time=time, notes=notes)
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment added successfully'}), 201

@app.route('/Appointment/<appointment_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def appointment_detail(appointment_id):
    if request.method == 'GET':
        appointment = Appointment.query.get(appointment_id)
        if appointment is None:
            return jsonify({'message': 'Appointment not found'}), 404
        
        return jsonify({
            "id": appointment.id,
            "pet_id": appointment.pet_id,
            "date": appointment.date.isoformat(),
            "time": appointment.time,
            "notes": appointment.notes
            }), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        appointment = Appointment.query.get(appointment_id)
        if appointment is None:
            return jsonify({'message': 'Appointment not found'}), 404
        
        User
        if appointment.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        appointment
        appointment.date = data['date']
        appointment.time = data['time']
        appointment.notes = data['notes']
        db.session.commit()
        return jsonify({'message': 'Appointment updated successfully'}), 200
    
    if request.method == 'DELETE':
        appointment = Appointment.query.get(appointment_id)
        if appointment is None:
            return jsonify({'message': 'Appointment not found'}), 404
        
        User
        if appointment.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        db
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'message': 'Appointment deleted successfully'}), 200
    
    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/Vaccination', methods=['GET', 'POST'])
@jwt_required()
def vaccination():
    if request.method == 'GET':
        current_user_id = get_jwt_identity()
        vaccinations = Vaccination.query.filter_by(user_id=current_user_id).all()
        return jsonify([{
            "id": vaccination.id,
            "pet_id": vaccination.pet_id,
            "name": vaccination.name,
            "date": vaccination.date.isoformat(),
            "next_due": vaccination.next_due
            } for vaccination in vaccinations]), 200
    
    data = request.get_json()
    vaccination_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    pet_id = data['pet_id']
    name = data['name']
    date = data['date']
    next_due = data['next_due']

    vaccination = Vaccination(id=vaccination_id, user_id=user_id, pet_id=pet_id, name=name, date=date, next_due=next_due)
    db.session.add(vaccination)
    db.session.commit()
    return jsonify({'message': 'Vaccination added successfully'}), 201

@app.route('/Vaccination/<vaccination_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def vaccination_detail(vaccination_id):
    if request.method == 'GET':
        vaccination = Vaccination.query.get(vaccination_id)
        if vaccination is None:
            return jsonify({'message': 'Vaccination not found'}), 404
        
        return
    if request.method == 'PUT':
        data = request.get_json()
        vaccination = Vaccination.query.get(vaccination_id)
        if vaccination is None:
            return jsonify({'message': 'Vaccination not found'}), 404
        
        User
        if vaccination.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        Vaccination
        vaccination.name = data['name']
        vaccination.date = data['date']
        vaccination.next_due = data['next_due']
        db.session.commit()
        return jsonify({'message': 'Vaccination updated successfully'}), 200
    
    if request.method == 'DELETE':
        vaccination = Vaccination.query.get(vaccination_id)
        if vaccination is None:
            return jsonify({'message': 'Vaccination not found'}), 404
        
        User
        if vaccination.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        db
        db.session.delete(vaccination)
        db.session.commit()
        return jsonify({'message': 'Vaccination deleted successfully'}), 200
    
    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/WeightRecord', methods=['GET', 'POST'])
@jwt_required()
def weight_record():
    if request.method == 'GET':
        current_user_id = get_jwt_identity()
        weight_records = WeightRecord.query.filter_by(user_id=current_user_id).all()
        return jsonify([{
            "id": weight_record.id,
            "pet_id": weight_record.pet_id,
            "date": weight_record.date.isoformat(),
            "weight": weight_record.weight,
            "unit": weight_record.unit
            } for weight_record in weight_records]), 200
    
    data = request.get_json()
    weight_record_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    pet_id = data['pet_id']
    weight = data['weight']
    unit = data['unit']
    date = data['date']
    weight_record = WeightRecord(id=weight_record_id, user_id=user_id, pet_id=pet_id, weight=weight, unit=unit, date=date)
    db.session.add(weight_record)
    db.session.commit()
    return jsonify({'message': 'Weight record added successfully'}), 201

@app.route('/WeightRecord/<weight_record_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def weight_record_detail(weight_record_id):
    if request.method == 'GET':
        weight_record = WeightRecord.query.get(weight_record_id)
        if weight_record is None:
            return jsonify({'message': 'Weight record not found'}), 404
        
        return
    if request.method == 'PUT':
        data = request.get_json()
        weight_record = WeightRecord.query.get(weight_record_id)
        if weight_record is None:
            return jsonify({'message': 'Weight record not found'}), 404
        
        User
        if weight_record.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        WeightRecord
        weight_record.weight = data['weight']
        weight_record.unit = data['unit']
        weight_record.date = data['date']
        db.session.commit()
        return jsonify({'message': 'Weight record updated successfully'}), 200
    
    if request.method == 'DELETE':
        weight_record = WeightRecord.query.get(weight_record_id)
        if weight_record is None:
            return jsonify({'message': 'Weight record not found'}), 404
        
        User
        if weight_record.user_id!= get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        db
        db.session.delete(weight_record)
        db.session.commit()
        return jsonify({'message': 'Weight record deleted successfully'}), 200
    
    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/ActivityRecord/create', methods=['POST'])
@jwt_required()
def create_activity_record():
    data = request.get_json()
    activity_record_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    pet_id = data['pet_id']
    activity_type = data['activity_type']
    activity_value = data['activity_value']
    activity_unit = data['activity_unit']
    activity_record = ActivityRecord(id=activity_record_id, user_id=user_id, pet_id=pet_id, type=activity_type, value=activity_value, unit=activity_unit)
    db.session.add(activity_record)



if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
