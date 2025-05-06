import cv2
from flask import Flask, jsonify, request, send_from_directory, render_template_string
import mysql.connector
from flask_cors import CORS
from functools import wraps
import os
from db_connection import get_db_connection, close_connection
import subprocess
import time

import subprocess
import json
import sys

import threading

from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
NEW_PRODUCT_IMG = os.path.join(BASE_DIR, 'new_product_img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(NEW_PRODUCT_IMG, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NEW_PRODUCT_IMG'] = NEW_PRODUCT_IMG

app.config['CUSTOMER_IMAGE'] = '\back\customer_image'

#  پوشه ذخیره تصاویر محصولات برای ترین
output_dir = 'new_product_img'
os.makedirs(output_dir, exist_ok=True)


streamlit_proc = None
timer = None

# Route for serving images from the 'uploads' folder
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# Custom error handler for database errors
@app.errorhandler(mysql.connector.Error)
def handle_db_error(error):
    """Handle database errors and return appropriate JSON response."""
    return jsonify({
        "error": str(error),
        "code": error.errno if hasattr(error, 'errno') else 500
    }), 500

# Corrected decorator for database operations
def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            result = func(connection, cursor, *args, **kwargs)
            connection.commit()
            return result
        except mysql.connector.Error as err:
            if connection.is_connected():
                connection.rollback()
            raise err
        finally:
            if cursor:
                cursor.close()
            if connection:
                close_connection(connection)
    return wrapper


# ---------------------------------------------------------------------------------------------
# product data access 
#----------------------------------------------------------------------------------------------



@app.route('/capture', methods=['GET'])
def capture_images():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return jsonify({"error": "Unable to access camera!"})

    image_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Webcam', frame)
        key = cv2.waitKey(1) & 0xFF

        # Press 's' to save an image
        if key == ord('s'):
            img_name = os.path.join(NEW_PRODUCT_IMG, f"image_{image_counter}.png")
            cv2.imwrite(img_name, frame)
            print(f"Image saved: {img_name}")
            image_counter += 1

        # Press 'Esc' to exit
        elif key == 27:
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return jsonify({"message": "Capture session ended", "total_images": image_counter})






