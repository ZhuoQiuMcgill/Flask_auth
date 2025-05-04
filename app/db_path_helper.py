#!/usr/bin/env python3
"""
Database path helper module.
This module provides utility functions for working with database paths consistently.
"""

import os
import logging

logger = logging.getLogger(__name__)

def get_db_path(env_file='.env'):
    """Get the absolute database path from the environment or .env file."""
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