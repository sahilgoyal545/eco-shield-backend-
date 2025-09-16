from flask import request, Flask, jsonify
import sqlite3, os
from argon2 import PasswordHasher 
from flask_cors import CORS

app = Flask(__name__)

# Allow multiple origins (e.g., localhost for development and production domain)
CORS(app, origins=[
    "http://localhost:3000",       # Local development (React, etc.)
    "https://eco-shield-green.web.app/"     # Hosted frontend domain
])

global login_id
global hashed
ph = PasswordHasher()

@app.route('/Contact', methods=['POST'])#useke hisb se 
def singup():
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    email = data['email']
    password = ph.hash(data['password'])
    dob = data['dob']

    
    eco = sqlite3.connect("eco.db")
    cursor = eco.cursor()
    
    if cursor.execute("SELECT 1 FROM User WHERE email = ?", (email,)).fetchall() and cursor.execute("SELECT 1 FROM User WHERE contact = ?" , (contact)).fetchall():
        eco.commit() 
        eco.close() 
        return jsonify("email exist try another email"),409
 
    cursor.execute("""CREATE TABLE IF NOT EXISTS 
                   User(user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   name VARCHAR(15), 
                   contact VARCHAR(15),
                   email VARCHAR(50), password VARCHAR(255),
                   dob VARCHAR(20), is_active BOOLEAN DEFAULT 1)
                   created_at timestamp default current_timestamp""")
    
    cursor.execute("INSERT INTO User(name, contact, email, password, dob) VALUES (?, ?, ?, ?, ?)",(name, contact, email, password, dob)) 
    
    eco.commit() 
    eco.close()

    return jsonify({"message": "Signup successful"}), 201

    
@app.route('/login',methods=['POST'])#useke hisb se 
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    eco = sqlite3.connect("eco.db")
    cursor = eco.cursor() 
    
    cursor.execute("SELECT password FROM User WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    eco.commit()
    eco.close()
    
    if not row:
        return jsonify({"message": "Email not found"}), 404
    elif ph.verify(row[0], password):
        eco = sqlite3.connect("eco.db")
        cursor = eco.cursor()
        login_id = cursor.execute("SELECT user_id FROM User WHERE email = ?", email)
        eco.commit()
        eco.close()
        return jsonify({"massage": "Login succesfully!"}), 200
    else:
        return jsonify({"message": "Password incorrect"}), 404