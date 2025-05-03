#!/usr/bin/env python3
"""
Flask Auth Service API - Utility Functions.
This module provides helper functions for password hashing, JWT generation/validation, etc.
"""

import jwt
from datetime import datetime, timedelta
from flask import current_app
import bcrypt

try:
    from argon2 import PasswordHasher

    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False


# Password hashing functions
def hash_password(password):
    """Hash password using preferred algorithm."""
    if HAS_ARGON2:
        ph = PasswordHasher()
        return ph.hash(password)
    else:
        # Use bcrypt
        rounds = current_app.config.get('PASSWORD_HASH_ROUNDS', 12)
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')


def verify_password(password, password_hash):
    """Verify password against hash."""
    if HAS_ARGON2 and password_hash.startswith('$argon2'):
        try:
            ph = PasswordHasher()
            ph.verify(password_hash, password)
            return True
        except Exception:
            return False
    else:
        # Assume bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# JWT functions
def generate_jwt(username, role):
    """Generate JWT token."""
    payload = {
        'sub': username,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
    }

    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

    # Ensure token is a string
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return token


def validate_jwt(token):
    """Validate JWT token."""
    try:
        return jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
    except jwt.PyJWTError:
        return None