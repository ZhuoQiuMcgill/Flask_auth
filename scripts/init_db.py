#!/usr/bin/env python3
"""
Database initialization script.
This script reads the SQL in sql/create_tables.sql and executes it to initialize the auth.db database.
"""

import os
import sqlite3
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_path(env_file='.env'):
    """Get the database path from the environment or .env file."""
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

    return db_path


def init_db(db_path, sql_file):
    """Initialize the database by executing the SQL file."""
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

    args = parser.parse_args()

    # Get database path
    db_path = args.db_path or get_db_path(args.env_file)

    # Initialize database
    if init_db(db_path, args.sql_file):
        logger.info("Database initialization completed successfully.")
    else:
        logger.error("Database initialization failed.")
        exit(1)


if __name__ == "__main__":
    main()