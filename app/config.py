#!/usr/bin/env python3
"""
Flask Auth Service API - Configuration Settings.
This module contains configuration classes for different environments.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""
    # SQLite database path
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'auth.db')

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Password hashing difficulty
    PASSWORD_HASH_ROUNDS = 12  # For bcrypt

    # API prefix
    API_PREFIX = '/api/user'

    # Debug flag
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_PATH = 'test_auth.db'


class ProductionConfig(Config):
    """Production configuration."""
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set in production")

    PASSWORD_HASH_ROUNDS = 14  # Higher for production


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}