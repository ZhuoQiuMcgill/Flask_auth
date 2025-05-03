#!/usr/bin/env python3
"""
User management script.
This script allows creating or updating users in the auth.db database.
It can create normal or platinum users with creation_method='local'.
"""

import os
import sys
import sqlite3
import argparse
import logging
import re
import string
import random
from pathlib import Path
from datetime import datetime

# Import password hashing library
try:
    from argon2 import PasswordHasher

    HASH_METHOD = "argon2"
except ImportError:
    try:
        import bcrypt

        HASH_METHOD = "bcrypt"
    except ImportError:
        print("Error: Neither argon2-cffi nor bcrypt is installed.")
        print("Please install one of them: pip install argon2-cffi or pip install bcrypt")
        sys.exit(1)

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


def get_sql_template(template_file):
    """Read a SQL template file."""
    try:
        with open(template_file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_file}")
        return None


def hash_password(password):
    """Hash a password using the available method."""
    if HASH_METHOD == "argon2":
        ph = PasswordHasher()
        return ph.hash(password)
    else:  # bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def validate_email(email):
    """Validate email format."""
    if not email:
        return True  # Empty email is allowed

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_username(username):
    """Validate username format."""
    if not username:
        return False

    # Username must be 3-30 characters, alphanumeric with underscores and hyphens
    username_pattern = r'^[a-zA-Z0-9_-]{3,30}$'
    return bool(re.match(username_pattern, username))


def generate_password(length=12):
    """Generate a random password."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))


def user_exists(conn, username):
    """Check if a user exists in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None


def create_user(conn, username, password_hash, role, email=None):
    """Create a new user in the database."""
    cursor = conn.cursor()

    # Prepare the email value for SQL
    email_value = f"'{email}'" if email else "NULL"

    # Use the template to create the SQL
    template = get_sql_template('sql/insert_user.sql.template')
    if not template:
        logger.error("Failed to read insert user SQL template")
        return False

    # Replace template variables
    sql = template.replace('${username}', username)
    sql = sql.replace('${password_hash}', password_hash)
    sql = sql.replace('${role}', role)
    sql = sql.replace('${creation_method}', 'local')
    sql = sql.replace('${email}', email_value)

    try:
        cursor.executescript(sql)
        conn.commit()
        logger.info(f"User '{username}' created successfully with role '{role}'")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error while creating user: {e}")
        return False


def update_user(conn, username, password=None, role=None, email=None, is_active=None):
    """Update an existing user in the database."""
    cursor = conn.cursor()

    # Prepare the set clauses
    password_set = f"password_hash = '{hash_password(password)}'," if password else ""
    email_set = f"email = '{email}'," if email else ""
    is_active_value = 1 if is_active else 0 if is_active is not None else 1

    # Use the template to create the SQL
    template = get_sql_template('sql/update_user.sql.template')
    if not template:
        logger.error("Failed to read update user SQL template")
        return False

    # Replace template variables
    sql = template.replace('${username}', username)
    sql = sql.replace('${role}', role or 'normal')
    sql = sql.replace('${password_set}', password_set)
    sql = sql.replace('${email_set}', email_set)
    sql = sql.replace('${is_active}', str(is_active_value))

    try:
        cursor.executescript(sql)
        if cursor.rowcount == 0:
            logger.warning(f"No user found with username '{username}'")
            return False

        conn.commit()
        logger.info(f"User '{username}' updated successfully")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error while updating user: {e}")
        return False


def main():
    """Main function to parse arguments and manage users."""
    parser = argparse.ArgumentParser(description='Create or update users in the auth database.')

    # Database connection options
    parser.add_argument(
        '--db-path',
        help='Path to the SQLite database file (default: read from .env or use auth.db)'
    )
    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to the environment file (default: .env)'
    )

    # User management subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create user command
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('username', help='Username for the new user')
    create_parser.add_argument(
        '--password',
        help='Password for the new user (if not provided, a random one will be generated)'
    )
    create_parser.add_argument(
        '--role',
        choices=['normal', 'platinum'],
        default='normal',
        help='Role for the new user (default: normal)'
    )
    create_parser.add_argument(
        '--email',
        help='Email address for the new user (optional)'
    )

    # Update user command
    update_parser = subparsers.add_parser('update', help='Update an existing user')
    update_parser.add_argument('username', help='Username of the user to update')
    update_parser.add_argument(
        '--password',
        help='New password for the user (optional)'
    )
    update_parser.add_argument(
        '--role',
        choices=['normal', 'platinum'],
        help='New role for the user (optional)'
    )
    update_parser.add_argument(
        '--email',
        help='New email address for the user (optional)'
    )
    update_parser.add_argument(
        '--activate',
        action='store_true',
        help='Activate the user'
    )
    update_parser.add_argument(
        '--deactivate',
        action='store_true',
        help='Deactivate the user'
    )

    args = parser.parse_args()

    # Validate command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get database path
    db_path = args.db_path or get_db_path(args.env_file)

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Process command
    if args.command == 'create':
        # Validate inputs
        if not validate_username(args.username):
            logger.error(
                "Invalid username. Username must be 3-30 characters, alphanumeric with underscores and hyphens.")
            sys.exit(1)

        if args.email and not validate_email(args.email):
            logger.error("Invalid email format.")
            sys.exit(1)

        # Check if user already exists
        if user_exists(conn, args.username):
            logger.error(f"User '{args.username}' already exists. Use the 'update' command to modify existing users.")
            sys.exit(1)

        # Generate password if not provided
        password = args.password
        if not password:
            password = generate_password()
            logger.info(f"Generated random password for user '{args.username}': {password}")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        if create_user(conn, args.username, password_hash, args.role, args.email):
            logger.info(f"User '{args.username}' created successfully")
        else:
            logger.error(f"Failed to create user '{args.username}'")
            sys.exit(1)

    elif args.command == 'update':
        # Check if user exists
        if not user_exists(conn, args.username):
            logger.error(f"User '{args.username}' does not exist. Use the 'create' command to create a new user.")
            sys.exit(1)

        # Validate email if provided
        if args.email and not validate_email(args.email):
            logger.error("Invalid email format.")
            sys.exit(1)

        # Determine is_active value
        is_active = None
        if args.activate and args.deactivate:
            logger.error("Cannot both activate and deactivate a user.")
            sys.exit(1)
        elif args.activate:
            is_active = True
        elif args.deactivate:
            is_active = False

        # Update user
        if update_user(conn, args.username, args.password, args.role, args.email, is_active):
            logger.info(f"User '{args.username}' updated successfully")
        else:
            logger.error(f"Failed to update user '{args.username}'")
            sys.exit(1)

    # Close database connection
    conn.close()


if __name__ == "__main__":
    main()
