# use flask to write a backend server to handle the request from the frontend
import firebase_admin.storage
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import sys
import requests
import time
import random
import threading
import logging
import datetime
import re
import hashlib
import base64
import hmac
import urllib.parse
import urllib.request
import urllib.error
import firebase_admin
from firebase_admin import credentials, storage, firestore, initialize_app, auth
import pyrebase
from cryptography.fernet import Fernet
from keywordCount import get_keywords
from fileSecure import decrypt_to_string

app = Flask(__name__)
CORS(app)

jsonStr = decrypt_to_string('serviceAccount.json.secure')
jsonObj = json.loads(jsonStr)
cred = credentials.Certificate(jsonObj)
firebase_admin.initialize_app(cred)

db = firestore.client()
storage = storage.bucket("wos-data-analysis-tool.appspot.com")

# firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyDU9yTCklZ9Jj6V6UqHwp0h2CiDiK5_Ygo",
    "authDomain": "wos-data-analysis-tool.firebaseapp.com",
    "databaseURL": "https://wos-data-analysis-tool.firebaseio.com",
    "projectId": "wos-data-analysis-tool",
    "storageBucket": "wos-data-analysis-tool.appspot.com",
    "messagingSenderId": "486046308590",
    "appId": "1:486046308590:web:9d7f0b810cf0d3a49b3bff",
    "measurementId": "G-XQ94Y9Z8ZE"
}

# initialize firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

FernetKey = Fernet.generate_key()
cipher_suite = Fernet(FernetKey)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode('utf-8')).decode('utf-8')

def decrypt_password(password):
    return cipher_suite.decrypt(password.encode('utf-8')).decode('utf-8')

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/upload')
def index():
    return send_file('webpage/upload.html')

@app.route('/register')
def registerPage():
    return send_file('webpage/register.html')

@app.route('/login')
def loginPage():
    return send_file('webpage/login.html')

@app.route('/keyword')
def keywordPage():
    return send_file('webpage/keywordCount.html')

@app.route('/registerAPI', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        user = auth.create_user_with_email_and_password(email, password)
        doc_ref = db.collection('users').document(email)
        doc_ref.set({
            'files': []
        })
        auth.send_email_verification(user['idToken'])
        return jsonify({"message": "Register successful"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@app.route('/loginAPI', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        encrypted = encrypt_password(password)
        user_id_token = user['idToken']
        account_info = auth.get_account_info(user_id_token)
        users = account_info['users']
        if users and len(users) > 0:
            user_info = users[0]
            email_verified = user_info['emailVerified']
            if not email_verified:
                return jsonify({"message": "Email not verified"}), 403
        else:
            return jsonify({"message": "No user found"}), 404
        return jsonify({
                    "message": "Login successful",
                    "email": email,
                    "password": encrypted,
                }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
@app.route('/forgotPasswordAPI', methods=['POST'])
def forgotPassword():
    data = request.get_json()
    email = data.get('email')
    try:
        auth.send_password_reset_email(email)
        return jsonify({"message": "Email sent"}), 200
    except:
        return jsonify({"message": "Email not sent"}), 400

# get the *.txt file from the frontend
@app.route('/uploadAPI', methods=['POST'])
def upload():
    # get the file
    try:
        files = request.files.getlist('file')
        fileSet = request.form.get('fileSet')
        email = request.form.get('email')
        password = request.form.get('password')
        password = decrypt_password(password)
        user = auth.sign_in_with_email_and_password(email, password)
        userId = user['localId']
        userEmail = user['email']
        # save the file to firebase storage
        results = []
        doc_ref = db.collection('users').document(userEmail)
        doc = doc_ref.get().to_dict()
        arr = doc.get(fileSet)
        if not arr:
            n = 0
        else:
            n = len(arr)
        for file in files:
            if file.filename.endswith('.txt'):
                saved_filename = userId + "." + fileSet + "." + str(n) + ".txt"
                n += 1
                # fileSize = len(file.read())
                # file.seek(0)
                # storedFiles = storage.list_blobs(prefix=f'{userId}.{fileSet}')
                # exist = False
                # for f in storedFiles:
                #     if f.size == fileSize:
                #         exist = True
                #         break
                # if exist:
                #     continue
                blob = storage.blob(saved_filename)
                blob.upload_from_file(file)
                blob.make_public()
                file_url = blob.public_url
                results.append({
                    'url': file_url
                })
        if results:
            doc_ref.update({
                f'{fileSet}': firestore.ArrayUnion(results)
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
@app.route('/keywordCountAPI', methods=['POST'])
def keywordCount():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        password = decrypt_password(password)
        user = auth.sign_in_with_email_and_password(email, password)
        userId = user['localId']
        userEmail = user['email']
        fileSet = data.get('fileSet')
        doc_ref = db.collection('users').document(userEmail)
        doc = doc_ref.get().to_dict()
        if doc:
            files = doc.get(fileSet)
            if files:
                sorted_keywords = get_keywords(files)
                return jsonify(sorted_keywords), 200
        return jsonify({"message": "No files found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    

if __name__ == '__main__':
    app.run(port=5000)