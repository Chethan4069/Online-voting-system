from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import base64
import os
import re
from datetime import datetime
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Basic Setup ---
app = Flask(__name__)
CORS(app)

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_NAME = os.path.join(BASE_DIR, 'voters.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'a-default-fallback-secret-key')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"[*] Database is located at: {DATABASE_NAME}")
print(f"[*] Image uploads are in: {UPLOAD_FOLDER}")

# --- Helper Functions ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def hash_data(data_string):
    """Hashes a string using SHA-256 for security."""
    return hashlib.sha256(data_string.encode()).hexdigest()

def save_photo(base64_image_data, aadhaar_number):
    """Saves a base64 encoded image to a file and returns the file path."""
    try:
        # Check if the base64 string has a header and split it
        if "," in base64_image_data:
            header, encoded = base64_image_data.split(",", 1)
        else:
            encoded = base64_image_data
            
        image_data = base64.b64decode(encoded)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{aadhaar_number}_{timestamp}.jpeg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        print(f"[SUCCESS] Photo saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to save photo: {e}")
        return None

# --- API Endpoint ---
@app.route('/register', methods=['POST'])
def register_voter():
    """Handles the voter registration request."""
    print("\n[INFO] Received a new registration request.")
    data = request.get_json()
    
    if not data:
        print("[ERROR] Request body is empty or not JSON.")
        return jsonify({"error": "Invalid request: Missing JSON body"}), 400

    required_fields = ['name', 'dob', 'aadhaar_number', 'voter_id', 'phone_number', 'photo']
    if not all(field in data and data[field] for field in required_fields):
        print(f"[ERROR] Missing one or more required fields. Received keys: {list(data.keys())}")
        return jsonify({"error": "Missing required fields"}), 400

    photo_path = save_photo(data['photo'], data['aadhaar_number'])
    if not photo_path:
        return jsonify({"error": "Server failed to process and save the photo"}), 500

    conn = None  # Initialize connection variable to None
    try:
        conn = get_db_connection()
        if not conn:
            # This will be triggered if get_db_connection returns None
            return jsonify({"error": "Failed to establish a database connection."}), 500
            
        cursor = conn.cursor()
        aadhaar_hash = hash_data(data['aadhaar_number'])
        
        print(f"[INFO] Executing INSERT statement for voter: {data['name']}")
        cursor.execute(
            """
            INSERT INTO voters (name, dob, aadhaar_hash, voter_id, phone_number, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data['name'], data['dob'], aadhaar_hash, data['voter_id'].upper(), data['phone_number'], photo_path)
        )
        conn.commit()
        print(f"[SUCCESS] Voter '{data['name']}' has been inserted into the database.")

    except sqlite3.IntegrityError:
        print("[ERROR] IntegrityError: A voter with this Aadhaar or Voter ID already exists.")
        return jsonify({"error": "A user with this Aadhaar or Voter ID is already registered."}), 409
    except Exception as e:
        print(f"[ERROR] A critical database error occurred: {e}")
        # Optionally, you can perform a rollback here if needed: conn.rollback()
        return jsonify({"error": f"A server-side database error occurred: {str(e)}"}), 500
    finally:
        # This block ensures the connection is closed, whether the try block succeeded or failed.
        if conn:
            conn.close()
            print("[INFO] Database connection closed.")

    return jsonify({"message": "Registration request sent successfully! An officer will review your application."}), 201

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)

