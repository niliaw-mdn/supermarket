import json
import threading
from flask import Flask, request, jsonify, make_response, render_template, Response
import camera_dao
from back.db_connection import get_sql_connection
import orders_dao
import os
from flask import Blueprint, request, Response, jsonify
from back.db_connection import get_sql_connection
from camera_dao import generate_frames, detection_counts

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import uuid

# Import database methods from db_methods.py
from user_dao import fetch_user_by_email, create_user, delete_user_by_id, fetch_all_users, fetch_user_by_id


UPLOAD_FOLDER='./productimages'




app = Flask(__name__)


connection = get_sql_connection()



# Configure JWT Secret Key and Token Expiry Times
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=3)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
jwt = JWTManager(app)

# In-memory storage for revoked tokens
revoked_tokens = set()

# Callback: Check if a Token is Revoked or Expired
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    token_id = jwt_payload['jti']
    return token_id in revoked_tokens

# Callback: Handle Expired Tokens
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    token_id = jwt_payload['jti']
    revoked_tokens.add(token_id)
    return jsonify({'message': 'Token has expired. Please log in again.'}), 401

# Middleware: Check JWT Token for All Requests
@app.before_request
def check_request_token():
    # Allow these routes without requiring a token
    unprotected_routes = ['login', 'register', 'refresh']
    if request.endpoint in unprotected_routes or request.endpoint is None:
        return None

    try:
        get_jwt_identity()  # Validate JWT token
    except Exception as e:
        return jsonify({'message': 'Unauthorized. Invalid or expired token.', 'error': str(e)}), 401




# Route: Register New User
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if fetch_user_by_email(email):
        return jsonify({'message': 'Email already exists'}), 409

    password_salt = str(uuid.uuid4())
    password_hash = generate_password_hash(password + password_salt)
    create_user(email, password_hash, password_salt)

    return jsonify({'message': 'User registered successfully'}), 201

# Route: Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = fetch_user_by_email(email)
    if not user:
        return jsonify({'message': 'Invalid email or password'}), 401

    password_hash = user['password_hash']
    password_salt = user['password_salt']

    if not check_password_hash(password_hash, password + password_salt):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user['user_id'], additional_claims={"type":"User"})
    refresh_token = create_refresh_token(identity=user['user_id'])
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200



# Route: Refresh Access Token
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': new_access_token}), 200

# Route: Logout (Access Token)
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    user_type = get_jwt()['user_type']
    if user_type != "User":
        raise
    revoked_tokens.add(jti)
    return jsonify({'message': 'Access token successfully revoked'}), 200

# Route: Logout (Refresh Token)
@app.route('/logout-refresh', methods=['POST'])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({'message': 'Refresh token successfully revoked'}), 200

# Route: Delete User
@app.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    delete_user_by_id(user_id)
    return jsonify({'message': 'Account deleted successfully'}), 200

# Route: Get User Information
@app.route('/get-user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = fetch_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'user_id': user['user_id'], 'email': user['email']}), 200

# Route: Get All Users
@app.route('/get-all-users', methods=['GET'])
@jwt_required()
def get_all_users():
    user_id = get_jwt_identity()
    if user_id != 1:  # Only admin (user_id = 1) is authorized
        return jsonify({'message': 'You are not authorized to access this endpoint'}), 403

    users = fetch_all_users()
    return jsonify(users), 200





if __name__ == "__main__":
    app.run(port=5000,debug=True, threaded=True)





