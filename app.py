from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
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

# --- Connect to PostgreSQL ---
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)

# --- Create users table if not exists ---
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            name TEXT,
            contact TEXT,
            email TEXT UNIQUE,
            password TEXT,
            dob TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- Home Route ---
@app.route('/')
def home():
    return "Welcome to Eco Shield Backend with PostgreSQL!"

# --- Signup Route ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    email = data['email']
    dob = data['dob']
    hashed_password = ph.hash(data['password'])

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, contact, email, password, dob) VALUES (%s, %s, %s, %s, %s)",
            (name, contact, email, hashed_password, dob)
        )
        conn.commit()
        return jsonify({"message": "Signup successful"}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "Email already registered"}), 409
    finally:
        cur.close()
        conn.close()

# --- Login Route ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, password FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, email, contact FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    users = []
    for row in rows:
        users.append({
            "name": row[0],
            "email": row[1],
            "contact": row[2]
        })
    return jsonify(users), 200

# --- API Endpoint for User Deletion ---
@app.route('/api/users/<string:email>', methods=['DELETE'])
def delete_user_by_email(email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE email = %s", (email,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"User {email} deleted"}), 200

# --- API ENDPOINT for User Update ---
@app.route('/api/users/<string:email>', methods=['PATCH'])
def update(email):
    data = request.get_json()
    fields = []
    values = []

    if 'name' in data and data['name']:
        fields.append("name = %s")
        values.append(data['name'])
    if 'contact' in data and data['contact']:
        fields.append("contact = %s")
        values.append(data['contact'])
    if 'dob' in data and data['dob']:
        fields.append("dob = %s")
        values.append(data['dob'])

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    values.append(email)
    query = f"UPDATE users SET {', '.join(fields)} WHERE email = %s"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(values))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"User {email} updated"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
