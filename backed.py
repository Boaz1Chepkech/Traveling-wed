from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
import os
import re
import logging

# Initialize app and database
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask app")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_planner.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
db = SQLAlchemy(app)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# User table with email as primary key
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    trips = db.relationship('TripPlan', backref='user', lazy=True)

# Trip planning table
class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)  # Changed to db.Date
    end_date = db.Column(db.Date, nullable=False)
    travelers = db.Column(db.Integer, nullable=False)
    travel_style = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)

# Helper function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Register a new user with email as primary key
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['email', 'username', 'password']
    
    # Check for missing fields
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing {field}'}), 400

    if not is_valid_email(data['email']):
        return jsonify({'message': 'Invalid email address'}), 400

    # Check if the email is already registered
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(email=data['email'], username=data['username'], password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error registering user: {e}")
        return jsonify({'message': 'Failed to register user', 'error': str(e)}), 500

    return jsonify({'message': 'User registered successfully'})


# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    required_fields = ['email', 'password']
    
    # Check for missing fields
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing {field}'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id  # Storing user ID in session
        app.logger.debug(f"User {data['email']} logged in successfully")
        return jsonify({'message': 'Logged in successfully'})
    
    return jsonify({'message': 'Invalid credentials'}), 401


# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})


# Home route with session check
@app.route('/home', methods=['GET'])
def home():
    if 'user_id' in session:
        return jsonify({'message': 'Welcome to the home page!'})
    return jsonify({'message': 'Please log in first'}), 401


# Add trip plan for a logged-in user
@app.route('/travel', methods=['POST'])
def plan_trip():
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to plan a trip'}), 401

    data = request.get_json()
    required_fields = ['destination', 'start_date', 'end_date', 'travelers', 'travel_style']
    
    # Check for missing fields
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing {field}'}), 400

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format, use YYYY-MM-DD'}), 400

    new_trip = TripPlan(
        destination=data['destination'],
        start_date=start_date,
        end_date=end_date,
        travelers=data['travelers'],
        travel_style=data['travel_style'],
        user_email=session['user_id']
    )
    
    try:
        db.session.add(new_trip)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error planning trip: {e}")
        return jsonify({'message': 'Failed to plan trip', 'error': str(e)}), 500

    return jsonify({'message': 'Trip planned successfully'})


# Get all trips for the logged-in user with pagination
@app.route('/trips', methods=['GET'])
def get_trips():
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to view trips'}), 401

    page = request.args.get('page', 1, type=int)  # Default to page 1
    trips = TripPlan.query.filter_by(user_email=session['user_id']).paginate(page, 10, False)

    trips_data = [
        {
            'destination': trip.destination,
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'travelers': trip.travelers,
            'travel_style': trip.travel_style
        }
        for trip in trips.items
    ]
    
    return jsonify({
        'trips': trips_data,
        'total': trips.total,
        'pages': trips.pages,
        'current_page': trips.page
    })


# Initialize the database (only needed the first time)
if __name__ == '__main__':
    db.create_all()  # Creates the database tables if they don't exist
    app.run(debug=True)
