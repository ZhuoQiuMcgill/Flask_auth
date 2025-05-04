#!/usr/bin/env python3
"""
Flask Auth Service API - Application Factory.
This module initializes the Flask application and its extensions.
"""

import os
from flask import Flask
from app.config import config
from app.models import db
from app.database import init_app as init_db_app
import logging

# Try to load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass


def check_database_initialized(app):
    """Check if the database is initialized with required tables."""
    try:
        # First check if the database file exists
        if not os.path.exists(app.config['DATABASE_PATH']):
            app.logger.error(
                f"Database file not found: {app.config['DATABASE_PATH']}. "
                "Please run 'python scripts/init_db.py' to initialize the database."
            )
            return False

        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)

            # Print all tables for debugging
            tables = inspector.get_table_names()
            app.logger.info(f"Tables found in database: {tables}")

            if not inspector.has_table('users'):
                app.logger.error(
                    f"Users table not found in database: {app.config['DATABASE_PATH']}. "
                    f"Tables found: {tables}. "
                    "Please run 'python scripts/init_db.py' to initialize the database."
                )
                return False

            app.logger.info(f"Database initialized successfully with users table: {app.config['DATABASE_PATH']}")
            return True
    except Exception as e:
        app.logger.error(f"Database check failed: {e}")
        return False


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Log database path for debugging
    app.logger.info(f"Using database path: {app.config['DATABASE_PATH']}")
    app.logger.info(f"Database file exists: {os.path.exists(app.config['DATABASE_PATH'])}")

    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE_PATH']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    init_db_app(app)

    # Check if database is initialized
    if not check_database_initialized(app):
        app.logger.warning(
            "Application started with uninitialized database. "
            "Some features may not work correctly."
        )

    # Register blueprints
    from app.routes import api
    app.register_blueprint(api)

    return app
