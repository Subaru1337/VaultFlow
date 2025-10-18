-- =================================================================
-- Schema for VaultFlow: A Zero-Knowledge File Encryption Platform
-- =================================================================
-- This script contains the CREATE TABLE commands for PostgreSQL.
-- Run this script in your database to set up the necessary tables.
-- =================================================================

-- Drop tables if they exist to ensure a clean setup.
-- Use with caution in a production environment.
DROP TABLE IF EXISTS shared_files;
DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS users;

-- =================================================================
-- Table: users
-- =================================================================
-- Stores user account information. The password_hash is a bcrypt hash
-- used only for authentication. The salt_id is a public salt given
-- to the client for client-side key derivation.
-- =================================================================
CREATE TABLE users (
id SERIAL PRIMARY KEY,
email TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
salt_id TEXT NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Table: files
-- =================================================================
-- Stores the main, permanently encrypted files for each user.
-- The encrypted_data is an opaque binary blob that the server
-- cannot read. The user_id is a foreign key linked to the users table.
-- ON DELETE CASCADE ensures that if a user is deleted, all their
-- associated files are also automatically deleted.
-- =================================================================
CREATE TABLE files (
id SERIAL PRIMARY KEY,
user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
original_filename TEXT NOT NULL,
encrypted_data BYTEA NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =================================================================
-- Table: shared_files
-- =================================================================
-- Stores temporary, re-encrypted file instances for the secure
-- sharing feature. Each record has a unique UUID for the share link
-- and an expiry timestamp. These records are designed to be ephemeral.
-- =================================================================
CREATE TABLE shared_files (
id SERIAL PRIMARY KEY,
share_id UUID UNIQUE NOT NULL,
encrypted_data BYTEA NOT NULL,
salt_id TEXT NOT NULL,
original_filename TEXT NOT NULL,
expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add an index on share_id for faster lookups
CREATE INDEX idx_share_id ON shared_files(share_id);

-- =================================================================
-- End of Schema
-- =================================================================