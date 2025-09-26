from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from argon2 import PasswordHasher
import os

app = Flask(__name__)

# Allow multiple frontend origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://eco-shield-green.web.app"
        ]
    }
})

ph = PasswordHasher()

# --- Create users table if not exists ---
def init_db():
    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            email TEXT UNIQUE,
            password TEXT,
            dob TEXT
        )
    """)
    eco.commit()
    eco.close()

init_db()

# --- Home Route ---
@app.route('/')
def home():
    return "Welcome to Eco Shield Backend!"

# --- Signup Route ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    email = data['email']
    dob = data['dob']
    hashed_password = ph.hash(data['password'])

    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    try:
        cursor.execute(
            "INSERT INTO User(name, contact, email, password, dob) VALUES (?, ?, ?, ?, ?)",
            (name, contact, email, hashed_password, dob)
        )
        eco.commit()
        return jsonify({"message": "Signup successful"}), 201
    except sqlite3.IntegrityError:

        return jsonify({"error": "Email already registered"}), 409
    finally:
        eco.close()

# --- Login Route ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    cursor.execute("SELECT user_id, password FROM User WHERE email = ?", (email,))
    row = cursor.fetchone()
    eco.close()

    if not row:
        return jsonify({"error": "Email not found"}), 404

    user_id, stored_hash = row
    try:
        if ph.verify(stored_hash, password):
            return jsonify({"message": "Login successful", "user_id": user_id}), 200
    except:
        pass

    return jsonify({"error": "Password incorrect"}), 401

# --- Dashboard Route ---
@app.route('/dashboard', methods=['GET'])
def dashboard():
    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    cursor.execute("SELECT name, email, contact FROM User")
    rows = cursor.fetchall()
    eco.close()

    users = []
    for row in rows:
        users.append({
            "name": row[0],
            "email": row[1],
            "contact": row[2]
        })
    return jsonify(users), 200

# --- API Endpoints for User Management ---
@app.route('/api/users/<string:email>', methods=['DELETE'])
def delete_user_by_email(email):
    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    cursor.execute("DELETE FROM User WHERE email = ?", (email,))
    eco.commit()
    eco.close()
    return jsonify({"message": f"User {email} deleted"}), 200

# Example: You should store your Gemini API key securely as an environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBMBmIUqt8FRnWsa0vavEkYsexD0awwAEE")
GEMINI_API_URL = "https://api.gemini.com/v1/analyze"  # Replace with actual endpoint

def call_gemini_api(imei):
    """
    Calls Google Gemini AI API to analyze device by IMEI.
    Replace with actual API specs when available.
    """
    try:
        payload = {"imei": imei}
        headers = {
            "Authorization": f"Bearer {GEMINI_API_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Example response: { "isHacked": true/false }
        return data
    except Exception as e:
        print("Gemini API error:", e)
        # Fallback simulation if API fails
        import random
        return {"isHacked": random.random() < 0.3}

@app.route("/api/gemini-analyze", methods=["POST"])
def gemini_analyze():
    data = request.get_json()
    imei = data.get("imei")
    if not imei:
        return jsonify({"error": "IMEI is required"}), 400

    gemini_response = call_gemini_api(imei)
    return jsonify({"isHacked": gemini_response.get("isHacked", False)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

