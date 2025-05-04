# Flask Auth Service CLI Tools Guide

This guide explains how to use the command-line tools included in the Flask Auth Service API project.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Database Initialization](#database-initialization)
- [User Management](#user-management)
  - [Creating Users](#creating-users)
  - [Updating Users](#updating-users)
- [User Listing](#user-listing)
- [Running the API Server](#running-the-api-server)

## Environment Setup

The CLI tools read the database path and other configuration from environment variables or a `.env` file. Create a `.env` file in the project root with the following content:

```
DATABASE_PATH=auth.db
JWT_SECRET_KEY=your-secret-key-change-in-production
```

Alternatively, you can set these as environment variables:

```bash
export DATABASE_PATH=auth.db
export JWT_SECRET_KEY=your-secret-key-change-in-production
```

## Database Initialization

Use the `init_db.py` script to initialize the database with the required schema:

```bash
python scripts/init_db.py
```

### Options:

- `--db-path`: Path to the SQLite database file (default: read from .env or use auth.db)
- `--sql-file`: Path to the SQL file (default: sql/create_tables.sql)
- `--env-file`: Path to the environment file (default: .env)

### Examples:

Initialize with default settings:
```bash
python scripts/init_db.py
```

Initialize with a custom database path:
```bash
python scripts/init_db.py --db-path /path/to/custom/auth.db
```

Use a different SQL file:
```bash
python scripts/init_db.py --sql-file /path/to/custom/schema.sql
```

## User Management

The `create_user.py` script provides commands to create and update users.

### Creating Users

```bash
python scripts/create_user.py create <username> [options]
```

#### Options:

- `--password`: Password for the new user (if not provided, a random one will be generated)
- `--role`: Role for the new user, choices: normal, platinum (default: normal)
- `--email`: Email address for the new user (optional)
- `--db-path`: Path to the SQLite database file (default: read from .env or use auth.db)
- `--env-file`: Path to the environment file (default: .env)

#### Examples:

Create a normal user with a random password:
```bash
python scripts/create_user.py create john_doe
```

Create a platinum user with a specific password and email:
```bash
python scripts/create_user.py create jane_doe --password SecurePass123 --role platinum --email jane@example.com
```

### Updating Users

```bash
python scripts/create_user.py update <username> [options]
```

#### Options:

- `--password`: New password for the user (optional)
- `--role`: New role for the user, choices: normal, platinum (optional)
- `--email`: New email address for the user (optional)
- `--activate`: Activate the user
- `--deactivate`: Deactivate the user
- `--db-path`: Path to the SQLite database file (default: read from .env or use auth.db)
- `--env-file`: Path to the environment file (default: .env)

#### Examples:

Change a user's password:
```bash
python scripts/create_user.py update john_doe --password NewSecurePass456
```

Upgrade a user to platinum:
```bash
python scripts/create_user.py update john_doe --role platinum
```

Update a user's email:
```bash
python scripts/create_user.py update john_doe --email john.new@example.com
```

Deactivate a user:
```bash
python scripts/create_user.py update john_doe --deactivate
```

## User Listing

The `list_user.py` script allows you to view and filter users in the database:

```bash
python scripts/list_user.py [options]
```

### Options:

- `-n`, `--limit`: Limit the number of users displayed
- `-name`, `--username`: Filter users by username
- `-email`: Filter users by email
- `-normal`: Show only normal users
- `-platinum`: Show only platinum users
- `--db-path`: Path to the SQLite database file (default: read from .env or use auth.db)
- `--env-file`: Path to the environment file (default: .env)

### Examples:

List all users:
```bash
python scripts/list_user.py
```

List only the first 5 users:
```bash
python scripts/list_user.py -n 5
```

Find a specific user by username:
```bash
python scripts/list_user.py -name john_doe
```

Find users with a specific email:
```bash
python scripts/list_user.py -email john@example.com
```

List only platinum users:
```bash
python scripts/list_user.py -platinum
```

List only normal users:
```bash
python scripts/list_user.py -normal
```

## Running the API Server

To start the Flask API server:

```bash
python app/run.py
```

You can set the following environment variables to configure the server:

- `FLASK_ENV`: Environment to use (development, testing, production)
- `FLASK_HOST`: Host address to bind to (default: 0.0.0.0)
- `FLASK_PORT`: Port to listen on (default: 5000)

Example:
```bash
export FLASK_ENV=development
export FLASK_PORT=8000
python app/run.py
```

## API Endpoints

The following API endpoints are available when the server is running:

- `POST /api/user/register`: Register a new user (normal role only)
- `POST /api/user/login`: Login with username/email and password
- `GET /api/user/me`: Get current user information (requires authentication)

See the project documentation for detailed API usage instructions.