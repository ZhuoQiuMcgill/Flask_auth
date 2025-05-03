#!/usr/bin/env python3
"""
Flask Auth Service API - Database Connection Utilities.
This module provides database connection and session management functions.
"""

import sqlite3
from flask import g, current_app


def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    """Initialize app with database functions."""
    app.teardown_appcontext(close_db)


# Raw SQL operations (if needed)
def execute_sql(sql, params=None):
    """Execute SQL statement."""
    db = get_db()
    cursor = db.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    db.commit()

    return cursor


def execute_sql_file(file_path):
    """Execute SQL file."""
    with open(file_path, 'r') as f:
        sql = f.read()

    db = get_db()
    db.executescript(sql)
    db.commit()