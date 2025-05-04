#!/usr/bin/env python3
"""
User listing script.
This script displays user information from the auth.db database with filtering options.
"""

import os
import sys
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


def fetch_users(conn, limit=None, username=None, email=None, role=None):
    """Fetch users from the database based on filters."""
    cursor = conn.cursor()

    # Start with base query
    query = "SELECT username, role, creation_method, created_at, email, is_active FROM users"
    params = []

    # Add filters
    conditions = []
    if username:
        conditions.append("username = ?")
        params.append(username)
    if email:
        conditions.append("email = ?")
        params.append(email)
    if role:
        conditions.append("role = ?")
        params.append(role)

    # Add WHERE clause if we have conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add ordering
    query += " ORDER BY username"

    # Add limit if specified
    if limit:
        query += f" LIMIT {limit}"

    # Execute query
    cursor.execute(query, params)

    # Fetch results
    return cursor.fetchall()


def display_users(users):
    """Display users in a nicely formatted table."""
    if not users:
        logger.info("No users found matching the specified criteria.")
        return

    # Define headers
    headers = ["Username", "Role", "Creation Method", "Created At", "Email", "Active"]

    # Calculate maximum width for each column
    widths = [len(h) for h in headers]
    for user in users:
        for i in range(len(headers)):
            value = str(user[i] if user[i] is not None else "N/A")
            widths[i] = max(widths[i], min(len(value), 40))  # Limit column width to 40 chars

    # Define formatting string for each row
    fmt = ' | '.join('{:<' + str(w) + '}' for w in widths)

    # Calculate total width
    total_width = sum(widths) + (len(widths) - 1) * 3

    # Print headers
    print(fmt.format(*headers))
    print('-' * total_width)

    # Print each user
    for user in users:
        # Format row data
        row_data = [
            user[0],  # username
            user[1],  # role
            user[2],  # creation_method
            user[3],  # created_at
            user[4] if user[4] else "N/A",  # email (or N/A if None)
            "Yes" if user[5] else "No"  # is_active
        ]

        # Truncate long values
        row_data = [str(val)[:40] + ('...' if len(str(val)) > 40 else '') for val in row_data]

        print(fmt.format(*row_data))

    print(f"\nTotal users: {len(users)}")


def main():
    """Main function to parse arguments and list users."""
    parser = argparse.ArgumentParser(description='List users from the auth database.')

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

    # Filtering options
    parser.add_argument(
        '-n', '--limit',
        type=int,
        help='Limit the number of users displayed'
    )
    parser.add_argument(
        '-name', '--username',
        help='Filter users by username'
    )
    parser.add_argument(
        '-email',
        help='Filter users by email'
    )

    # Role filter group
    role_group = parser.add_mutually_exclusive_group()
    role_group.add_argument(
        '-normal',
        action='store_true',
        help='Show only normal users'
    )
    role_group.add_argument(
        '-platinum',
        action='store_true',
        help='Show only platinum users'
    )

    args = parser.parse_args()

    # Get database path
    db_path = args.db_path or get_db_path(args.env_file)

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

    # Determine role filter
    role = None
    if args.normal:
        role = 'normal'
    elif args.platinum:
        role = 'platinum'

    # Fetch users
    users = fetch_users(
        conn,
        limit=args.limit,
        username=args.username,
        email=args.email,
        role=role
    )

    # Display users
    display_users(users)

    # Close database connection
    conn.close()


if __name__ == "__main__":
    main()
