import os
from flask import Flask, jsonify, request
import mysql.connector

from sql_connection import get_sql_connection



app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = get_sql_connection()

# ---------------------------------------------------------------------------------------------
# product data access 
#----------------------------------------------------------------------------------------------


# T
# update all attribute of a product except id
@app.route('/updateProduct/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        # Check if a new image is uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
        else:
            file_path = request.form.get('image_address')  # Use existing image path

        # Extract product details
        product_data = {
            'name': request.form.get('name'),
            'uom_id': request.form.get('uom_id'),
            'price_per_unit': request.form.get('price_per_unit'),
            'available_quantity': request.form.get('available_quantity'),
            'manufacturer_name': request.form.get('manufacturer_name'),
            'weight': request.form.get('weight'),
            'purchase_price': request.form.get('purchase_price'),
            'discount_percentage': request.form.get('discount_percentage'),
            'voluminosity': request.form.get('voluminosity'),
            'combinations': request.form.get('combinations'),
            'nutritional_information': request.form.get('nutritional_information'),
            'expiration_date': request.form.get('expiration_date'),
            'storage_conditions': request.form.get('storage_conditions'),
            'number_sold': request.form.get('number_sold'),
            'date_added_to_stock': request.form.get('date_added_to_stock'),
            'total_profit_on_sales': request.form.get('total_profit_on_sales'),
            'error_rate_in_weight': request.form.get('error_rate_in_weight'),
            'category_id': request.form.get('category_id'),
            'image_address': file_path
        }

        cursor = connection.cursor()

        sql = """UPDATE product SET 
                    name = %s, uom_id = %s, price_per_unit = %s, available_quantity = %s,
                    manufacturer_name = %s, weight = %s, purchase_price = %s, discount_percentage = %s,
                    voluminosity = %s, combinations = %s, nutritional_information = %s, expiration_date = %s,
                    storage_conditions = %s, number_sold = %s, date_added_to_stock = %s, total_profit_on_sales = %s,
                    error_rate_in_weight = %s, image_address = %s, category_id = %s
                WHERE product_id = %s"""
        
        values = (
            product_data['name'], product_data['uom_id'], product_data['price_per_unit'],
            product_data['available_quantity'], product_data['manufacturer_name'], product_data['weight'],
            product_data['purchase_price'], product_data['discount_percentage'], product_data['voluminosity'],
            product_data['combinations'], product_data['nutritional_information'], product_data['expiration_date'],
            product_data['storage_conditions'], product_data['number_sold'], product_data['date_added_to_stock'],
            product_data['total_profit_on_sales'], product_data['error_rate_in_weight'], product_data['image_address'],
            product_data['category_id'], product_id
        )

        cursor.execute(sql, values)
        connection.commit()

        return jsonify({'message': 'Product updated successfully'})

    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# T
# inserting all attribute of a product 
@app.route('/insertProduct', methods=['POST'])
def insert_product():
    try:
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Extract product details from request
        product = {
            'name': request.form.get('name'),
            'uom_id': request.form.get('uom_id'),
            'price_per_unit': request.form.get('price_per_unit'),
            'available_quantity': request.form.get('available_quantity'),
            'manufacturer_name': request.form.get('manufacturer_name'),
            'weight': request.form.get('weight'),
            'purchase_price': request.form.get('purchase_price'),
            'discount_percentage': request.form.get('discount_percentage'),
            'voluminosity': request.form.get('voluminosity'),
            'combinations': request.form.get('combinations'),
            'nutritional_information': request.form.get('nutritional_information'),
            'expiration_date': request.form.get('expiration_date'),
            'storage_conditions': request.form.get('storage_conditions'),
            'number_sold': request.form.get('number_sold'),
            'date_added_to_stock': request.form.get('date_added_to_stock'),
            'total_profit_on_sales': request.form.get('total_profit_on_sales'),
            'error_rate_in_weight': request.form.get('error_rate_in_weight'),
            'category_id': request.form.get('category_id'),
            'image_address': file_path
        }

        cursor = connection.cursor()

        query = ("""INSERT INTO product (name, uom_id, price_per_unit, available_quantity,
                    manufacturer_name, weight, purchase_price, discount_percentage, voluminosity,
                    combinations, nutritional_information, expiration_date, storage_conditions,
                    number_sold, date_added_to_stock, total_profit_on_sales, error_rate_in_weight, 
                    image_address, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")

        data = (
            product['name'], product['uom_id'], product['price_per_unit'], product['available_quantity'],
            product['manufacturer_name'], product['weight'], product['purchase_price'],
            product['discount_percentage'], product['voluminosity'], product['combinations'],
            product['nutritional_information'], product['expiration_date'], product['storage_conditions'], 
            product['number_sold'], product['date_added_to_stock'], product['total_profit_on_sales'], 
            product['error_rate_in_weight'], product['image_address'], product['category_id']
        )

        cursor.execute(query, data)
        connection.commit()
        product_id = cursor.lastrowid

        cursor.close()

        return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500




# T
# worning !!! this function remove product from the universe (even in order_detale table like never exist)
@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    cursor = connection.cursor()

    try:
        # First, delete related records in order_details
        delete_order_details_query = "DELETE FROM order_details WHERE product_id = %s"
        cursor.execute(delete_order_details_query, (product_id,))

        # Now, delete the product itself
        delete_product_query = "DELETE FROM product WHERE product_id = %s"
        cursor.execute(delete_product_query, (product_id,))

        connection.commit()
        return jsonify({'message': 'Product deleted successfully', 'product_id': product_id}), 200

    except connection.Error as err:
        connection.rollback()  # Rollback if any error occurs
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()



# T
# delete one specific product(just delete those product that dont have any sall)
@app.route('/deleteUnsallProduct', methods=['POST'])
def delete_Unsall_product():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    cursor = connection.cursor()

    # Delete from product table
    delete_product_query = "DELETE FROM product WHERE product_id = %s"
    cursor.execute(delete_product_query, (product_id,))

    connection.commit()
    cursor.close()

    return jsonify({'product_id': product_id}), 200



# T
# return all unites of mesurment
@app.route('/getUOM', methods=['GET'])
def get_uom():
    cursor = connection.cursor()
    query = ("SELECT * from uom")
    cursor.execute(query)
    
    response = []
    for (uom_id, uom_name) in cursor:
        response.append({
            'uom_id': uom_id,
            'uom_name': uom_name
        })
    return jsonify(response)



# T
# return all category
@app.route('/getcategory', methods=['GET'])
def get_category():
    cursor = connection.cursor()
    query = ("SELECT * from category")
    cursor.execute(query)
    
    response = []
    for (category_id, category_name) in cursor:
        response.append({
            'category_id': category_id,
            'category_name': category_name
        })
    return jsonify(response)




if __name__ == "__main__":
    app.run(port=5000,debug=True)