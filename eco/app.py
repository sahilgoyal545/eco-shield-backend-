from flask import request, Flask, jsonify
import sqlite3
from argon2 import PasswordHasher 
app = Flask(__name__)

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
     
    cursor.execute("CREATE TABLE IF NOT EXISTS User(user_id INT PRIMARY KEY AUTOINCREMENT, name VARCHAR(15), contact VARCHAR(15), email VARCHAR(50), password VARCHAR(255), dob VARCHAR(20))")
    
    cursor.execute("INSERT INTO User(name, contact, email, password, dob) VALUES (?, ?, ?, ?, ?)",(name, contact, email, password, dob)) 
    
    eco.commit() #eco close karni ha 
    eco.close()

    return jsonify({"message": "Signup successful"}), 201

    
@app.route('/login',methods=['POST'])#useke hisb se 
def login():
    data = request.get_json()
    email = data['email']
    password = ph.hash(data['password'])
    
    eco = sqlite3.connect("eco.db")
    cursor = eco.cursor() 
    
    row = cursor.execute("SELECT password FROM User WHERE email = ?", email)
    if len(row) != 1 or :
        return jsonify({"message": " Email not found"}), 404
    elif row == password 
