#!/usr/bin/env python3
"""
Flask Auth Service API - API Routes.
This module defines API endpoints for user authentication and management.
"""

from flask import Blueprint, request, jsonify, current_app, g
from marshmallow import ValidationError
from app.models import User
from app.schemas import RegisterSchema, LoginSchema, UserSchema
from app.utils import hash_password, verify_password, generate_jwt, validate_jwt
import functools
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api/user')

# Schemas
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


# Decorator for routes that require authentication
def jwt_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header.'}), 401

        token = auth_header.split(' ')[1]

        # Validate token
        payload = validate_jwt(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token.'}), 401

        # Get user from database
        username = payload.get('sub')
        user = User.find_by_username(username)

        if not user:
            return jsonify({'error': 'User not found.'}), 404

        if not user.is_active:
            return jsonify({'error': 'User is disabled.'}), 401

        # Store user in g
        g.user = user

        return f(*args, **kwargs)

    return decorated


# Routes
@api.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    # Validate request data
    try:
        data = register_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation error.', 'details': e.messages}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # Check if username or email already exists
    user = User.find_by_username(username)
    if user:
        return jsonify({'error': 'Username already exists.'}), 409

    if email:
        user = User.find_by_email(email)
        if user:
            return jsonify({'error': 'Email already exists.'}), 409

    # Create new user
    user = User(
        username=username,
        password_hash=hash_password(password),
        role='normal',
        creation_method='web',
        email=email
    )

    # Save user to database
    try:
        user.save()
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': 'Error creating user.'}), 500

    # Return created user
    return jsonify({
        'message': 'User registered successfully.',
        'user': user_schema.dump(user)
    }), 201


@api.route('/login', methods=['POST'])
def login():
    """Login user."""
    # Validate request data
    try:
        data = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation error.', 'details': e.messages}), 400

    identifier = data.get('identifier')
    password = data.get('password')

    # Find user by identifier (username or email)
    user = User.find_by_identifier(identifier)

    # Check user and password
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials.'}), 401

    # Generate JWT
    token = generate_jwt(user.username, user.role)

    # Return token
    return jsonify({
        'message': 'Login successful.',
        'access_token': token,
        'token_type': 'bearer'
    }), 200


@api.route('/me', methods=['GET'])
@jwt_required
def get_me():
    """Get current user information."""
    return jsonify(user_schema.dump(g.user)), 200