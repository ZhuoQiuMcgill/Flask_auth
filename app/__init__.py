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

# Try to load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.config['DATABASE_PATH']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    init_db_app(app)

    # Do not create tables with SQLAlchemy, they're created by SQL scripts

    # Register blueprints
    from app.routes import api
    app.register_blueprint(api)

    return app
