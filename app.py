from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from argon2 import PasswordHasher

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
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    eco = sqlite3.connect("file.db")
    cursor = eco.cursor()
    cursor.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
    eco.commit()
    eco.close()
    return jsonify({"message": f"User {user_id} deleted"}),200


if __name__ == "__main__":
    app.run(debug=True)