````markdown
# 🔐 VaultFlow: A Secure, Zero-Knowledge File Vault

**VaultFlow** is a privacy-first web-based file storage and sharing platform built on a **Zero-Knowledge Architecture** — meaning the server cannot access your files or passwords.  
All encryption and decryption are done **client-side** using strong, industry-standard cryptography, ensuring **true end-to-end security**.

---

## 🚀 Features

- **🧠 Zero-Knowledge Architecture**  
  The server acts purely as storage — it never sees your plaintext files or passwords.

- **🔒 End-to-End Encryption**  
  Files are encrypted and decrypted exclusively on the client-side using **AES-256-GCM**.

- **🧩 Secure Authentication**  
  Passwords are never stored.  
  - **bcrypt**: For password hashing  
  - **PBKDF2**: For deriving encryption keys

- **📤 Ephemeral & Secure File Sharing**  
  Generate **time-limited, password-protected links** using a client-side re-keying process.

- **💡 Modern Frontend**  
  Clean, responsive UI built with:
  - Drag-and-drop uploads  
  - Password strength meter  
  - Secure password prompts

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | Python (Flask) |
| **Database** | PostgreSQL |
| **Frontend** | HTML, Tailwind CSS, Vanilla JavaScript |
| **Cryptography** | Web Crypto API (AES-256-GCM, PBKDF2), bcrypt |
| **Environment Management** | python-dotenv |

---

## ⚙️ Local Setup

Follow these steps to set up and run **VaultFlow** locally.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
````

### 2. Create a Virtual Environment & Install Dependencies

```bash
python -m venv venv
# Activate environment
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate         # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up the Database

* Connect to your PostgreSQL database (e.g., on **Neon** or local instance).
* Run the SQL commands in `schema.sql` to create the following tables:

  * `users`
  * `files`
  * `shared_files`

### 4. Configure Environment Variables

This project uses a `.env` file for local development secrets.

```bash
# Copy the example file
cp .env.example .env    # (macOS/Linux)
# or
copy .env.example .env  # (Windows)
```

Open the `.env` file and update the database connection string:

```bash
DATABASE_URL="your_actual_database_url_here"
```

> ⚠️ **Note:** The `.env` file is ignored by Git for security reasons.

---

### 5. Run the Application

```bash
python app.py
```

Once running, open your browser and visit:

👉 **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

---

## 🔐 Security Highlights

* All encryption/decryption happens **in-browser** (client-side only).
* The server stores only **ciphertext**, not plaintext data.
* User credentials and encryption keys never leave the client device.

---

## 📸 UI Highlights

* Responsive dashboard for uploads & sharing
* Drag-and-drop file uploads
* Secure password and sharing prompts

---

## 💬 Acknowledgments

Built with ❤️ using:

* Flask
* Tailwind CSS
* Web Crypto API
* PostgreSQL

---

### 👨‍💻 Developer

**VaultFlow** — A project by *Varad Mhatre*
For feedback or suggestions, feel free to open an issue or submit a pull request.

```

---
