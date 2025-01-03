import json
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import uom_dao
import product_dao
from sql_connection import get_sql_connection
import orders_dao
import os
from flask import Blueprint, request, Response, jsonify
from user_dao import validate_user_input, generate_salt, generate_hash, db_write, validate_user
from sql_connection import get_sql_connection

from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from settings import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

UPLOAD_FOLDER='./productimages'




app = Flask(__name__)

app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

connection = get_sql_connection()

# tested
@app.route("/register", methods=["POST"])
def register_user():
    user_email = request.json["email"]
    user_password = request.json["password"]
    user_confirm_password = request.json["confirm_password"]

    if user_password == user_confirm_password and validate_user_input(email=user_email, password=user_password):
        password_salt = generate_salt()
        password_hash = generate_hash(user_password, password_salt)

        if db_write(connection ,
            """INSERT INTO grocery_store.user (email, password_salt, password_hash) VALUES (%s, %s, %s)""",
            (user_email, password_salt, password_hash),
        ):
            # Registration Successful
            return Response(status=201)
        else:
            # Registration Failed
            return Response(status=409)
    else:
        # Registration Failed
        return Response(status=400)

# have a bug in here
@app.route("/login", methods=["POST"])
def login_user():
    try:
        user_email = request.json["email"]
        user_password = request.json["password"]

        user_token = validate_user(connection, user_email, user_password)

        if user_token:
            return jsonify({"jwt_token": user_token})
        else:
            return Response(status=401)
    except Exception as e:
        print(f"Error in login_user: {e}")  # Log the error for debugging purposes
        return Response(status=500)






# tested
# returning all products in db
@app.route('/getProducts', methods=['GET'])
def get_products():
    products = product_dao.get_all_products(connection)
    response = jsonify(products)
    return response

# tested
# returning all entiteis of a specific product
@app.route('/getProduct/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    try:
        product = product_dao.get_product(connection, product_id)

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        response = jsonify(product)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500



# tested
# delete one specific product
@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    return_id = product_dao.delete_product(connection, request.json.get('product_id'))
    response = jsonify({
        'product_id': return_id

    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# tested
# return all unites of mesurment
@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = uom_dao.get_uoms(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# tested
# Inserting  new product to db
@app.route('/insertProduct', methods=['POST'])
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
    print('ssdds')
    return {"null":1}
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
def update_product_route(product_id):
    try:
        request_payload = request.json
        if not request_payload:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        product_dao.update_product(connection, product_id, request_payload)
        return jsonify({'message': 'Product updated successfully'})
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500




@app.route('/insertOrder', methods=['POST'])
def insert_order():
    request_payload = json.loads(request.form['date'])
    order_id = orders_dao.insert_order(connection, request_payload)
    response = jsonify({
        'order_id': order_id
    })


@app.route('/getAllOrders', methods=['GET'])
def get_all_orders():
    response = orders_dao.get_all_orders(connection)
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":

    app.run(port=5000,debug=True)
