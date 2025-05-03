#!/usr/bin/env python3
"""
Flask Auth Service API - Database Models.
This module defines SQLAlchemy ORM models that map to the database schema.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model representing the 'users' table in auth.db."""
    __tablename__ = 'users'

    username = db.Column(db.String, primary_key=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    creation_method = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String, unique=True)
    is_active = db.Column(db.Boolean, default=True)

    @classmethod
    def find_by_username(cls, username):
        """Find user by username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        """Find user by email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_identifier(cls, identifier):
        """Find user by username or email."""
        return cls.query.filter(
            (cls.username == identifier) | (cls.email == identifier)
        ).first()

    def save(self):
        """Save user to database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete user from database."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'creation_method': self.creation_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }