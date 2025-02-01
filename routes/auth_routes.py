from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.gas_request import GasRequest
from models.notification import Notification
from models.outlet import Outlet
from models.user import User

# Creating the blueprint
auth_bp = Blueprint('auth', __name__)


# User Registration Route
@auth_bp.route('/register', methods=['POST'])
def register_user():
    from app import db  # Import db here to avoid circular import issue

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in ['name', 'email', 'phone', 'nic', 'address', 'role', 'password']):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if NIC or email already exists
    existing_user = User.query.filter((User.nic == data['nic']) | (User.email == data['email'])).first()
    if existing_user:
        return jsonify({"message": "User with the given NIC or email already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data['password'])

    # Create a new user
    new_user = User(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        nic=data['nic'],
        address=data['address'],
        role=data['role'],
        password=hashed_password
    )

    # Add the user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    from app import db  # Import db here to avoid circular import issue

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in ['email', 'password']):
        return jsonify({"message": "Missing required fields"}), 400

    email = data['email']
    password = data['password']

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User with the given email does not exist"}), 404

    # Check if the password is correct
    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Store userID in the session
    session['userID'] = user.userID

    # Login successful
    return jsonify({
        "message": "Login successful",
        "userID": user.userID,
        "name": user.name,
        "email": user.email,
        "userType": user.role
    }), 200


# Profile Route
@auth_bp.route('/profile', methods=['GET'])
def profile():
    from app import db  # Import db here to avoid circular import issue

    # Ensure the user is logged in
    if 'userID' not in session:
        return jsonify({"message": "User not logged in"}), 401

    userID = session['userID']
    user = User.query.get(userID)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "userID": user.userID,
        "name": user.name,
        "email": user.email,
        "userType": user.role
    }), 200


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Remove userID from session
    session.pop('userID', None)
    return jsonify({"message": "Logged out successfully"}), 200