#----------------------------------------------------------------------------------------------------
# های آماری برای محصولاتAPI 
# T $
# 1. تعداد کل محصولات
@app.route('/total_products', methods=['GET'])
@with_db_connection
def total_products(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product")
    result = cursor.fetchone()
    return jsonify({"total_products": result[0]})

# T
# 2. میانگین قیمت هر واحد
@app.route('/average_price', methods=['GET'])
@with_db_connection
def average_price(connection, cursor):
    cursor.execute("SELECT AVG(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify({"average_price": result[0]}) 

# T
# 3. بیشترین تخفیف داده شده
@app.route('/max_discount', methods=['GET'])
@with_db_connection
def max_discount(connection, cursor):
    cursor.execute("SELECT MAX(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 4. کمترین وزن
@app.route('/min_weight', methods=['GET'])
@with_db_connection
def min_weight(connection, cursor):
    cursor.execute("SELECT MIN(weight) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 5. مجموع سود
@app.route('/total_profit', methods=['GET'])
@with_db_connection
def total_profit(connection, cursor):
    cursor.execute("SELECT SUM(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 6. تعداد محصولات منقضی شده
@app.route('/expired_productspn', methods=['GET'])
@with_db_connection
def expired_productspn(connection, cursor):
    # دریافت پارامترهای صفحه‌بندی
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    
    try:
        # شمارش تعداد کل محصولات منقضی شده
        count_query = "SELECT COUNT(*) FROM product WHERE expiration_date < CURDATE()"
        cursor.execute(count_query)
        total_products = cursor.fetchone()[0]
        total_pages = (total_products + limit - 1) // limit

        # دریافت لیست محصولات منقضی شده
        select_query = """
            SELECT product_id, name, price_per_unit, available_quantity, image_address, 
                   expiration_date, category_id
            FROM product
            WHERE expiration_date < CURDATE()
            ORDER BY expiration_date ASC
            LIMIT %s OFFSET %s
        """
        offset = (page - 1) * limit
        cursor.execute(select_query, (limit, offset))

        products = []
        for row in cursor.fetchall():
            products.append({
                "product_id": row[0],
                "name": row[1],
                "price_per_unit": row[2],
                "available_quantity": row[3],
                "image_address": row[4],
                "expiration_date": row[5].isoformat() if row[5] else None,
                "category_id": row[6]
            })

        return jsonify({
            "page": page,
            "limit": limit,
            "total_products": total_products,
            "total_pages": total_pages,
            "products": products
        })

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


# T
# 7. تعداد محصولات در حال انقضاء (در یک ماه آینده)
@app.route('/expiring_products', methods=['GET'])
@with_db_connection
def expiring_products(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)")
    result = cursor.fetchone()
    return jsonify(result)



# 7.2 لیست محصولات در حال انقضاء (در یک ماه آینده) با پیجینیشن
@app.route('/expiring_productspn', methods=['GET'])
@with_db_connection
def expiring_productspn(connection, cursor):
    # دریافت پارامترهای صفحه‌بندی
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    
    try:
        # شمارش تعداد کل محصولات در حال انقضاء
        count_query = """
            SELECT COUNT(*) 
            FROM product 
            WHERE expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)
        """
        cursor.execute(count_query)
        total_products = cursor.fetchone()[0]
        total_pages = (total_products + limit - 1) // limit

        # دریافت لیست محصولات در حال انقضاء
        select_query = """
            SELECT product_id, name, price_per_unit, available_quantity, image_address, expiration_date, category_id FROM product
            WHERE expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)
            ORDER BY expiration_date ASC
            LIMIT %s OFFSET %s
        """
        offset = (page - 1) * limit
        cursor.execute(select_query, (limit, offset))

        products = []
        for row in cursor.fetchall():
            products.append({
                "product_id": row[0],
                "name": row[1],
                "price_per_unit": row[2],
                "available_quantity": row[3],
                "image_address": row[4],
                "expiration_date": row[5].isoformat() if row[5] else None,
                "category_id": row[6]
            })

        return jsonify({
            "page": page,
            "limit": limit,
            "total_products": total_products,
            "total_pages": total_pages,
            "products": products
        })

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500



# T
# 8. تعداد محصولات بدون تخفیف
@app.route('/no_discount_products', methods=['GET'])
@with_db_connection
def no_discount_products(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 9. مجموع وزن محصولات
@app.route('/total_weight', methods=['GET'])
@with_db_connection
def total_weight(connection, cursor):
    cursor.execute("SELECT name, weight, error_rate_in_weight, available_quantity FROM product")
    results = cursor.fetchall()
    
    if results:
        total_weight_sum = 0
        products = []
        for name, weight, error_rate, quantity in results:
            corrected_weight = (weight + (weight * error_rate)) * quantity
            total_weight_sum += corrected_weight
            products.append({"name": name, "corrected_weight": corrected_weight})
        return jsonify({"total_weight": total_weight_sum, "products": products})
    return jsonify({"error": "No products found"}), 404

# T
# 10. بیشترین قیمت هر واحد
@app.route('/max_price', methods=['GET'])
@with_db_connection
def max_price(connection, cursor):
    cursor.execute("SELECT MAX(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 11. کمترین قیمت هر واحد
@app.route('/min_price', methods=['GET'])
@with_db_connection
def min_price(connection, cursor):
    cursor.execute("SELECT MIN(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 12. تعداد محصولات با قیمت بیش از 10000 تومان
@app.route('/price_above_10000', methods=['GET'])
@with_db_connection
def price_above_10000(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit > 10000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 13. تعداد محصولات با وزن کمتر از 500 گرم
@app.route('/weight_below_500', methods=['GET'])
@with_db_connection
def weight_below_500(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE weight < 500")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 14. میانگین درصد تخفیف
@app.route('/average_discount', methods=['GET'])
@with_db_connection
def average_discount(connection, cursor):
    cursor.execute("SELECT AVG(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 15. تعداد محصولات با سود بیش از 100000 تومان
@app.route('/profit_above_1000', methods=['GET'])
@with_db_connection
def profit_above_1000(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales > 100000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 16. تعداد محصولات با تخفیف کمتر از 10 درصد
@app.route('/discount_below_10', methods=['GET'])
@with_db_connection
def discount_below_10(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE discount_percentage < 10")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 17. میانگین وزن محصولات
@app.route('/average_weight', methods=['GET'])
@with_db_connection
def average_weight(connection, cursor):
    cursor.execute("SELECT AVG(weight) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 18. بیشترین سود هر محصول
@app.route('/max_profit', methods=['GET'])
@with_db_connection
def max_profit(connection, cursor):
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 19. کمترین سود هر محصول
@app.route('/min_profit', methods=['GET'])
@with_db_connection
def min_profit(connection, cursor):
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 20. تعداد محصولات با سود منفی (ضرر)
@app.route('/negative_profit_products', methods=['GET'])
@with_db_connection
def negative_profit_products(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales < 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 21. مجموع تخفیف‌ها
@app.route('/total_discounts', methods=['GET'])
@with_db_connection
def total_discounts(connection, cursor):
    cursor.execute("SELECT SUM(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 22. تعداد محصولات با قیمت بین 5000 تا 10000 تومان
@app.route('/price_between_5000_10000', methods=['GET'])
@with_db_connection
def price_between_5000_10000(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit BETWEEN 5000 AND 10000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 23. میانگین سود هر محصول
@app.route('/average_profit', methods=['GET'])
@with_db_connection
def average_profit(connection, cursor):
    cursor.execute("SELECT AVG(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 24. تعداد محصولات با وزن بین 500 تا 1000 گرم
@app.route('/weight_between_500_1000', methods=['GET'])
@with_db_connection
def weight_between_500_1000(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE weight BETWEEN 500 AND 1000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 25. بیشترین سود در فروش
@app.route('/max_sales_profit', methods=['GET'])
@with_db_connection
def max_sales_profit(connection, cursor):
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 26. کمترین سود در فروش
@app.route('/min_sales_profit', methods=['GET'])
@with_db_connection
def min_sales_profit(connection, cursor):
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 27. میانگین قیمت محصولات بدون تخفیف
@app.route('/average_price_no_discount', methods=['GET'])
@with_db_connection
def average_price_no_discount(connection, cursor):
    cursor.execute("SELECT AVG(price_per_unit) FROM product WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 28. تعداد محصولات با سود بالای 500 تومان
@app.route('/profit_above_500', methods=['GET'])
@with_db_connection
def profit_above_500(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales > 500")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 29. میانگین سود هر واحد
@app.route('/average_profit_per_unit', methods=['GET'])
@with_db_connection
def average_profit_per_unit(connection, cursor):
    cursor.execute("SELECT AVG(total_profit_on_sales / number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 30. مجموع تعداد واحدهای فروخته شده
@app.route('/total_units_sold', methods=['GET'])
@with_db_connection
def total_units_sold(connection, cursor):
    cursor.execute("SELECT SUM(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 31. بیشترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/max_units_sold', methods=['GET'])
@with_db_connection
def max_units_sold(connection, cursor):
    cursor.execute("SELECT MAX(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 32. کمترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/min_units_sold', methods=['GET'])
@with_db_connection
def min_units_sold(connection, cursor):
    cursor.execute("SELECT MIN(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 33. میانگین تعداد واحدهای فروخته شده از یک محصول
@app.route('/average_units_sold', methods=['GET'])
@with_db_connection
def average_units_sold(connection, cursor):
    cursor.execute("SELECT AVG(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 34. تعداد محصولات با قیمت بیش از میانگین قیمت
@app.route('/price_above_average', methods=['GET'])
@with_db_connection
def price_above_average(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit > (SELECT AVG(price_per_unit) FROM product)")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 35. تعداد محصولات با تخفیف بیش از میانگین تخفیف
@app.route('/discount_above_average', methods=['GET'])
@with_db_connection
def discount_above_average(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE discount_percentage > (SELECT AVG(discount_percentage) FROM product)")
    result = cursor.fetchone()
    return jsonify(result)

"""
# 36. بیشترین تعداد واحدهای فروخته شده در یک ماه
@app.route('/max_units_sold_in_month', methods=['GET'])
def max_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(number_sold) FROM product WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 37. کمترین تعداد واحدهای فروخته شده در یک ماه
@app.route('/min_units_sold_in_month', methods=['GET'])
def min_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(number_sold) FROM product WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 38. مجموع تعداد واحدهای فروخته شده در یک ماه
@app.route('/total_units_sold_in_month', methods=['GET'])
def total_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(number_sold) FROM product WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)

# 39. میانگین تعداد واحدهای فروخته شده در یک ماه
@app.route('/average_units_sold_in_month', methods=['GET'])
def average_units_sold_in_month():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(number_sold) FROM product WHERE DATE_FORMAT(sold_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
    result = cursor.fetchone()
    return jsonify(result)
"""

# T
# 40. تعداد محصولات با سود هر واحد بیش از میانگین سود هر واحد
@app.route('/profit_per_unit_above_average', methods=['GET'])
@with_db_connection
def profit_per_unit_above_average(connection, cursor):
    cursor.execute("SELECT COUNT(*) FROM product WHERE (total_profit_on_sales / number_sold) > (SELECT AVG(total_profit_on_sales / number_sold) FROM product)")
    result = cursor.fetchone()
    return jsonify(result)

#------------------------------------------------------------------------------------------------------------------------------



# get available quantity of a product
@app.route('/getAvailableQuantity/<int:product_id>', methods=['GET'])
@with_db_connection
def get_available_quantity(connection, cursor, product_id):
    cursor.execute("SELECT available_quantity FROM grocery_store.product WHERE product_id = %s", (product_id,))
    result = cursor.fetchone()
    if result:
        return jsonify({'available_quantity': result[0]})
    return jsonify({'error': 'Product not found'}), 404






# if its worked delete this line and replace it by T
@app.route('/getProductspn', methods=['GET'])
@with_db_connection
def get_productspn(connection, cursor):
    try:
        if not connection.is_connected():
            connection.reconnect()
            cursor = connection.cursor()

        # Retrieve query parameters safely
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        search = request.args.get('search', default='', type=str)
        category_id = request.args.get('category_id', default=None, type=int)
        min_price = request.args.get('minPrice', default=None, type=int)
        max_price = request.args.get('maxPrice', default=None, type=int)
        sort_field = request.args.get('sort', default='name', type=str)
        sort_order = request.args.get('order', default='asc', type=str)

        # Log received parameters
        print("Received parameters:", {
            'page': page,
            'limit': limit,
            'search': search,
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort_field': sort_field,
            'sort_order': sort_order,
        })

        # Ensure sort field is valid
        valid_sort_fields = ['name', 'price_per_unit', 'available_quantity']
        if sort_field not in valid_sort_fields:
            print(f"Invalid sort field: {sort_field}, defaulting to 'name'")
            sort_field = 'name'

        sort_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        order_by_clause = f"ORDER BY product.{sort_field} {sort_direction}"

        # Filters and query parameters
        filters = []
        query_params = []

        if search:
            filters.append("(product.name LIKE %s OR category.category_name LIKE %s)")
            search_term = f"%{search}%"
            query_params.extend([search_term, search_term])

        if category_id is not None:
            filters.append("product.category_id = %s")
            query_params.append(category_id)

        if min_price is not None and max_price is not None:
            filters.append("product.price_per_unit BETWEEN %s AND %s")
            query_params.extend([min_price, max_price])
        elif min_price is not None:
            filters.append("product.price_per_unit >= %s")
            query_params.append(min_price)
        elif max_price is not None:
            filters.append("product.price_per_unit <= %s")
            query_params.append(max_price)

        filter_query = " WHERE " + " AND ".join(filters) if filters else ""

        # Get total product count
        count_query = f"""
            SELECT COUNT(*)
            FROM grocery_store.product
            JOIN category ON product.category_id = category.category_id
            {filter_query}
        """
        cursor.execute(count_query, tuple(query_params))
        total_products = cursor.fetchone()[0]
        total_pages = (total_products + limit - 1) // limit

        # Get product list with pagination
        offset = (page - 1) * limit
        select_query = f"""
            SELECT product.product_id, product.name, product.price_per_unit, product.available_quantity, 
            product.image_address, product.category_id, category.category_name
            FROM grocery_store.product
            JOIN category ON product.category_id = category.category_id
            {filter_query}
            {order_by_clause}
            LIMIT %s OFFSET %s
        """
        cursor.execute(select_query, tuple(query_params + [limit, offset]))

        products = [
            {
                'product_id': row[0],
                'name': row[1],
                'price_per_unit': row[2],
                'available_quantity': row[3],
                'image_address': row[4],
                'category_id': row[5],
                'category_name': row[6]
            }
            for row in cursor.fetchall()
        ]

        return jsonify({
            'page': page,
            'limit': limit,
            'total_products': total_products,
            'total_pages': total_pages,
            'products': products
        })
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")  # Debugging
        return jsonify({'error': str(err)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging
        return jsonify({'error': str(e)}), 500


@app.route('/getProduct/<int:product_id>', methods=['GET'])
@with_db_connection
def get_one_product(connection, cursor, product_id):
    query = """SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
    product.available_quantity, product.manufacturer_name, product.weight, product.purchase_price, 
    product.discount_percentage, product.voluminosity, product.combinations, 
    product.nutritional_information, product.expiration_date, product.storage_conditions, 
    product.number_sold, product.date_added_to_stock, product.total_profit_on_sales, 
    product.error_rate_in_weight, product.image_address, product.category_id, 
    uom.uom_name, category.category_name 
    FROM grocery_store.product 
    JOIN uom ON product.uom_id = uom.uom_id 
    JOIN category ON product.category_id = category.category_id 
    WHERE product.product_id = %s"""

    cursor.execute(query, (product_id,))
    product = cursor.fetchone()

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    response = {
        'product_id': product[0],
        'name': product[1],
        'uom_id': product[2],
        'price_per_unit': product[3],
        'available_quantity': product[4],
        'manufacturer_name': product[5],
        'weight': product[6],
        'purchase_price': product[7],
        'discount_percentage': product[8],
        'voluminosity': product[9],
        'combinations': product[10],
        'nutritional_information': product[11],
        'expiration_date': product[12],
        'storage_conditions': product[13],
        'number_sold': product[14],
        'date_added_to_stock': product[15],
        'total_profit_on_sales': product[16],
        'error_rate_in_weight': product[17],
        'image_address': product[18],
        'category_id': product[19],
        'uom_name': product[20],
        'category_name': product[21]
    }

    return jsonify(response)

# T
# update all attribute of a product except id
@app.route('/updateProduct/<int:product_id>', methods=['PUT'])
@with_db_connection
def update_product(connection, cursor, product_id):
    try:
        
        cursor.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            return jsonify({'error': 'Product not found'}), 404

        
        file_path = current_product[18]  
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                file_path = file.filename  # Save only the filename

        
        expiration_date = request.form.get('expiration_date')
        if expiration_date in [None, ""]:  
            expiration_date = current_product[12]  

        product_data = {
            'name': request.form.get('name', current_product[1]),
            'uom_id': request.form.get('uom_id', current_product[2]),
            'price_per_unit': request.form.get('price_per_unit', current_product[3]),
            'available_quantity': request.form.get('available_quantity', current_product[4]),
            'manufacturer_name': request.form.get('manufacturer_name', current_product[5]),
            'weight': request.form.get('weight', current_product[6]),
            'purchase_price': request.form.get('purchase_price', current_product[7]),
            'discount_percentage': request.form.get('discount_percentage', current_product[8]),
            'voluminosity': request.form.get('voluminosity', current_product[9]),
            'combinations': request.form.get('combinations', current_product[10]),
            'nutritional_information': request.form.get('nutritional_information', current_product[11]),
            'expiration_date': expiration_date,  
            'storage_conditions': request.form.get('storage_conditions', current_product[13]),
            'number_sold': request.form.get('number_sold', current_product[14]),
            'date_added_to_stock': request.form.get('date_added_to_stock', current_product[15]),
            'total_profit_on_sales': request.form.get('total_profit_on_sales', current_product[16]),
            'error_rate_in_weight': request.form.get('error_rate_in_weight', current_product[17]),
            'category_id': request.form.get('category_id', current_product[19]),
            'image_address': file_path
        }

        
        sql = """UPDATE product SET 
                    name = %s, uom_id = %s, price_per_unit = %s, available_quantity = %s,
                    manufacturer_name = %s, weight = %s, purchase_price = %s, discount_percentage = %s,
                    voluminosity = %s, combinations = %s, nutritional_information = %s, 
                    expiration_date = %s, storage_conditions = %s, number_sold = %s, 
                    date_added_to_stock = %s, total_profit_on_sales = %s, error_rate_in_weight = %s,
                    image_address = %s, category_id = %s
                WHERE product_id = %s"""
        
        values = (
            product_data['name'], product_data['uom_id'], product_data['price_per_unit'],
            product_data['available_quantity'], product_data['manufacturer_name'], 
            product_data['weight'], product_data['purchase_price'], product_data['discount_percentage'],
            product_data['voluminosity'], product_data['combinations'], 
            product_data['nutritional_information'], product_data['expiration_date'],
            product_data['storage_conditions'], product_data['number_sold'], 
            product_data['date_added_to_stock'], product_data['total_profit_on_sales'], 
            product_data['error_rate_in_weight'], product_data['image_address'],
            product_data['category_id'], product_id
        )

        cursor.execute(sql, values)
        connection.commit()
        return jsonify({'message': 'Product updated successfully', 'image_address': file_path})

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': f"Database error: {str(err)}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500



# T
# inserting all attribute of a product 
@app.route('/insertProduct', methods=['POST'])
@with_db_connection
def insert_product(connection, cursor):
    try:
        # Get the uploaded file
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        relative_file_path = os.path.relpath(file_path, app.config['UPLOAD_FOLDER'])

        # Extract product details from the form
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
            'image_address': relative_file_path
        }

        query = """INSERT INTO product (
                    name, uom_id, price_per_unit, available_quantity, manufacturer_name, 
                    weight, purchase_price, discount_percentage, voluminosity, combinations,
                    nutritional_information, expiration_date, storage_conditions, number_sold,
                    date_added_to_stock, total_profit_on_sales, error_rate_in_weight,
                    image_address, category_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        data = (
            product['name'], product['uom_id'], product['price_per_unit'],
            product['available_quantity'], product['manufacturer_name'], product['weight'],
            product['purchase_price'], product['discount_percentage'], product['voluminosity'],
            product['combinations'], product['nutritional_information'], product['expiration_date'],
            product['storage_conditions'], product['number_sold'], product['date_added_to_stock'],
            product['total_profit_on_sales'], product['error_rate_in_weight'], product['image_address'],
            product['category_id']
        )

        cursor.execute(query, data)
        connection.commit()
        product_id = cursor.lastrowid
        return jsonify({'message': 'Product added successfully', 'product_id': product_id}), 201

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500



# T
# worning !!! this function remove product from the universe (even in order_detale table like never exist)
@app.route('/deleteProduct', methods=['POST'])
@with_db_connection
def delete_product(connection, cursor):
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    try:
        # First, delete related records in order_details
        cursor.execute("DELETE FROM order_details WHERE product_id = %s", (product_id,))
        
        # Now, delete the product itself
        cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
        
        connection.commit()
        return jsonify({'message': 'Product deleted successfully', 'product_id': product_id}), 200

    except connection.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500



# T
# delete one specific product(just delete those product that dont have any sall)
@app.route('/deleteUnsallProduct', methods=['POST'])
@with_db_connection
def delete_unsall_product(connection, cursor):
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    try:
        cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
        connection.commit()
        return jsonify({'product_id': product_id}), 200

    except connection.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500



# T
# return all unites of mesurment
@app.route('/getUOM', methods=['GET'])
@with_db_connection
def get_uom(connection, cursor):
    cursor.execute("SELECT * FROM uom")
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
@with_db_connection
def get_category(connection, cursor):
    try:
        if not connection.is_connected():
            connection.reconnect(attempts=3, delay=2)
        cursor.execute("SELECT * FROM category")
        categories = cursor.fetchall()

        response = [{'category_id': row[0], 'category_name': row[1]} for row in categories]

        cursor.close()

        return jsonify(response)
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500








#--------------------------------------------------------------------------------------------------------------------------------



# Orders APIs
@app.route('/insertOrder', methods=['POST'])
@with_db_connection
def insert_order_api(connection, cursor):
    """
    دریافت payload JSON به شکل:
    {
      "customer_name": "...",
      "total": 123.45,
      "order_details": [
         {"product_id": 1, "quantity": 2, "total_price": 50.0},
         ...
      ]
    }
    و درج رکورد در جدول orders و order_details
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    # اعتبارسنجی اولیه‌ی فیلدهای اصلی
    if 'customer_name' not in data or 'total' not in data or 'order_details' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = connection.cursor()
    try:
        # ۱) درج در جدول orders
        insert_order_sql = """
            INSERT INTO orders (customer_name, total, date_time, customer_phone)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_order_sql, (
            data['customer_name'],
            data['total'],
            datetime.now(),
            data['customer_phone']
        ))
        order_id = cursor.lastrowid

        # ۲) برای هر جزئیات سفارش: بررسی موجودی و آماده‌سازی دیتای batch
        insert_details_sql = """
            INSERT INTO order_details (order_id, product_id, quantity, total_price, price_per_unit, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        details_params = []
        for item in data['order_details']:
            # اعتبارسنجی هر آیتم
            if not all(k in item for k in ('product_id', 'quantity', 'total_price', 'price_per_unit', 'category_id')):
                raise ValueError("Each order detail must include product_id, quantity, total_price, price_per_unit and category_id")
            
            # --- بررسی موجودی محصول ---
            cursor.execute(
                "SELECT available_quantity FROM products WHERE product_id = %s",
                (item['product_id'],)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Product ID {item['product_id']} does not exist")
            available_qty = row[0]
            if available_qty < item['quantity']:
                raise ValueError(f"Not enough stock for product {item['product_id']} (have {available_qty}, need {item['quantity']})")
            # --------------------------------

            details_params.append((
                order_id,
                item['product_id'],
                item['quantity'],
                item['total_price'],
                item['price_per_unit'],
                item['category_id']
            ))

        # ۳) درج همه‌ی جزئیات به‌صورت batch
        if details_params:
            cursor.executemany(insert_details_sql, details_params)

        # ۴) نهایی‌سازی تراکنش
        connection.commit()
        return jsonify({'order_id': order_id}), 201

    except ValueError as ve:
        connection.rollback()
        return jsonify({'error': str(ve)}), 400

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({'error': db_err.msg}), 500

    finally:
        cursor.close()
    




@app.route('/getAllOrders', methods=['GET'])
@with_db_connection
def get_all_orders(connection, cursor):
    try:
        cursor = connection.cursor()

        # ۱) واکشی همه‌ی سفارش‌ها
        cursor.execute("SELECT order_id, customer_name, total, date_time, customer_phone FROM orders")
        orders = [{
            'order_id': oid,
            'customer_name': cname,
            'total': total,
            'datetime': dt,
            'customer_phone': cp
        } for oid, cname, total, dt, cp in cursor.fetchall()]

        # ۲) برای هر سفارش، واکشی جزئیاتش و اضافه کردن به دیکشنری سفارش
        details_sql = """
            SELECT od.quantity, od.total_price,
                    p.name AS product_name, p.price_per_unit, category_id
            FROM order_details od
            LEFT JOIN products p ON od.product_id = p.product_id
            WHERE od.order_id = %s
        """
        for order in orders:
            cursor.execute(details_sql, (order['order_id'],))
            order['order_details'] = [{
                'quantity': qty,
                'total_price': price,
                'product_name': pname,
                'price_per_unit': ppu,
                'category_id' : ci
            } for qty, price, pname, ppu, ci in cursor.fetchall()]

        cursor.close()
        return jsonify(orders), 200

    except mysql.connector.Error as err:
        # در صورت هر خطای دیتابیس، rollback و پاسخ ۵۰۰
        connection.rollback()
        return jsonify({'error': str(err)}), 500










@app.route('/st1')
def st1():
    global streamlit_proc, timer

    if streamlit_proc is None or streamlit_proc.poll() is not None:
        streamlit_proc = subprocess.Popen(
            ["streamlit", "run", "st1.py", "--server.port=8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        timer = threading.Timer(300, lambda: streamlit_proc.kill())
        timer.start()

    html = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>شروع Streamlit</title></head>
      <body>
        <script>
          window.open("http://localhost:8501", "_blank", "resizable=yes,width=1200,height=800");
        </script>
        <p>✅ برنامه در پنجره جدید باز شد. لطفاً در ۵ دقیقه خرید خود را ثبت کنید.</p>
      </body>
    </html>
    """
    return render_template_string(html)

@app.route('/submit', methods=['POST'])
def submit():
    global streamlit_proc, timer

    data = request.get_json()
    print("📥 داده‌های دریافتی:", data)

    if timer:
        timer.cancel()
    if streamlit_proc:
        streamlit_proc.kill()
        streamlit_proc = None

    return jsonify({"status": "success", "received_data": data}), 200













@app.route("/calculate_total_weight", methods=["POST"])
@with_db_connection
def calculate_total_weight(connection, cursor):
    # دریافت داده‌های JSON از فرانت
    data = request.get_json()
    products_list = data.get("products", [])
    
    total_weight = 0.0
    details = []  # جزئیات هر محصول برای گزارش
    errors = []   # نگهداری پیام‌های خطا در صورت عدم یافتن محصول

    try:
        with connection.cursor() as cursor:
            for item in products_list:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 0)
                
                # اجرای کوئری برای دریافت اطلاعات محصول با استفاده از product_id
                sql = "SELECT weight, error_rate_in_weight FROM products WHERE product_id = %s"
                cursor.execute(sql, (product_id,))
                product = cursor.fetchone()
                
                if not product:
                    errors.append(f"محصول با آی‌دی {product_id} پیدا نشد")
                    continue

                unit_weight = product['weight']
                error_rate = product['error_rate_in_weight']
                
                # محاسبه وزن محصول به صورت: وزن کل = وزن واحد * تعداد * (1 + درصد خطا)
                product_weight = unit_weight * quantity * (1 + error_rate)
                total_weight += product_weight
                
                details.append({
                    "product_id": product_id,
                    "quantity": quantity,
                    "calculated_weight": product_weight
                })
    except Exception as e:
        return jsonify({"error": "خطا در اتصال یا اجرای کوئری دیتابیس", "exception": str(e)}), 500
    finally:
        connection.close()
    
    if errors:
        return jsonify({"error": errors}), 400
    
    return jsonify({
        "total_weight": total_weight,
        "products": details
    })




@app.route('/updateStockAfterOrder', methods=['POST'])
@with_db_connection
def update_stock_after_order(connection, cursor):
    """
    دریافت payload JSON با یکی از ساختارهای زیر:
    
    حالت اول (سفارش تک‌تک):
    {
      "order_details": [
          {"product_id": 1, "quantity": 2},
          {"product_id": 3, "quantity": 1},
          ...
      ]
    }
    
    حالت دوم (چند سفارش):
    {
       "orders": [
           {
               "order_id": 101,
               "order_details": [
                   {"product_id": 1, "quantity": 2},
                   {"product_id": 3, "quantity": 1}
               ]
           },
           {
               "order_id": 102,
               "order_details": [
                   {"product_id": 2, "quantity": 4}
               ]
           }
       ]
    }
    
    هدف: با توجه به تعداد خرید مشتری، موجودی محصولات را در جدول products کاهش دهیم.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # استخراج لیست جزئیات سفارش از payload
    order_items = []
    if "orders" in data:
        for order in data["orders"]:
            if "order_details" not in order:
                return jsonify({"error": "Missing order_details in one of the orders"}), 400
            order_items.extend(order["order_details"])
    elif "order_details" in data:
        order_items = data["order_details"]
    else:
        return jsonify({"error": "Missing order information"}), 400

    try:
        update_sql = """
            UPDATE products
            SET available_quantity = available_quantity - %s
            WHERE product_id = %s
        """
        # بررسی و به‌روزرسانی موجودی هر محصول
        for item in order_items:
            if not all(key in item for key in ("product_id", "quantity")):
                raise ValueError("هر جزئیات سفارش باید شامل product_id و quantity باشد")

            product_id = item["product_id"]
            quantity = item["quantity"]

            # بررسی موجودی فعلی محصول
            select_sql = "SELECT available_quantity FROM products WHERE product_id = %s"
            cursor.execute(select_sql, (product_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"محصول با آی‌دی {product_id} وجود ندارد")
            current_qty = row[0]
            if current_qty < quantity:
                raise ValueError(
                    f"موجودی ناکافی برای محصول {product_id} (موجود: {current_qty}, درخواست شده: {quantity})"
                )
            
            # به‌روزرسانی موجودی محصول
            cursor.execute(update_sql, (quantity, product_id))
        
        connection.commit()
        return jsonify({"message": "موجودی محصولات با موفقیت به روز شد"}), 200

    except ValueError as ve:
        connection.rollback()
        return jsonify({"error": str(ve)}), 400

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({"error": db_err.msg}), 500

    finally:
        cursor.close()









@app.route('/insertCustomer', methods=['POST'])
@with_db_connection
def insert_customer(connection, cursor):
    try:
        # دریافت فایل آپلود شده
        file = request.files['file']
        file_path = os.path.join(app.config['CUSTOMER_IMAGE'], file.filename)
        file.save(file_path)
        relative_file_path = os.path.relpath(file_path, app.config['CUSTOMER_IMAGE'])

        # استخراج اطلاعات مشتری از فرم ارسالی
        customer = {
            'customer_name': request.form.get('customer_name'),
            'customer_phone': request.form.get('customer_phone'),
            'membership_date': request.form.get('membership_date'),
            'number_of_purchases': request.form.get('number_of_purchases'),
            'total': request.form.get('total'),
            'image_address': relative_file_path
        }

        query = """INSERT INTO customer (
                    customer_name, customer_phone, membership_date, number_of_purchases, total, image_address
                ) VALUES (%s, %s, %s, %s, %s, %s)"""

        data = (
            customer['customer_name'],
            customer['customer_phone'],
            customer['membership_date'],
            customer['number_of_purchases'],
            customer['total'],
            customer['image_address']
        )

        cursor.execute(query, data)


        connection.commit()
        customer_id = cursor.lastrowid

        return jsonify({'message': 'Customer added successfully', 'customer_id': customer_id}), 201

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({'error': str(err)}), 500






@app.route('/updateCustomerAfterOrder', methods=['POST'])
@with_db_connection
def update_customer_after_order(connection, cursor):
    """
    دریافت payload JSON با ساختار زیر:
    {
      "customer_phone": "09123456789",
      "order_total": 250.75
    }
    
    هدف: افزایش فیلد number_of_purchases به تعداد ۱ و جمع مبلغ total به مقدار order_total
    در جدول customer برای مشتری با شماره تماس مشخص.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # اعتبارسنجی فیلدهای ورودی
    if "customer_phone" not in data or "order_total" not in data:
        return jsonify({"error": "Missing customer_phone or order_total"}), 400

    customer_phone = data["customer_phone"]
    try:
        order_total = float(data["order_total"])
    except (ValueError, TypeError):
        return jsonify({"error": "order_total must be a number"}), 400

    try:
        # بررسی وجود مشتری با phone
        select_sql = "SELECT total, number_of_purchases FROM customer WHERE customer_phone = %s"
        cursor.execute(select_sql, (customer_phone,))
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": f"مشتری با شماره {customer_phone} یافت نشد"}), 404

        # به‌روزرسانی رکورد مشتری
        update_sql = """
            UPDATE customer
            SET total = total + %s,
                number_of_purchases = number_of_purchases + 1
            WHERE customer_phone = %s
        """
        cursor.execute(update_sql, (order_total, customer_phone))
        connection.commit()

        return jsonify({
            "message": "مشخصات مشتری با موفقیت به‌روز شد",
            "customer_phone": customer_phone,
            "added_total": order_total,
            "new_number_of_purchases": row[1] + 1,
            "new_total": row[0] + order_total
        }), 200

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({"error": db_err.msg}), 500

    finally:
        cursor.close()






@app.route("/get_customer_info", methods=["GET"])
@with_db_connection
def get_customer_info(connection, cursor):
    # دریافت داده‌های JSON از فرانت
    data = request.get_json()
    customer_phone = data.get("customer_phone")
    
    # بررسی وجود شماره تماس مشتری در درخواست
    if not customer_phone:
        return jsonify({"error": "شماره تماس مشتری اجباری است"}), 400

    try:
        with connection.cursor() as cursor:
            # اجرای کوئری جهت جستجوی مشتری بر اساس شماره تماس
            sql = "SELECT * FROM customers WHERE customer_phone = %s"
            cursor.execute(sql, (customer_phone,))
            customer = cursor.fetchone()
            
            # در صورتی که مشتری یافت نشد، پیام خطای مناسب ارسال می‌شود
            if not customer:
                return jsonify({"error": "مشتری با این شماره تماس یافت نشد"}), 404

    except Exception as e:
        return jsonify({
            "error": "خطا در اتصال یا اجرای کوئری دیتابیس",
            "exception": str(e)
        }), 500

    finally:
        connection.close()  # بستن اتصال به دیتابیس در نهایت

    return jsonify(customer)








#--------------------------------------------------------------------------------------------------------



# return all products for scrool down
@app.route('/get_products', methods=['GET'])
def get_products():
    """ دریافت تمام نام کالاها """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM product")
    products = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    
    return jsonify({'products': products})



# return the search result base on type from the bigening the type for your search result
@app.route('/search_products', methods=['GET'])
def search_products():
    """ جستجوی کالاهایی که نامشان با متن وارد شده شروع می‌شود """
    search_term = request.args.get('query', '')  # دریافت متن جستجو از فرانت
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM product WHERE name LIKE %s", (search_term + '%',))
    filtered_products = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    
    return jsonify({'products': filtered_products})




#ثبت تصاویری دلخواه با دوربین از محصولا برای ترین 
#نام کاربر که یونیک است رو میگیره و با همون اسم به علاوه شماره ان تصویر در بک ذخیره میکند 
@app.route('/capture_new_product_image', methods=['POST'])
def capture_image():
    
    image_counter = 0
    # دریافت نام محصول از فرانت‌اند
    data = request.json
    product_name = data.get('product_name', 'default_product')  # مقدار پیش‌فرض در صورت نبود نام
    
    cap = cv2.VideoCapture(0)  # باز کردن دوربین
    if not cap.isOpened():
        return jsonify({'error': 'Unable to access the camera!'}), 500

    while True:
        ret, frame = cap.read()
        if not ret:
            return jsonify({'error': 'Failed to capture frame!'}), 500

        cv2.imshow('Webcam', frame)
        k = cv2.waitKey(1)

        if k % 256 == 27:  # ESC برای خروج
            print("Escape hit, closing...")
            break
        elif k % 256 == ord('s'):  # ذخیره تصویر محصول با نام اختصاصی
            img_name = os.path.join(output_dir, f"{product_name}_{image_counter}.png")
            cv2.imwrite(img_name, frame)
            print(f"Image {img_name} saved successfully!")
            image_counter += 1

    cap.release()
    cv2.destroyAllWindows()

    return jsonify({'message': f'Images saved for product: {product_name}'}), 200


#--------------------------------------------------------------------------------------------------------------------






@app.route("/get_customer_orders", methods=["GET"])
@with_db_connection
def get_customer_orders(connection, cursor):
    # دریافت داده‌های JSON از فرانت
    data = request.get_json()
    customer_phone = data.get("customer_phone")

    # بررسی وجود شماره تماس مشتری در درخواست
    if not customer_phone:
        return jsonify({"error": "شماره تماس مشتری اجباری است"}), 400

    try:
        # اجرای کوئری جهت جستجوی خریدهای مشتری بر اساس شماره تماس
        sql = """
            SELECT o.order_id, o.customer_name, o.total, o.date_time
            FROM orders o
            JOIN customer c ON o.customer_phone = c.customer_phone
            WHERE c.customer_phone = %s
        """
        cursor.execute(sql, (customer_phone,))
        orders = cursor.fetchall()

        # در صورتی که خریدی یافت نشد، پیام مناسب ارسال می‌شود
        if not orders:
            return jsonify({"error": "هیچ خریدی برای این شماره تماس یافت نشد"}), 404

        # ساخت لیست خریدهای مشتری
        order_list = []
        for order in orders:
            order_list.append({
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "total": order["total"],
                "date_time": order["date_time"]
            })
    except Exception as e:
        return jsonify({
            "error": "خطا در اتصال یا اجرای کوئری دیتابیس",
            "exception": str(e)
        }), 500

    return jsonify(order_list)

@app.route("/get_order_details/<int:order_id>", methods=["GET"])
@with_db_connection
def get_order_details(order_id, connection, cursor):
    try:
        # اجرای کوئری جهت دریافت جزئیات خرید بر اساس order_id
        sql = """
            SELECT 
                od.product_id, 
                p.name, 
                od.quantity, 
                od.total_price, 
                od.ppu, 
                c.category_name
            FROM order_details od
            JOIN product p ON od.product_id = p.product_id
            JOIN categories c ON od.category_id = c.category_id
            WHERE od.order_id = %s
        """
        cursor.execute(sql, (order_id,))
        order_details = cursor.fetchall()

        # در صورت عدم وجود جزئیات خرید برای شناسه دریافت‌شده
        if not order_details:
            return jsonify({"error": "جزئیاتی برای این خرید یافت نشد"}), 404
    except Exception as e:
        return jsonify({
            "error": "خطا در اتصال یا اجرای کوئری دیتابیس",
            "exception": str(e)
        }), 500

    return jsonify(order_details)



#-----------------------------------------------------------------------------------------------------------------------------------------




#های آماری با استفاده از سفارشات api

# 1. API: مجموع کل فروش
@app.route("/stats/total_sales", methods=["GET"])
@with_db_connection
def total_sales(connection, cursor):
    try:
        sql = "SELECT IFNULL(SUM(total), 0) AS total_sales FROM orders"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 2. API: تعداد کل سفارش‌ها
@app.route("/stats/total_orders", methods=["GET"])
@with_db_connection
def total_orders(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS total_orders FROM orders"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 3. API: میانگین ارزش سفارش‌ها
@app.route("/stats/average_order_value", methods=["GET"])
@with_db_connection
def average_order_value(connection, cursor):
    try:
        sql = "SELECT IFNULL(AVG(total), 0) AS avg_order_value FROM orders"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 4. API: سفارش‌ها بر اساس تاریخ (تعداد سفارش روزانه)
@app.route("/stats/orders_by_date", methods=["GET"])
@with_db_connection
def orders_by_date(connection, cursor):
    try:
        sql = """
        SELECT DATE(date_time) AS date, COUNT(*) AS order_count 
        FROM orders 
        GROUP BY DATE(date_time) 
        ORDER BY date
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 5. API: مجموع فروش روزانه
@app.route("/stats/sales_by_date", methods=["GET"])
@with_db_connection
def sales_by_date(connection, cursor):
    try:
        sql = """
        SELECT DATE(date_time) AS date, IFNULL(SUM(total), 0) AS daily_sales 
        FROM orders 
        GROUP BY DATE(date_time) 
        ORDER BY date
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 6. API: مجموع فروش ماهانه
@app.route("/stats/sales_by_month", methods=["GET"])
@with_db_connection
def sales_by_month(connection, cursor):
    try:
        sql = """
        SELECT DATE_FORMAT(date_time, '%Y-%m') AS month, IFNULL(SUM(total), 0) AS monthly_sales 
        FROM orders 
        GROUP BY DATE_FORMAT(date_time, '%Y-%m') 
        ORDER BY month
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 7. API: مجموع فروش سالانه
@app.route("/stats/sales_by_year", methods=["GET"])
@with_db_connection
def sales_by_year(connection, cursor):
    try:
        sql = """
        SELECT YEAR(date_time) AS year, IFNULL(SUM(total), 0) AS yearly_sales 
        FROM orders 
        GROUP BY YEAR(date_time) 
        ORDER BY year
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 8. API: مشتریان برتر (بزرگترین هزینه)
@app.route("/stats/top_customers", methods=["GET"])
@with_db_connection
def top_customers(connection, cursor):
    try:
        sql = """
        SELECT o.customer_phone, c.customer_name, IFNULL(SUM(o.total), 0) AS total_spent 
        FROM orders o
        JOIN customer c ON o.customer_phone = c.customer_phone
        GROUP BY o.customer_phone, c.customer_name
        ORDER BY total_spent DESC
        LIMIT 5
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 9. API: تعداد سفارش‌های هر مشتری
@app.route("/stats/customer_order_counts", methods=["GET"])
@with_db_connection
def customer_order_counts(connection, cursor):
    try:
        sql = "SELECT customer_phone, COUNT(*) AS order_count FROM orders GROUP BY customer_phone ORDER BY order_count DESC"
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 10. API: محصولات پرفروش (بر اساس تعداد)
@app.route("/stats/top_products", methods=["GET"])
@with_db_connection
def top_products(connection, cursor):
    try:
        sql = """
        SELECT od.product_id, p.name, IFNULL(SUM(od.quantity), 0) AS total_quantity 
        FROM order_details od
        JOIN product p ON od.product_id = p.product_id
        GROUP BY od.product_id, p.name
        ORDER BY total_quantity DESC
        LIMIT 5
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 11. API: درآمد هر محصول
@app.route("/stats/product_revenue", methods=["GET"])
@with_db_connection
def product_revenue(connection, cursor):
    try:
        sql = """
        SELECT od.product_id, p.name, IFNULL(SUM(od.total_price), 0) AS product_revenue 
        FROM order_details od
        JOIN product p ON od.product_id = p.product_id
        GROUP BY od.product_id, p.name
        ORDER BY product_revenue DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 12. API: درآمد بر اساس دسته‌بندی محصولات
@app.route("/stats/revenue_by_category", methods=["GET"])
@with_db_connection
def revenue_by_category(connection, cursor):
    try:
        sql = """
        SELECT c.category_id, c.category_name, IFNULL(SUM(od.total_price), 0) AS category_revenue 
        FROM order_details od
        JOIN categories c ON od.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY category_revenue DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 13. API: میانگین تعداد آیتم در هر سفارش
@app.route("/stats/average_items_per_order", methods=["GET"])
@with_db_connection
def average_items_per_order(connection, cursor):
    try:
        sql = """
        SELECT IFNULL(AVG(item_count), 0) AS avg_items_per_order 
        FROM (
            SELECT order_id, COUNT(*) AS item_count 
            FROM order_details 
            GROUP BY order_id
        ) AS sub
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 14. API: محبوب‌ترین دسته‌بندی‌ها (بر اساس تعداد سفارش)
@app.route("/stats/most_popular_categories", methods=["GET"])
@with_db_connection
def most_popular_categories(connection, cursor):
    try:
        sql = """
        SELECT c.category_id, c.category_name, COUNT(od.order_id) AS order_count
        FROM order_details od
        JOIN categories c ON od.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY order_count DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 15. API: تعداد سفارشات در 30 روز گذشته
@app.route("/stats/orders_last_30_days", methods=["GET"])
@with_db_connection
def orders_last_30_days(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS orders_last_30 FROM orders WHERE date_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 16. API: مجموع فروش در 30 روز گذشته
@app.route("/stats/sales_last_30_days", methods=["GET"])
@with_db_connection
def sales_last_30_days(connection, cursor):
    try:
        sql = "SELECT IFNULL(SUM(total), 0) AS sales_last_30 FROM orders WHERE date_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 17. API: تعداد سفارشات در 7 روز گذشته
@app.route("/stats/orders_last_7_days", methods=["GET"])
@with_db_connection
def orders_last_7_days(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS orders_last_7 FROM orders WHERE date_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 18. API: مجموع فروش در 7 روز گذشته
@app.route("/stats/sales_last_7_days", methods=["GET"])
@with_db_connection
def sales_last_7_days(connection, cursor):
    try:
        sql = "SELECT IFNULL(SUM(total), 0) AS sales_last_7 FROM orders WHERE date_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 19. API: تعداد سفارشات در یک ساعت گذشته
@app.route("/stats/orders_last_hour", methods=["GET"])
@with_db_connection
def orders_last_hour(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS orders_last_hour FROM orders WHERE date_time >= DATE_SUB(NOW(), INTERVAL 1 HOUR)"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 20. API: ساعت اوج سفارشات (ساعتی که بیشترین سفارش ثبت شده)
@app.route("/stats/peak_order_hour", methods=["GET"])
@with_db_connection
def peak_order_hour(connection, cursor):
    try:
        sql = "SELECT HOUR(date_time) AS hour, COUNT(*) AS order_count FROM orders GROUP BY HOUR(date_time) ORDER BY order_count DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 21. API: الگوی سفارشات در یک روز (با گروه‌بندی بر اساس ساعت)
@app.route("/stats/daily_order_pattern", methods=["GET"])
@with_db_connection
def daily_order_pattern(connection, cursor):
    try:
        # دریافت تاریخ از پارامترهای GET یا استفاده از تاریخ امروز
        date_str = request.args.get("date")
        if not date_str:
            date_str = datetime.date.today().isoformat()
        sql = """
        SELECT HOUR(date_time) AS hour, COUNT(*) AS orders 
        FROM orders 
        WHERE DATE(date_time) = %s 
        GROUP BY HOUR(date_time)
        ORDER BY hour
        """
        cursor.execute(sql, (date_str,))
        result = cursor.fetchall()
        return jsonify({"date": date_str, "pattern": result})
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 22. API: نرخ نگهداری مشتریان (مشتریانی که بیش از یک سفارش داشته‌اند)
@app.route("/stats/customer_retention", methods=["GET"])
@with_db_connection
def customer_retention(connection, cursor):
    try:
        sql_total = "SELECT COUNT(DISTINCT customer_phone) AS total_customers FROM orders"
        cursor.execute(sql_total)
        total_customers = cursor.fetchone()["total_customers"]
        sql_repeat = """
        SELECT COUNT(*) AS repeat_customers 
        FROM (SELECT customer_phone, COUNT(*) AS order_count FROM orders GROUP BY customer_phone HAVING order_count > 1) AS sub
        """
        cursor.execute(sql_repeat)
        repeat_customers = cursor.fetchone()["repeat_customers"]
        retention_rate = (repeat_customers / total_customers * 100) if total_customers else 0
        return jsonify({
            "total_customers": total_customers,
            "repeat_customers": repeat_customers,
            "retention_rate_percentage": retention_rate
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 23. API: مشتریان جدید در مقابل مشتریان برگشتی
@app.route("/stats/new_vs_returning_customers", methods=["GET"])
@with_db_connection
def new_vs_returning_customers(connection, cursor):
    try:
        sql = "SELECT customer_phone, COUNT(*) AS order_count FROM orders GROUP BY customer_phone"
        cursor.execute(sql)
        data = cursor.fetchall()
        new_customers = sum(1 for d in data if d["order_count"] == 1)
        returning_customers = sum(1 for d in data if d["order_count"] > 1)
        return jsonify({
            "new_customers": new_customers,
            "returning_customers": returning_customers
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 24. API: نرخ تحقق سفارش (با استفاده از ستون status، فرض شده 'fulfilled' نشان‌دهنده تکمیل است)
@app.route("/stats/order_fulfillment_rate", methods=["GET"])
@with_db_connection
def order_fulfillment_rate(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS total, SUM(CASE WHEN status='fulfilled' THEN 1 ELSE 0 END) AS fulfilled FROM orders"
        cursor.execute(sql)
        res = cursor.fetchone()
        rate = (res["fulfilled"] / res["total"] * 100) if res["total"] else 0
        return jsonify({
            "total_orders": res["total"],
            "fulfilled_orders": res["fulfilled"],
            "fulfillment_rate_percentage": rate
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 25. API: نرخ لغو سفارش
@app.route("/stats/cancellation_rate", methods=["GET"])
@with_db_connection
def cancellation_rate(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS total, SUM(CASE WHEN status='canceled' THEN 1 ELSE 0 END) AS canceled FROM orders"
        cursor.execute(sql)
        res = cursor.fetchone()
        rate = (res["canceled"] / res["total"] * 100) if res["total"] else 0
        return jsonify({
            "total_orders": res["total"],
            "canceled_orders": res["canceled"],
            "cancellation_rate_percentage": rate
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 26. API: فروش بر اساس روش پرداخت (فرض بر این که ستون payment_method در orders موجود است)
@app.route("/stats/sales_by_payment_method", methods=["GET"])
@with_db_connection
def sales_by_payment_method(connection, cursor):
    try:
        sql = "SELECT payment_method, IFNULL(SUM(total), 0) AS total_sales FROM orders GROUP BY payment_method"
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 27. API: فروش بر اساس منطقه (فرض شده ستون region در جدول customer موجود است)
@app.route("/stats/sales_by_region", methods=["GET"])
@with_db_connection
def sales_by_region(connection, cursor):
    try:
        sql = """
        SELECT c.region, IFNULL(SUM(o.total), 0) AS total_sales 
        FROM orders o
        JOIN customer c ON o.customer_phone = c.customer_phone
        GROUP BY c.region
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 28. API: خلاصه جزئیات سفارش‌ها (تعداد آیتم‌ها، مجموع تعداد، و درآمد کل)
@app.route("/stats/order_details_summary", methods=["GET"])
@with_db_connection
def order_details_summary(connection, cursor):
    try:
        sql = "SELECT COUNT(*) AS total_items, IFNULL(SUM(quantity), 0) AS total_quantity, IFNULL(SUM(total_price), 0) AS total_revenue FROM order_details"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 29. API: میانگین ارزش سفارش به ازای هر مشتری
@app.route("/stats/customer_average_order_value", methods=["GET"])
@with_db_connection
def customer_average_order_value(connection, cursor):
    try:
        sql = "SELECT customer_phone, AVG(total) AS avg_order_value FROM orders GROUP BY customer_phone ORDER BY avg_order_value DESC"
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 30. API: میانه ارزش سفارش‌ها
@app.route("/stats/median_order_value", methods=["GET"])
@with_db_connection
def median_order_value(connection, cursor):
    try:
        sql = """
        SELECT AVG(total) AS median_order_value FROM (
            SELECT total FROM orders
            ORDER BY total
            LIMIT 2 - (SELECT COUNT(*) FROM orders) % 2
            OFFSET (SELECT (COUNT(*) - 1) / 2 FROM orders)
        ) AS med
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 31. API: واریانس و انحراف معیار ارزش سفارش‌ها
@app.route("/stats/order_variance_std", methods=["GET"])
@with_db_connection
def order_variance_std(connection, cursor):
    try:
        sql = "SELECT VARIANCE(total) AS variance, STD(total) AS std_deviation FROM orders"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 32. API: میانگین تعداد محصولات در هر سفارش
@app.route("/stats/products_per_order", methods=["GET"])
@with_db_connection
def products_per_order(connection, cursor):
    try:
        sql = "SELECT AVG(product_count) AS avg_products_per_order FROM (SELECT order_id, COUNT(*) AS product_count FROM order_details GROUP BY order_id) AS sub"
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 33. API: نرخ سفارش‌های تکراری (درصد سفارش‌هایی که از مشتریان برگشتی هستند)
@app.route("/stats/repeat_order_rate", methods=["GET"])
@with_db_connection
def repeat_order_rate(connection, cursor):
    try:
        sql_total = "SELECT COUNT(*) AS total_orders FROM orders"
        cursor.execute(sql_total)
        total = cursor.fetchone()["total_orders"]
        sql_repeat = "SELECT COUNT(*) AS repeat_orders FROM orders WHERE customer_phone IN (SELECT customer_phone FROM orders GROUP BY customer_phone HAVING COUNT(*) > 1)"
        cursor.execute(sql_repeat)
        repeat_orders = cursor.fetchone()["repeat_orders"]
        rate = (repeat_orders / total * 100) if total else 0
        return jsonify({
            "total_orders": total,
            "repeat_orders": repeat_orders,
            "repeat_order_rate_percentage": rate
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 34. API: توزیع فروش ساعتی برای امروز
@app.route("/stats/hrly_sales_distribution", methods=["GET"])
@with_db_connection
def hrly_sales_distribution(connection, cursor):
    try:
        sql = "SELECT HOUR(date_time) AS hour, IFNULL(SUM(total), 0) AS sales FROM orders WHERE DATE(date_time) = CURDATE() GROUP BY HOUR(date_time) ORDER BY hour"
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 35. API: میانگین فروش روزانه طی 30 روز گذشته
@app.route("/stats/daily_sales_average", methods=["GET"])
@with_db_connection
def daily_sales_average(connection, cursor):
    try:
        sql = """
        SELECT AVG(daily_sales) AS avg_daily_sales FROM (
            SELECT DATE(date_time) AS date, IFNULL(SUM(total), 0) AS daily_sales 
            FROM orders 
            WHERE date_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(date_time)
        ) AS sub
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 36. API: روند فروش هفتگی (12 هفته اخیر)
@app.route("/stats/weekly_sales_trend", methods=["GET"])
@with_db_connection
def weekly_sales_trend(connection, cursor):
    try:
        sql = "SELECT YEARWEEK(date_time) AS week, IFNULL(SUM(total), 0) AS weekly_sales FROM orders GROUP BY YEARWEEK(date_time) ORDER BY week DESC LIMIT 12"
        cursor.execute(sql)
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 37. API: رشد فروش ماهانه (مقایسه فروش ماه جاری با ماه قبلی)
@app.route("/stats/monthly_sales_growth", methods=["GET"])
@with_db_connection
def monthly_sales_growth(connection, cursor):
    try:
        sql_current = "SELECT IFNULL(SUM(total), 0) AS current_sales FROM orders WHERE MONTH(date_time)=MONTH(CURDATE()) AND YEAR(date_time)=YEAR(CURDATE())"
        cursor.execute(sql_current)
        current_sales = cursor.fetchone()["current_sales"]
        
        sql_prev = "SELECT IFNULL(SUM(total), 0) AS previous_sales FROM orders WHERE MONTH(date_time)=MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND YEAR(date_time)=YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))"
        cursor.execute(sql_prev)
        previous_sales = cursor.fetchone()["previous_sales"]

        growth_rate = ((current_sales - previous_sales) / previous_sales * 100) if previous_sales else None
        return jsonify({
            "current_sales": current_sales,
            "previous_sales": previous_sales,
            "growth_rate_percentage": growth_rate
        })
    except Exception as e:
        return jsonify({"error": "خطا در اجرای کوئری", "exception": str(e)}), 500

# 38. API: تعداد سفارش‌ها و درآمد بر اساس دسته‌ب






if __name__ == "__main__":
    app.run(port=5000,debug=True)