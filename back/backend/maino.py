import json
import threading
from flask import Flask, request, jsonify, make_response, render_template, Response
import camera_dao
import back.category_dao as category_dao
import back.uom_dao as uom_dao
import back.product_dao as product_dao
from back.sql_connection import get_sql_connection
import orders_dao
import os
from flask import Blueprint, request, Response, jsonify
from back.sql_connection import get_sql_connection
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


#----------------------------------------------------------------------------------------------------

# های آماری برای محصولاتAPI 
# 1. تعداد کل محصولات
@app.route('/total_products', methods=['GET'])
def total_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 2. میانگین قیمت هر واحد
@app.route('/average_price', methods=['GET'])
def average_price():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(price_per_unit) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 3. بیشترین تخفیف داده شده
@app.route('/max_discount', methods=['GET'])
def max_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(discount_percentage) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 4. کمترین وزن
@app.route('/min_weight', methods=['GET'])
def min_weight():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(weight) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 5. مجموع سود
@app.route('/total_profit', methods=['GET'])
def total_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 6. تعداد محصولات منقضی شده
@app.route('/expired_products', methods=['GET'])
def expired_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE expiration_date < CURDATE()")
    result = cursor.fetchone()
    return jsonify(result)

# 7. تعداد محصولات در حال انقضاء (در یک ماه آینده)
@app.route('/expiring_products', methods=['GET'])
def expiring_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)")
    result = cursor.fetchone()
    return jsonify(result)

# 8. تعداد محصولات بدون تخفیف
@app.route('/no_discount_products', methods=['GET'])
def no_discount_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# 9. مجموع وزن محصولات
@app.route('/total_weight', methods=['GET'])
def total_weight():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(weight) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 10. بیشترین قیمت هر واحد
@app.route('/max_price', methods=['GET'])
def max_price():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(price_per_unit) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 11. کمترین قیمت هر واحد
@app.route('/min_price', methods=['GET'])
def min_price():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(price_per_unit) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 12. تعداد محصولات با قیمت بیش از 10000 تومان
@app.route('/price_above_10000', methods=['GET'])
def price_above_10000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_per_unit > 10000")
    result = cursor.fetchone()
    return jsonify(result)

# 13. تعداد محصولات با وزن کمتر از 500 گرم
@app.route('/weight_below_500', methods=['GET'])
def weight_below_500():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE weight < 500")
    result = cursor.fetchone()
    return jsonify(result)

# 14. میانگین درصد تخفیف
@app.route('/average_discount', methods=['GET'])
def average_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(discount_percentage) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 15. تعداد محصولات با سود بیش از 1000 تومان
@app.route('/profit_above_1000', methods=['GET'])
def profit_above_1000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE total_profit_on_sales > 1000")
    result = cursor.fetchone()
    return jsonify(result)

# 16. تعداد محصولات با تخفیف کمتر از 10 درصد
@app.route('/discount_below_10', methods=['GET'])
def discount_below_10():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE discount_percentage < 10")
    result = cursor.fetchone()
    return jsonify(result)

# 17. میانگین وزن محصولات
@app.route('/average_weight', methods=['GET'])
def average_weight():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(weight) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 18. بیشترین سود هر محصول
@app.route('/max_profit', methods=['GET'])
def max_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 19. کمترین سود هر محصول
@app.route('/min_profit', methods=['GET'])
def min_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 20. تعداد محصولات با سود منفی (ضرر)
@app.route('/negative_profit_products', methods=['GET'])
def negative_profit_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE total_profit_on_sales < 0")
    result = cursor.fetchone()
    return jsonify(result)

# 21. مجموع تخفیف‌ها
@app.route('/total_discounts', methods=['GET'])
def total_discounts():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(discount_percentage) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 22. تعداد محصولات با قیمت بین 5000 تا 10000 تومان
@app.route('/price_between_5000_10000', methods=['GET'])
def price_between_5000_10000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_per_unit BETWEEN 5000 AND 10000")
    result = cursor.fetchone()
    return jsonify(result)

# 23. میانگین سود هر محصول
@app.route('/average_profit', methods=['GET'])
def average_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 24. تعداد محصولات با وزن بین 500 تا 1000 گرم
@app.route('/weight_between_500_1000', methods=['GET'])
def weight_between_500_1000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE weight BETWEEN 500 AND 1000")
    result = cursor.fetchone()
    return jsonify(result)

