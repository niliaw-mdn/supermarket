import json
from flask import Flask, request, jsonify
import uom_dao
import product_dao
from sql_connection import get_sql_connection
import orders_dao

app = Flask(__name__)

connection = get_sql_connection()

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
    try:
        print("Request received")
        request_payload = request.get_json()
        print(f"Request payload: {request_payload}")

        # Check if request payload is received correctly
        if not request_payload:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Assuming product_dao.insert_new_product function and connection are defined elsewhere
        product_id = product_dao.insert_new_product(connection, request_payload)
        return jsonify({'product_id': product_id})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500



#tested
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
    print("starting python flask")
    app.run(port=5000)
