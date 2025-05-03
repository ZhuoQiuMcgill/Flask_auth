-- sql/create_tables.sql
-- These statements will be executed in the auth.db file
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('normal', 'platinum')),
    creation_method TEXT NOT NULL CHECK(creation_method IN ('web', 'local')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email TEXT UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT 1
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_email ON users (email);