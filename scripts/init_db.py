#!/usr/bin/env python3
"""
Database initialization script.
This script reads the SQL in sql/create_tables.sql and executes it to initialize the auth.db database.
"""

import os
import sqlite3
import argparse
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_path(env_file='.env'):
    """Get the database path from the environment or .env file."""
    # First, try to use the same path resolution as the Flask app
    try:
        # Add the parent directory to sys.path if needed
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)

        if parent_dir not in sys.path:
            sys.path.append(parent_dir)

        from app.config import Config
        db_path = Config.DATABASE_PATH
        logger.info(f"Using database path from app config: {db_path}")
        return db_path
    except ImportError:
        pass

    # If that fails, fall back to our own path resolution
    # First check if DATABASE_PATH is in environment
    db_path = os.environ.get('DATABASE_PATH')

    # If not, try to read from .env file
    if not db_path and os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('DATABASE_PATH='):
                    db_path = line.strip().split('=', 1)[1].strip("'\"")
                    break

    # Default to auth.db in the project root if not found
    if not db_path:
        db_path = 'auth.db'
        logger.warning(f"DATABASE_PATH not found in environment or .env file. Using default: {db_path}")

    # Convert to absolute path if it's relative
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)
        logger.info(f"Using absolute database path: {db_path}")

    return db_path


def check_tables_exist(db_path):
    """Check if the users table already exists in the database."""
    if not os.path.exists(db_path):
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error:
        return False


def init_db(db_path, sql_file, force=False):
    """Initialize the database by executing the SQL file."""
    # Check if tables already exist
    if check_tables_exist(db_path) and not force:
        logger.info(f"Database already initialized with required tables: {db_path}")
        return True

    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created directory: {db_dir}")

    # Read SQL file
    try:
        with open(sql_file, 'r') as f:
            sql_script = f.read()
    except FileNotFoundError:
        logger.error(f"SQL file not found: {sql_file}")
        return False

    # Connect to database and execute SQL
    try:
        conn = sqlite3.connect(db_path)
        conn.executescript(sql_script)
        conn.commit()
        logger.info(f"Database initialized successfully: {db_path}")
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return False


def main():
    """Main function to parse arguments and initialize the database."""
    parser = argparse.ArgumentParser(description='Initialize the auth database.')
    parser.add_argument(
        '--db-path',
        help='Path to the SQLite database file (default: read from .env or use auth.db)'
    )
    parser.add_argument(
        '--sql-file',
        default='sql/create_tables.sql',
        help='Path to the SQL file (default: sql/create_tables.sql)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to the environment file (default: .env)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reinitialize the database even if tables already exist'
    )

    args = parser.parse_args()

    # Get database path
    db_path = args.db_path or get_db_path(args.env_file)

    # Initialize database
    if init_db(db_path, args.sql_file, args.force):
        logger.info("Database initialization completed successfully.")
        logger.info(f"You can now create users with: python scripts/create_user.py create <username>")
    else:
        logger.error("Database initialization failed.")
        exit(1)


if __name__ == "__main__":
    main()
