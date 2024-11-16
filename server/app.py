from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Pet, HealthRecord, Appointment, ActivityRecord
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def create_app(test_config=None):
    # Initialize the Flask app
    app = Flask(__name__)

    # If test_config is provided, use it to configure the app
    if test_config:
        app.config.from_mapping(test_config)
    else:
        # App configurations from .env file
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    # Register the routes
    @app.route('/')
    def index():
        return "Pet App Database"

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        # username = data['username']
        email = data['email']
        password = generate_password_hash(data['password'])

        user = User(email=email, password=password)
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
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

    @app.route('/pets', methods=['POST'])
    @jwt_required()
    def add_pet():
        data = request.get_json()
        name = data['name']
        type = data['type']
        breed = data['breed']
        gender = data['gender']
        date_of_birth = datetime.strptime(data['date_of_birth'], "%Y-%m-%d")

        owner_id = get_jwt_identity()
        user = User.query.get(owner_id)
        if not user:
            return jsonify({"message": "Invalid user"}), 401
        
        pet = Pet(name=name, type=type, breed=breed, gender=gender, date_of_birth=date_of_birth, owner_id=owner_id)
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
        if not pet or pet.owner_id != get_jwt_identity():
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
        if not pet or pet.owner_id != get_jwt_identity():
            return jsonify({'message': 'Pet not found'}), 404
        
        pet.name = data['name']
        pet.type = data['type']
        pet.breed = data['breed']
        pet.gender = data['gender']
        pet.date_of_birth = datetime.strptime(data['date_of_birth'], "%Y-%m-%d")

        db.session.commit()
        return jsonify({'message': 'Pet updated successfully'}), 200

    @app.route('/pets/<pet_id>', methods=['DELETE'])
    @jwt_required()
    def delete_pet(pet_id):
        pet = Pet.query.get(pet_id)
        if not pet or pet.owner_id != get_jwt_identity():
            return jsonify({'message': 'Pet not found'}), 404
        
        db.session.delete(pet)
        db.session.commit()
        return jsonify({'message': 'Pet deleted successfully'}), 200

    @app.route('/appointment', methods=['GET', 'POST'])
    @jwt_required()
    def appointment():
        if request.method == 'GET':
            current_user_id = get_jwt_identity()
            appointments = Appointment.query.filter_by(owner_id=current_user_id).all()
            return jsonify([{
                "id": appointment.id,
                "pet_id": appointment.pet_id,
                "date": appointment.date.isoformat(),
                "notes": appointment.notes
            } for appointment in appointments]), 200
        elif request.method == 'POST':
            data = request.get_json()
            pet_id = data['pet_id']
            date = datetime.strptime(data['date'], "%Y-%m-%d")
            notes = data['notes']

            appointment = Appointment(pet_id=pet_id, date=date, notes=notes, owner_id=get_jwt_identity())
            db.session.add(appointment)
            db.session.commit()
            return jsonify({'message': 'Appointment created successfully'}), 201

    @app.route('/activity', methods=['GET', 'POST'])
    @jwt_required()
    def activity_record():
        if request.method == 'GET':
            current_user_id = get_jwt_identity()
            activity_records = ActivityRecord.query.filter_by(owner_id=current_user_id).all()
            return jsonify([{
                "id": record.id,
                "pet_id": record.pet_id,
                "date": record.date.isoformat(),
                "type": record.type,
                "duration": record.duration
            } for record in activity_records]), 200
        elif request.method == 'POST':
            data = request.get_json()
            pet_id = data['pet_id']
            date = datetime.strptime(data['date'], "%Y-%m-%d")
            type = data['type']
            duration = data['duration']

            activity_record = ActivityRecord(pet_id=pet_id, date=date, type=type, duration=duration, owner_id=get_jwt_identity())
            db.session.add(activity_record)
            db.session.commit()
            return jsonify({'message': 'Activity recorded successfully'}), 201

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=7505, debug=True)
