import os
from flask import Flask, jsonify, request

from sql_connection import get_sql_connection



app = Flask(__name__)


connection = get_sql_connection()

# ---------------------------------------------------------------------------------------------
# product data access 
#----------------------------------------------------------------------------------------------









#T
# this function remove product from the universe (even in order_detale table like never exist)
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



#T
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



#T
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



#T
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