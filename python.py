from flask import Flask, render_template, request, redirect
import face_recognition
import cv2
import os
import numpy as np
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Ensure faces folder exists
if not os.path.exists('faces'):
    os.makedirs('faces')

# Database setup
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    datetime TEXT
)''')
conn.commit()

# Home page - take attendance
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Save uploaded image
        file = request.files['image']
        path = f"temp.jpg"
        file.save(path)

        # Load uploaded image
        unknown_img = face_recognition.load_image_file(path)
        unknown_enc = face_recognition.face_encodings(unknown_img)
        if len(unknown_enc) == 0:
            return "No face found!"
        unknown_enc = unknown_enc[0]

        # Compare with saved faces
        for fname in os.listdir('faces'):
            known_img = face_recognition.load_image_file(f'faces/{fname}')
            known_enc = face_recognition.face_encodings(known_img)[0]
            results = face_recognition.compare_faces([known_enc], unknown_enc)
            if results[0]:
                # Mark attendance
                c.execute("INSERT INTO attendance(name, datetime) VALUES(?,?)", (fname.split('.')[0], datetime.now()))
                conn.commit()
                return f"Attendance marked for {fname.split('.')[0]}"
        return "Face not recognized!"
    return render_template('index.html')

# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['image']
        file.save(f"faces/{name}.jpg")
        return "User registered successfully!"
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
