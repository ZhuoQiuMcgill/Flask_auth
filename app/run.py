#!/usr/bin/env python3
"""
Run script for the Flask Auth Service API.
This script is the entry point for running the application.
"""

import os
from app import create_app

# Get environment configuration
env = os.environ.get('FLASK_ENV', 'development')

# Create app with appropriate configuration
app = create_app(env)

if __name__ == '__main__':
    # Run app
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )