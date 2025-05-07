#!/usr/bin/env python3
"""
Flask Auth Service API - Configuration Settings.
This module contains configuration classes for different environments.
"""

import os
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def get_absolute_db_path(db_path):
    """Convert database path to absolute path if it's not already absolute."""
    if not os.path.isabs(db_path):
        return os.path.abspath(db_path)
    return db_path


class Config:
    """Base configuration class."""
    # SQLite database path - always use absolute path
    db_path = os.environ.get('DATABASE_PATH', 'auth.db')
    DATABASE_PATH = get_absolute_db_path(db_path)

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
    DATABASE_PATH = get_absolute_db_path('test_auth.db')


class ProductionConfig(Config):
    """Production configuration."""
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        # Log a warning instead of raising an error
        logger.warning("JWT_SECRET_KEY not set in environment, using default (NOT SECURE FOR PRODUCTION)")
        JWT_SECRET_KEY = Config.JWT_SECRET_KEY

    PASSWORD_HASH_ROUNDS = 14  # Higher for production


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