# 25. بیشترین سود در فروش
@app.route('/max_sales_profit', methods=['GET'])
def max_sales_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 26. کمترین سود در فروش
@app.route('/min_sales_profit', methods=['GET'])
def min_sales_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 27. میانگین قیمت محصولات بدون تخفیف
@app.route('/average_price_no_discount', methods=['GET'])
def average_price_no_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(price_per_unit) FROM products WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# 28. تعداد محصولات با سود بالای 500 تومان
@app.route('/profit_above_500', methods=['GET'])
def profit_above_500():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE total_profit_on_sales > 500")
    result = cursor.fetchone()
    return jsonify(result)

# 29. میانگین سود هر واحد
@app.route('/average_profit_per_unit', methods=['GET'])
def average_profit_per_unit():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(total_profit_on_sales / weight) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 30. مجموع تعداد واحدهای فروخته شده
@app.route('/total_units_sold', methods=['GET'])
def total_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(units_sold) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 31. بیشترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/max_units_sold', methods=['GET'])
def max_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(units_sold) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 32. کمترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/min_units_sold', methods=['GET'])
def min_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(units_sold) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 33. میانگین تعداد واحدهای فروخته شده از یک محصول
@app.route('/average_units_sold', methods=['GET'])
def average_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(units_sold) FROM products")
    result = cursor.fetchone()
    return jsonify(result)

# 34. تعداد محصولات با قیمت بیش از میانگین قیمت
@app.route('/price_above_average', methods=['GET'])
def price_above_average():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE price_per_unit > (SELECT AVG(price_per_unit) FROM products)")
    result = cursor.fetchone()
    return jsonify(result)

# 35. تعداد محصولات با تخفیف بیش از میانگین تخفیف
@app.route('/discount_above_average', methods=['GET'])
def discount_above_average():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE discount_percentage > (SELECT AVG(discount_percentage) FROM products)")
    result = cursor.fetchone()
    return jsonify(result)

# 36. بیشترین تعداد واحدهای فروخته شده در یک ماه
@app.route('/max_units_sold_in_month', methods=['GET'])
def max_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(units_sold) FROM products WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 37. کمترین تعداد واحدهای فروخته شده در یک ماه
@app.route('/min_units_sold_in_month', methods=['GET'])
def min_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(units_sold) FROM products WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 38. مجموع تعداد واحدهای فروخته شده در یک ماه
@app.route('/total_units_sold_in_month', methods=['GET'])
def total_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(units_sold) FROM products WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 39. میانگین تعداد واحدهای فروخته شده در یک ماه
@app.route('/average_units_sold_in_month', methods=['GET'])
def average_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(units_sold) FROM products WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 40. تعداد محصولات با سود هر واحد بیش از میانگین سود هر واحد
@app.route('/profit_per_unit_above_average', methods=['GET'])
def profit_per_unit_above_average():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE (total_profit_on_sales / weight) > (SELECT AVG(total_profit_on_sales / weight) FROM products)")
    result = cursor.fetchone()
    return jsonify(result)

#------------------------------------------------------------------------------------------------------------------------------

# 


"""

# ditection camera 
@app.route('/video', methods=['GET']) 
def video(): 
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame') 

"""
'''
# not nesesery!!!!!!!!!!!!
# return detectiion lable 
@app.route('/detections', methods=['GET']) 
def detections(): 
    if detection_counts: 
        most_detected_label = max(detection_counts, key=detection_counts.get) 
        return jsonify({'most_detected': most_detected_label}) 
    else: 
        return jsonify({'most_detected':'No detections made'})'''


# returning all products in db
# Product APIs
@app.route('/getProducts', methods=['GET'])
@jwt_required()
def get_products():
    products = product_dao.get_all_products(connection)
    return jsonify(products)

# returning all entiteis of a specific product
# Product APIs
@app.route('/getProduct/<int:product_id>', methods=['GET'])
@jwt_required()
def get_one_product(product_id):
    product = product_dao.get_product(connection, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)












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
    app.run(port=5000,debug=True, threaded=True)





