from flask import Flask, render_template, redirect, request, url_for, send_file, jsonify, session, Response
import mysql.connector
import os
import cv2
import speech_recognition as sr
import math
import numpy as np
import uuid
import re
from cvzone.HandTrackingModule import HandDetector
from keras.models import load_model
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.preprocessing import image
from cvzone.ClassificationModule import Classifier
import subprocess
import torch
from ultralytics import YOLO
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from pynput import keyboard

# Create a single Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "waxsdrctfvybguhnijmok"

# Ensure upload folder exists
UPLOAD_FOLDER = "static/uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MySQL Database Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='gesture'
)
mycursor = mydb.cursor()

def executionquery(query, values):
    mycursor.execute(query, values)
    mydb.commit()

def retrivequery1(query, values):
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

# Password validation function
def is_valid_password(password):
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special character
    password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_regex, password) is not None

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/home')
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.pop("user", None)  # Use None as default to avoid KeyError
    return redirect('/')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        c_password = request.form.get('c_password', '').strip()

        # Check for empty fields
        if not name or not email or not password or not c_password:
            return render_template('register.html', message="All fields are required!")

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return render_template('register.html', message="Invalid email format!")

        # Validate password
        if not is_valid_password(password):
            return render_template('register.html', message="Password must be at least 8 characters long, with 1 uppercase, 1 lowercase, 1 digit, and 1 special character!")

        # Check if passwords match
        if password != c_password:
            return render_template('register.html', message="Confirm password does not match!")

        # Check if email already exists
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = [i[0] for i in email_data]
        if email.upper() in email_data_list:
            return render_template('register.html', message="This email ID already exists!")

        # Insert user into database
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        values = (name, email, password)
        executionquery(query, values)
        return render_template('login.html', message="Successfully Registered!")

    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect('/home')

    if request.method == "POST":
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Check for empty fields
        if not email or not password:
            return render_template('login.html', message="Both email and password are required!")

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return render_template('login.html', message="Invalid email format!")

        # Check if email exists
        query = "SELECT email, password, name FROM users WHERE UPPER(email) = UPPER(%s)"
        values = (email,)
        user_data = retrivequery1(query, values)
        if not user_data:
            return render_template('login.html', message="This email ID does not exist!")

        # Verify password (case-sensitive)
        stored_email, stored_password, stored_name = user_data[0]
        if password != stored_password:
            return render_template('login.html', message="Invalid password!")

        # Set session
        session['user'] = {'email': stored_email, 'name': stored_name}
        return redirect("/")

    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('home.html')

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'user' not in session:
        return redirect('/login')
    return render_template('prediction.html')

@app.route('/graph')
def graph():
    if 'user' not in session:
        return redirect('/login')
    return render_template('graph.html')

@app.route("/mic", methods=["GET", "POST"])
def mic():
    if 'user' not in session:
        if request.method == "POST":
            return jsonify({"error": "Please login first"}, 401)
        return redirect('/login')
    
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}, 400)
        
        file = request.files["file"]
        if not file or file.filename == "":
            return jsonify({"error": "No file selected"}, 400)
        
        try:
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(file_path) as source:
                audio = recognizer.record(source)
            transcript = recognizer.recognize_google(audio)
            
            query = "INSERT INTO recordings (user_email, filename, transcript) VALUES (%s, %s, %s)"
            values = (session['user']['email'], unique_filename, transcript)
            executionquery(query, values)
            
            return jsonify({
                "transcript": transcript,
                "filename": unique_filename
            })
        except sr.UnknownValueError:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Could not understand audio"}, 400)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": str(e)}, 500)
    
    return render_template("mic.html", transcript1="")

@app.route("/my_recordings", methods=["GET"])
def my_recordings():
    if 'user' not in session:
        return redirect('/login')
    
    query = "SELECT filename, transcript, created_at FROM recordings WHERE user_email = %s ORDER BY created_at DESC"
    values = (session['user']['email'],)
    recordings = retrivequery1(query, values)
    
    recordings_list = [
        {
            "filename": rec[0],
            "transcript": rec[1],
            "date": rec[2].strftime("%Y-%m-%d %H:%M:%S"),
            "url": url_for('static', filename=f'uploads/{rec[0]}')
        } for rec in recordings
    ]
    
    return render_template("recordings.html", recordings=recordings_list)

@app.route("/download_recording/<filename>")
def download_recording(filename):
    if 'user' not in session:
        return redirect('/login')
    
    query = "SELECT user_email FROM recordings WHERE filename = %s"
    values = (filename,)
    result = retrivequery1(query, values)
    
    if not result or result[0][0] != session['user']['email']:
        return "Unauthorized", 403
    
    return send_file(
        os.path.join(UPLOAD_FOLDER, filename),
        as_attachment=True,
        download_name=filename
    )

@app.route("/delete_recording/<filename>", methods=["POST"])
def delete_recording(filename):
    if 'user' not in session:
        return redirect('/login')
    
    query = "SELECT user_email, filename FROM recordings WHERE filename = %s"
    values = (filename,)
    result = retrivequery1(query, values)
    
    if not result or result[0][0] != session['user']['email']:
        return "Unauthorized", 403
    
    file_path = os.path.join(UPLOAD_FOLDER, result[0][1])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    query = "DELETE FROM recordings WHERE filename = %s"
    executionquery(query, (filename,))
    
    return redirect(url_for('my_recordings'))

@app.route('/open_webcam', methods=['POST', 'GET'])
def open_webcam():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        subprocess.Popen(['python', 'live.py'])
    return render_template('prediction.html')

if __name__ == '__main__':
    app.run(debug=True)