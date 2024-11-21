from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Pet, HealthRecord, Appointment, Vaccination, WeightRecord, ActivityRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configurations for the database and JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petApp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = 'qwerty123456716253e'

# Initialize database, CORS, JWT, and migration
db.init_app(app)
CORS(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Route for testing the app
@app.route('/')
def index():
    return "Pet App Database"

# Route for user registration
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

# Route for user login
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

# Route for fetching the current user's profile
@app.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'image': user.image})

# Configurations for file uploads
UPLOAD_FOLDER = 'uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for updating user information including profile image
@app.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.form  # Using form data for file uploads
    file = request.files.get('image')  # Retrieve the uploaded file

    # Ensure the uploads/images directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Check if a file is provided
    if file:
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({'message': 'Invalid file type. Allowed types are: png, jpg, jpeg, gif.'}), 400

        # Secure the file name to avoid directory traversal attacks
        filename = secure_filename(file.filename)

        # Save the file to the server
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)  # Save the file to the disk
            user.image = file_path  # Save the relative file path to the database
        except Exception as e:
            return jsonify({'message': f'Error saving image: {str(e)}'}), 500

    # Optionally, update other fields like username or email
    if 'username' in data:
        user.name = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    db.session.commit()

    return jsonify({'message': 'User information updated successfully'}), 200


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
    date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')
    owner_id = get_jwt_identity()

    pet = Pet(id=pet_id, name=name, type=type, breed=breed, gender=gender, owner_id=owner_id, date_of_birth=date_of_birth)
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
    date_of_birth = data['date_of_birth']
    pet.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')

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
    date = datetime.strptime(data['date'], '%Y-%m-%d')
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
    health_record.date=datetime.strptime(data['date'], '%Y-%m-%d')
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
        return jsonify([
            {
                "id": appointment.id,
                "pet_id": appointment.pet_id,
                "type": appointment.type,
                "date": appointment.date.isoformat(),
                "location": appointment.location,
                "status": appointment.status,
                "priority": appointment.priority,
                "notes": appointment.notes
            }
            for appointment in appointments
        ]), 200
    
    if request.method == 'POST':
        data = request.get_json()

        appointment_id = str(uuid.uuid4())
        user_id = get_jwt_identity()
        pet_id = data['pet_id']
        type_ = data['type']
        date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S')  
        location = data['location']
        status = data['status']
        priority = data.get('priority') 
        notes = data.get('notes') 

        appointment = Appointment(
            id=appointment_id,
            user_id=user_id,
            pet_id=pet_id,
            type=type_,
            date=date,
            location=location,
            status=status,
            priority=priority,
            notes=notes
        )
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
            "user_id": appointment.user_id,
            "pet_id": appointment.pet_id,
            "type": appointment.type,
            "date": appointment.date.isoformat(),  
            "location": appointment.location,
            "status": appointment.status,
            "priority": appointment.priority,
            "notes": appointment.notes,
            "created_at": appointment.created_at.isoformat(),
            "updated_at": appointment.updated_at.isoformat()
            }), 200
    
    
    if request.method == 'PUT':
        data = request.get_json()
        appointment = Appointment.query.get(appointment_id)
        
        if appointment is None:
            return jsonify({'message': 'Appointment not found'}), 404
        
        if appointment.user_id != get_jwt_identity():
            return jsonify({'message': 'Unauthorized'}), 401
        
        try:
            date_str = data['date']
            appointment.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')  
        except KeyError:
            return jsonify({'message': "'date' key is required"}), 400
        except ValueError:
            return jsonify({'message': "Invalid date format. Use 'YYYY-MM-DDTHH:MM:SS'"}), 400
    
        appointment.type = data.get('type', appointment.type)  
        appointment.notes = data.get('notes', appointment.notes)  
        appointment.status = data.get('status', appointment.status)  
        appointment.location = data.get('location', appointment.location)  
        appointment.priority = data.get('priority', appointment.priority)
    

        appointment.updated_at = datetime.utcnow()
        
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
        pets = Pet.query.filter_by(owner_id=current_user_id).all()
        pet_ids = [pet.id for pet in pets]
        
        vaccinations = Vaccination.query.filter(Vaccination.pet_id.in_(pet_ids)).all()
        
        return jsonify([{
            "id": vaccination.id,
            "pet_id": vaccination.pet_id,
            "name": vaccination.name,
            "date": vaccination.date.isoformat(),
            "next_due": vaccination.next_due.isoformat(),
            "status": vaccination.status,
            "notes": vaccination.notes,
            "created_at": vaccination.created_at.isoformat(),
            "updated_at": vaccination.updated_at.isoformat()
        } for vaccination in vaccinations]), 200
    
    data = request.get_json()
    
    try:
        date_str = data['date']
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    except KeyError:
        return jsonify({'message': "'date' key is required"}), 400
    except ValueError:
        return jsonify({'message': "Invalid date format. Use 'YYYY-MM-DDTHH:MM:SS'"}), 400

    try:
        next_due_str = data['next_due']
        next_due = datetime.strptime(next_due_str, '%Y-%m-%dT%H:%M:%S')
    except KeyError:
        return jsonify({'message': "'next_due' key is required"}), 400
    except ValueError:
        return jsonify({'message': "Invalid next_due format. Use 'YYYY-MM-DDTHH:MM:SS'"}), 400
    
    vaccination_id = str(uuid.uuid4())
    pet_id = data['pet_id']
    name = data['name']
    status = data.get('status', 'Scheduled')  
    notes = data.get('notes', None) 
    
    vaccination = Vaccination(
        id=vaccination_id,
        pet_id=pet_id,
        name=name,
        date=date,
        next_due=next_due,
        status=status,
        notes=notes
    )
    
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
        
        return jsonify({
            "id": vaccination.id,
            "pet_id": vaccination.pet_id,
            "name": vaccination.name,
            "date": vaccination.date.isoformat(),
            "next_due": vaccination.next_due.isoformat(),
            "status": vaccination.status,
            "notes": vaccination.notes,
            "created_at": vaccination.created_at.isoformat(),
            "updated_at": vaccination.updated_at.isoformat()
        }), 200
    
    if request.method == 'PUT':
        data = request.get_json()
        vaccination = Vaccination.query.get(vaccination_id)
        if vaccination is None:
            return jsonify({'message': 'Vaccination not found'}), 404
        
        if vaccination.pet.owner_id != get_jwt_identity(): 
            return jsonify({'message': 'Unauthorized'}), 401
        
        try:
            if 'date' in data:
                vaccination.date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S')
            if 'next_due' in data:
                vaccination.next_due = datetime.strptime(data['next_due'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({'message': "Invalid date format. Use 'YYYY-MM-DDTHH:MM:SS'"}), 400
        
        vaccination.name = data.get('name', vaccination.name)
        vaccination.status = data.get('status', vaccination.status)
        vaccination.notes = data.get('notes', vaccination.notes)
        vaccination.updated_at = datetime.utcnow()
        
        db.session.commit()

        return jsonify({'message': 'Vaccination updated successfully'}), 200
    
    if request.method == 'DELETE':
        vaccination = Vaccination.query.get(vaccination_id)
        if vaccination is None:
            return jsonify({'message': 'Vaccination not found'}), 404
        
        if vaccination.pet.owner_id != get_jwt_identity(): 
            return jsonify({'message': 'Unauthorized'}), 401
        
        db.session.delete(vaccination)
        db.session.commit()
        
        return jsonify({'message': 'Vaccination deleted successfully'}), 200
    
    return jsonify({'message': 'Invalid request method'}), 405

@app.route('/WeightRecord/<pet_id>', methods=['GET'])
@jwt_required()
def get_weight_records(pet_id):
    weight_records = WeightRecord.query.filter_by(pet_id=pet_id).all()

    return jsonify([{
        "id": weight_record.id,
        "pet_id": weight_record.pet_id,
        "date": weight_record.date.isoformat(),
        "weight": weight_record.weight,
        "unit": weight_record.unit
    } for weight_record in weight_records]), 200


@app.route('/WeightRecord', methods=['POST'])
@jwt_required()
def create_weight_record():
    data = request.get_json()
    weight_record_id = str(uuid.uuid4())
    pet_id = data['pet_id']
    weight = data['weight']
    unit = data['unit']
    date_str = data['date']
    
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    weight_record = WeightRecord(id=weight_record_id, pet_id=pet_id, weight=weight, unit=unit, date=date)
    db.session.add(weight_record)
    db.session.commit()

    return jsonify({'message': 'Weight record added successfully'}), 201



@app.route('/WeightRecord/<weight_record_id>', methods=['PUT'])
@jwt_required()
def update_weight_record(weight_record_id):
    data = request.get_json()
    
    weight_record = WeightRecord.query.get(weight_record_id)
    if weight_record is None:
        return jsonify({'message': 'Weight record not found'}), 404

    weight = data.get('weight')
    date_str = data.get('date')

    try:
        if date_str:
            date = datetime.fromisoformat(date_str)  
            weight_record.date = date
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400
    
    if weight is not None:
        weight_record.weight = weight

    weight_record.updated_at = datetime.utcnow()  

    db.session.commit()
    return jsonify({'message': 'Weight record updated successfully'}), 200

@app.route('/WeightRecord/<weight_record_id>', methods=['DELETE'])
@jwt_required()
def delete_weight_record(weight_record_id):
    weight_record = WeightRecord.query.get(weight_record_id)

    if weight_record is None:
        return jsonify({'message': 'Weight record not found'}), 404

    db.session.delete(weight_record)
    db.session.commit()

    return jsonify({'message': 'Weight record deleted successfully'}), 200


@app.route('/ActivityRecord/<pet_id>', methods=['GET'])
@jwt_required()
def get_activity_records(pet_id):
    user_id = get_jwt_identity()

    pet = Pet.query.filter_by(id=pet_id, owner_id=user_id).first()
    
    if pet is None:
        return jsonify({'message': 'Pet not found or does not belong to the current user'}), 404

    activity_records = ActivityRecord.query.filter_by(pet_id=pet_id).all()

    return jsonify([{
        'id': activity.id,
        'pet_id': activity.pet_id,
        'type': activity.type,
        'value': activity.value,
        'unit': activity.unit,
        'date': activity.date.isoformat(),
        'created_at': activity.created_at.isoformat(),
        'updated_at': activity.updated_at.isoformat()
    } for activity in activity_records]), 200


@app.route('/ActivityRecord/create', methods=['POST'])
@jwt_required()
def create_activity_record():
    data = request.get_json()
    
    required_fields = ["pet_id", "activity_type", "activity_value", "activity_unit"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}"}), 400

    activity_record_id = str(uuid.uuid4())
    pet_id = data['pet_id']
    activity_type = data['activity_type']
    activity_value = data['activity_value']
    activity_unit = data['activity_unit']
    
    activity_record = ActivityRecord(
        id=activity_record_id,
        pet_id=pet_id,
        type=activity_type,
        value=activity_value,
        unit=activity_unit,
        date=datetime.utcnow()  
    )

    db.session.add(activity_record)
    db.session.commit()

    return jsonify({"message": "Activity record created successfully"}), 201

@app.route('/ActivityRecord/<activity_id>', methods=['PUT'])
@jwt_required()
def update_activity_record(activity_id):
    user_id = get_jwt_identity()

    activity_record = ActivityRecord.query.get(activity_id)
    
    if activity_record is None:
        return jsonify({'message': 'Activity record not found'}), 404


    pet = Pet.query.get(activity_record.pet_id)
    if pet.owner_id != user_id:
        return jsonify({'message': 'Unauthorized access'}), 401
    
    data = request.get_json()

    if 'type' in data:
        activity_record.type = data['type']
    if 'value' in data:
        activity_record.value = data['value']
    if 'unit' in data:
        activity_record.unit = data['unit']
    if 'date' in data:
        try:
            activity_record.date = datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({'message': "Invalid date format. Use 'YYYY-MM-DDTHH:MM:SS'"}), 400
    
    db.session.commit()
    
    return jsonify({'message': 'Activity record updated successfully'}), 200

@app.route('/ActivityRecord/<activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity_record(activity_id):
    
    user_id = get_jwt_identity()

    activity_record = ActivityRecord.query.get(activity_id)

    if activity_record is None:
        return jsonify({'message': 'Activity record not found'}), 404

    
    pet = Pet.query.get(activity_record.pet_id)
    if pet.owner_id != user_id:
        return jsonify({'message': 'Unauthorized access'}), 401

    
    db.session.delete(activity_record)
    db.session.commit()

    return jsonify({'message': 'Activity record deleted successfully'}), 200


import os

if __name__ == '__main__':
    from models import db  # Ensure this correctly imports your database instance

    # Create the application context
    with app.app_context():
        db.create_all()  # Create all tables within the application context

    # Fetch the port dynamically or use the default
    port = int(os.environ.get('PORT', 7500))

    # Run the Flask app
    app.run(host='0.0.0.0', port=port)