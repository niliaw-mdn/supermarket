from flask import Flask, jsonify, request, send_from_directory
import mysql.connector
from flask_cors import CORS
from functools import wraps
import os
from db_connection import get_db_connection, close_connection
import subprocess
import time
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








# مسیر اجرای Streamlit
STREAMLIT_COMMAND_1 = ["streamlit", "run", "st1.py"]

@app.route('/start_streamlit_1', methods=['GET'])
def start_streamlit_1():
    try:
        # بررسی اینکه آیا Streamlit در حال اجرا است
        process = subprocess.Popen(STREAMLIT_COMMAND_1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)  # زمان کوتاهی برای راه‌اندازی

        return jsonify({"message": "✅ اپلیکیشن Streamlit راه‌اندازی شد!"}), 200
    except Exception as e:
        return jsonify({"error": f"مشکل در اجرای Streamlit: {str(e)}"}), 500









if __name__ == "__main__":
    app.run(port=5000,debug=True)