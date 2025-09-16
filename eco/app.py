from flask import request, Flask, jsonify
import sqlite3, os
from argon2 import PasswordHasher 
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)



# Allow multiple origins (e.g., localhost for development and production domain)
CORS(app, origins=[
    "http://localhost:3000",       # Local development (React, etc.)
    "https://eco-shield-green.web.app/"     # Hosted frontend domain
])
SCAM_FOLDER = "eco/scam/"
app.config["SCAM_FOLDER"] = SCAM_FOLDER

global login_id
global hashed
ph = PasswordHasher()

@app.route('/signup', methods=['POST'])#useke hisb se 
def singup():
    data = request.get_json()
    name = data['name']
    contact = data['contact']
    email = data['email']
    password = ph.hash(data['password'])
    dob = data['dob']
    
    eco = sqlite3.connect("eco.db")
    cursor = eco.cursor()
     
    cursor.execute("CREATE TABLE IF NOT EXISTS User(user_id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(15), contact VARCHAR(15), email VARCHAR(50), password VARCHAR(255), dob VARCHAR(20))")
    
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
    
    cursor.execute("SELECT password FROM User WHERE email = ?", email)
    row = cursor.fetchone()
    
    eco.commit()
    eco.close()
    
    if len(row) != 1:
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

@app.route('/Scam_Report',methods=['POST'])
def scam():
    data = request.get_json()
    file = request.files["image"]
    file_path = os.path.join(app.config["SCAM_FOLDER"], file.filename)#when u local host path is to be set then 
    file.save(file_path)
    title = data["title"]
    discription = data["detail"]
    
    eco = sqlite3.connect("eco.db")
    cursor = eco.cursor()
     
    cursor.execute("CREATE TABLE IF NOT EXISTS Scam_reports (report_id INTEGER PRIMARY KEY AUTOENCREMENT,  victim INTEGER, title TEXT, discription TEXT, image TEXT, FOREIGN KEY (user_id) RFREFENCES User(user_id)  ")
    
