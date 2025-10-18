import os
import psycopg2
import bcrypt
import uuid
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# FIX: Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# FIX: Use the correct environment variable name
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("FATAL ERROR: DATABASE_URL is not set in your .env file.")

try:
    conn = psycopg2.connect(DATABASE_URL)
except psycopg2.OperationalError as e:
    raise RuntimeError(f"FATAL ERROR: Could not connect to the database. Check your DATABASE_URL. Error: {e}")

# REMOVED: The fragile @before_request and @after_request handlers.
# Cursor management is now handled inside each function.

@app.route("/")
def index():
    if "user_id" in session: return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        email, password = request.form["email"], request.form["password"]
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        salt_id = os.urandom(16).hex()
        # FIX: Use a 'with' block for robust cursor management
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (email, password_hash, salt_id) VALUES (%s, %s, %s)", (email, password_hash, salt_id))
        conn.commit()
        return jsonify({"success": True, "message": "Registration successful! Please log in."})
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({"success": False, "message": "Email already exists."}), 400
    except Exception as e:
        conn.rollback()
        print(f"Error in /register: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        email, password = request.form["email"], request.form["password"]
        # FIX: Use a 'with' block for robust cursor management
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password_hash, salt_id FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
        
        if user:
            user_id, stored_hash, salt_id = user
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                session["user_id"], session["email"] = user_id, email
                return jsonify({"success": True, "salt": salt_id})
        
        return jsonify({"success": False, "message": "Invalid credentials."}), 401
    except Exception as e:
        print(f"Error in /login: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("index"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/upload", methods=["POST"])
def upload_file():
    if "user_id" not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        if 'file' not in request.files or 'filename' not in request.form: return jsonify({"success": False, "message": "Missing file or filename"}), 400
        user_id = session["user_id"]
        encrypted_file, original_filename = request.files['file'], request.form['filename']
        encrypted_data = encrypted_file.read()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO files (user_id, original_filename, encrypted_data) VALUES (%s, %s, %s)", (user_id, original_filename, encrypted_data))
        conn.commit()
        return jsonify({"success": True, "message": "File uploaded successfully."})
    except Exception as e:
        conn.rollback()
        print(f"Error in /upload: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/files", methods=["GET"])
def list_files():
    if "user_id" not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        user_id = session["user_id"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, original_filename, created_at FROM files WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            files = [{"id": r[0], "name": r[1], "date": r[2].strftime("%Y-%m-%d %H:%M:%S")} for r in cursor.fetchall()]
        return jsonify(files)
    except Exception as e:
        print(f"Error in /files: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    if "user_id" not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        user_id = session["user_id"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT encrypted_data, original_filename FROM files WHERE id = %s AND user_id = %s", (file_id, user_id))
            file_data = cursor.fetchone()
        if file_data:
            encrypted_blob, original_filename = file_data
            return Response(bytes(encrypted_blob), mimetype='application/octet-stream', headers={"Content-Disposition": f"attachment;filename={original_filename}.enc"})
        return jsonify({"success": False, "message": "File not found or permission denied"}), 404
    except Exception as e:
        print(f"Error in /download: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    if "user_id" not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        user_id = session["user_id"]
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM files WHERE id = %s AND user_id = %s RETURNING id", (file_id, user_id))
            deleted_id = cursor.fetchone()
        conn.commit()
        if deleted_id: return jsonify({"success": True, "message": "File deleted."})
        return jsonify({"success": False, "message": "File not found or permission denied."}), 404
    except Exception as e:
        conn.rollback()
        print(f"Error in /delete: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/create-share", methods=["POST"])
def create_share():
    if "user_id" not in session: return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        if 'file' not in request.files or 'salt' not in request.form or 'filename' not in request.form:
            return jsonify({"success": False, "message": "Missing required data for sharing."}), 400
        re_encrypted_file = request.files['file']
        new_salt, original_filename = request.form['salt'], request.form['filename']
        re_encrypted_data = re_encrypted_file.read()
        share_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO shared_files (share_id, encrypted_data, salt_id, original_filename, expires_at) VALUES (%s, %s, %s, %s, %s)", (str(share_id), re_encrypted_data, new_salt, original_filename, expires_at))
        conn.commit()
        share_link = url_for('serve_share_page', share_id=share_id, _external=True)
        return jsonify({"success": True, "link": share_link})
    except Exception as e:
        conn.rollback()
        print(f"An error occurred in /create-share: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

@app.route("/share/<uuid:share_id>")
def serve_share_page(share_id):
    return render_template("share.html", share_id=share_id)

@app.route("/api/share/<uuid:share_id>", methods=["GET"])
def get_share_data(share_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT encrypted_data, salt_id, original_filename FROM shared_files WHERE share_id = %s AND expires_at > %s", (str(share_id), datetime.now(timezone.utc)))
            shared_file = cursor.fetchone()
            if shared_file:
                encrypted_data, salt_id, original_filename = shared_file
                encrypted_data_hex = bytes(encrypted_data).hex()
                cursor.execute("DELETE FROM shared_files WHERE share_id = %s", (str(share_id),))
                conn.commit()
                return jsonify({"success": True, "encryptedData": encrypted_data_hex, "salt": salt_id, "filename": original_filename})
        return jsonify({"success": False, "message": "This link has expired or is invalid."}), 404
    except Exception as e:
        conn.rollback()
        print(f"An error occurred in /api/share: {e}")
        return jsonify({"success": False, "message": "An internal server error occurred."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)

