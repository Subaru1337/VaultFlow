VaultFlow: A Secure, Zero-Knowledge File Vault

VaultFlow is a web-based file storage and sharing platform built on a zero-knowledge architecture. This means the server has no technical ability to access user files, guaranteeing complete privacy. All encryption and decryption operations are performed directly in the user's browser using modern, standard cryptographic algorithms.

Core Features

Zero-Knowledge Architecture: The server acts only as a dumb storage provider and has no access to plaintext files or user passwords.

End-to-End Encryption: Files are encrypted and decrypted exclusively on the client-side using AES-256-GCM.

Secure Authentication: User passwords are not stored. Instead, bcrypt is used for hashing, and PBKDF2 is used for deriving the encryption key.

Ephemeral & Secure File Sharing: Users can generate time-limited, password-protected links to share files securely. This is achieved via a client-side "re-keying" process.

Modern Frontend: A clean, responsive UI with features like drag-and-drop uploads, password strength meters, and secure password prompts.

Technology Stack

Backend: Python, Flask

Database: PostgreSQL

Frontend: HTML, Tailwind CSS, Vanilla JavaScript

Cryptography: Web Crypto API (AES-256-GCM, PBKDF2), bcrypt

Environment Management: python-dotenv

How to Run Locally

Clone the repository:

git clone <your-repo-url>
cd <your-repo-folder>


Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Set up the database:

Connect to your PostgreSQL database (e.g., on Neon).

Run the SQL commands provided in schema.sql to create the users, files, and shared_files tables.

Set up environment variables:

This project uses a .env file to manage secret keys for local development.

Make a copy of the example file: cp .env.example .env (on Mac/Linux) or copy .env.example .env (on Windows).

Open the new .env file and replace the placeholder with your actual database connection string. This file is ignored by Git and should never be committed.

DATABASE_URL="your_actual_database_url_here"


Run the application:

python app.py


The application will now start up, reading your DATABASE_URL from the .env file. It will be running at http://127.0.0.1:5001.
