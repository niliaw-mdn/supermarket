import json
import threading
from flask import Flask, request, jsonify, make_response, render_template, Response
import camera_dao
import category_dao
import uom_dao
import product_dao
from sql_connection import get_sql_connection
import orders_dao
import os
from flask import Blueprint, request, Response, jsonify
from sql_connection import get_sql_connection
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

    access_token = create_access_token(identity=user['user_id'])
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


# tested
# ditection camera 
@app.route('/video', methods=['GET']) 
def video(): 
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') 


# tested
# not nesesery!!!!!!!!!!!!
# return detectiion lable 
@app.route('/detections', methods=['GET']) 
def detections(): 
    if detection_counts: 
        most_detected_label = max(detection_counts, key=detection_counts.get) 
        return jsonify({'most_detected': most_detected_label}) 
    else: 
        return jsonify({'most_detected':'No detections made'})


# tested
# returning all products in db
# Product APIs
@app.route('/getProducts', methods=['GET'])
@jwt_required()
def get_products():
    products = product_dao.get_all_products(connection)
    return jsonify(products)

# tested
# returning all entiteis of a specific product
# Product APIs
@app.route('/getProduct/<int:product_id>', methods=['GET'])
@jwt_required()
def get_one_product(product_id):
    product = product_dao.get_product(connection, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)



# tested
# delete one specific product
@app.route('/deleteProduct', methods=['POST'])
@jwt_required()
def delete_product():
    return_id = product_dao.delete_product(connection, request.json.get('product_id'))
    return jsonify({'product_id': return_id})

# tested
# return all unites of mesurment
@app.route('/getUOM', methods=['GET'])
@jwt_required()
def get_uom():
    response = uom_dao.get_uoms(connection)
    response = jsonify(response)
    return response


# tested
# return all category
@app.route('/getcategory', methods=['GET'])
@jwt_required()
def get_uom():
    response = category_dao.get_category(connection)
    response = jsonify(response)
    return response


# tested
# Inserting  new product to db
@app.route('/insertProduct', methods=['POST'])
@jwt_required()
def insert_product():
    """productname = request.form.get('name')
    productdescription = request.form.get('description')
    productprice = request.form.get('price')
    productquantity = request.form.get('quantity')"""
    
    file = request.files['file']
    imageaddress = app.config['UPLOAD_FOLDER'] + file.name
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
    
    file.save(file_path)
    product={}
    product['name']=request.form.get('name')
    product['uom_id']=request.form.get('uom_id')
    product['price_per_unit']=request.form.get('price_per_unit')
    product['available_quantity']=request.form.get('available_quantity')
    product['manufacturer_name']=request.form.get('manufacturer_name')
    product['weight']=request.form.get('weight')
    product['purchase_price']=request.form.get('purchase_price')
    product['discount_percentage']=request.form.get('discount_percentage')
    product['voluminosity']=request.form.get('voluminosity')
    product['combinations']=request.form.get('combinations')
    product['nutritional_information']=request.form.get('nutritional_information')
    product['expiration_date']=request.form.get('expiration_date')
    product['storage_conditions']=request.form.get('storage_conditions')
    product['number_sold']=request.form.get('number_sold')
    product['date_added_to_stock']=request.form.get('date_added_to_stock')
    product['total_profit_on_sales']=request.form.get('total_profit_on_sales')
    product['error_rate_in_weight']=request.form.get('error_rate_in_weight')
    product['image_address'] = file_path
    product_dao.insert_new_product(connection, product=product)
    return jsonify({'message': 'Product added successfully'})
    # try:
    #     print("Request received")
    #     request_payload = request.get_json()
    #     print(f"Request payload: {request_payload}")

    #     # Check if request payload is received correctly
    #     if not request_payload:
    #         return jsonify({"error": "Invalid JSON payload"}), 400

    #     # Assuming product_dao.insert_new_product function and connection are defined elsewhere
    #     product_id = product_dao.insert_new_product(connection, request_payload)
    #     return jsonify({'product_id': product_id})
    # except Exception as e:
    #     # Log the exception for debugging
    #     print(f"Error occurred: {e}")
    #     return jsonify({"error": str(e)}), 500



#image update missing
# updating a single product in db
@app.route('/updateProduct/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product_route(product_id):
    request_payload = request.json
    if not request_payload:
        return jsonify({"error": "Invalid JSON payload"}), 400
    product_dao.update_product(connection, product_id, request_payload)
    return jsonify({'message': 'Product updated successfully'})




# Orders APIs
@app.route('/insertOrder', methods=['POST'])
@jwt_required()
def insert_order():
    request_payload = json.loads(request.form['date'])
    order_id = orders_dao.insert_order(connection, request_payload)
    return jsonify({'order_id': order_id})
    


@app.route('/getAllOrders', methods=['GET'])
@jwt_required()
def get_all_orders():
    response = orders_dao.get_all_orders(connection)
    return jsonify(response)


if __name__ == "__main__":
    threading.Thread(target=generate_frames).start()
    app.run(port=5000,debug=True, threaded=True)





