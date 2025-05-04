#!/usr/bin/env python3
"""
Run script for the Flask Auth Service API.
This script is the entry point for running the application.
"""

import os
import sys
import logging
from pathlib import Path
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_database_file():
    """Check if the database file exists."""
    try:
        # Get the database path from the config module
        # This ensures we use the same path resolution as the app
        from app.config import Config
        db_path = Config.DATABASE_PATH

        logger.info(f"Checking database file at path: {db_path}")

        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            logger.info("Please run 'python scripts/init_db.py' to initialize the database.")
            return False

        # Try to connect to the database to check if it's valid
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone() is None:
                logger.error(f"Users table not found in database: {db_path}")
                logger.info("Please run 'python scripts/init_db.py' to initialize the database.")
                conn.close()
                return False
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

        logger.info(f"Database file exists and contains users table: {db_path}")
        return True

    except Exception as e:
        logger.error(f"Error checking database file: {e}")
        return False


if __name__ == '__main__':
    # Check if database file exists
    if not check_database_file():
        sys.exit(1)

    # Get environment configuration, default to development
    env = os.environ.get('FLASK_ENV', 'development')

    # Create app with appropriate configuration
    app = create_app(env)

    # Run app
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )
