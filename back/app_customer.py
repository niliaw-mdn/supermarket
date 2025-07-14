import cv2
from flask import Flask, jsonify, redirect, request, Response, send_from_directory, render_template_string
import mysql.connector
from flask_cors import CORS
from functools import wraps
import os
from db_connection import get_db_connection, close_connection
import subprocess
import time
import traceback

import subprocess
import json
import sys

import threading

from datetime import datetime, date 

import signal

from statistics import median


import socket
from flask import Flask, jsonify, request, make_response
from functools import wraps



app = Flask(__name__)
CORS(app)
# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
NEW_PRODUCT_IMG = os.path.join(BASE_DIR, 'new_product_img')
CUSTOMER_IMAGE = os.path.join(BASE_DIR, 'customer_image')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CUSTOMER_IMAGE, exist_ok=True)
os.makedirs(NEW_PRODUCT_IMG, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NEW_PRODUCT_IMG'] = NEW_PRODUCT_IMG

app.config['CUSTOMER_IMAGE'] = CUSTOMER_IMAGE

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










@app.route('/getAvailableQuantity/<int:product_id>', methods=['GET'])
@with_db_connection
def get_available_quantity(connection, cursor, product_id):
    cursor.execute("SELECT available_quantity FROM grocery_store.product WHERE product_id = %s", (product_id,))
    result = cursor.fetchone()
    if result:
        return jsonify({'available_quantity': result[0]})
    return jsonify({'error': 'Product not found'}), 404


@app.route('/getProductspn', methods=['GET'])
@with_db_connection
def get_productspn(connection, cursor):
    try:
        if not connection.is_connected():
            connection.reconnect()
        cursor = connection.cursor()

        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=20, type=int)
        search = request.args.get('search', default='', type=str)
        category_id = request.args.get('category_id', default=None, type=int)
        min_price = request.args.get('minPrice', default=None, type=int)
        max_price = request.args.get('maxPrice', default=None, type=int)
        sort_field = request.args.get('sort', default='name', type=str)
        sort_order = request.args.get('order', default='asc', type=str)
        brand = request.args.get('brand', default=None, type=str)  # 🔸 فیلتر برند

        print("Received parameters:", {
            'page': page,
            'limit': limit,
            'search': search,
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort_field': sort_field,
            'sort_order': sort_order,
            'brand': brand
        })

        valid_sort_fields = ['name', 'price_per_unit', 'available_quantity', 'manufacturer_name']
        if sort_field not in valid_sort_fields:
            print(f"Invalid sort field: {sort_field}, defaulting to 'name'")
            sort_field = 'name'

        sort_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        order_by_clause = f"ORDER BY product.{sort_field} {sort_direction}"

        filters = []
        query_params = []

        if search:
            filters.append("(product.name LIKE %s OR categories.category_name LIKE %s OR product.manufacturer_name LIKE %s)")
            search_term = f"%{search}%"
            query_params.extend([search_term, search_term, search_term])

        if category_id is not None:
            filters.append("product.category_id = %s")
            query_params.append(category_id)

        if brand:
            filters.append("product.manufacturer_name = %s")
            query_params.append(brand)

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

        count_query = f"""
            SELECT COUNT(*)
            FROM grocery_store.product
            JOIN categories ON product.category_id = categories.category_id
            {filter_query}
        """
        cursor.execute(count_query, tuple(query_params))
        total_products = cursor.fetchone()[0]
        total_pages = (total_products + limit - 1) // limit

        offset = (page - 1) * limit
        select_query = f"""
            SELECT product.product_id, product.name, product.price_per_unit, product.available_quantity, 
                   product.image_address, product.category_id, categories.category_name, product.manufacturer_name
            FROM grocery_store.product
            JOIN categories ON product.category_id = categories.category_id
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
                'category_name': row[6],
                'manufacturer_name': row[7]
            }
            for row in cursor.fetchall()
        ]

        response_data = {
            'page': page,
            'limit': limit,
            'total_products': total_products,
            'total_pages': total_pages,
            'products': products
        }
        return Response(json.dumps(response_data, ensure_ascii=False), content_type='application/json; charset=utf-8')

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return Response(json.dumps({'error': str(err)}, ensure_ascii=False), content_type='application/json; charset=utf-8'), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(json.dumps({'error': str(e)}, ensure_ascii=False), content_type='application/json; charset=utf-8'), 500
    


@app.route('/getProduct/<int:product_id>', methods=['GET'])
@with_db_connection
def get_one_product(connection, cursor, product_id):
    query = """
        SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
               product.available_quantity, product.manufacturer_name, product.weight, 
               product.purchase_price, product.discount_percentage, product.voluminosity, 
               product.combinations, product.nutritional_information, product.expiration_date, 
               product.storage_conditions, product.number_sold, product.date_added_to_stock, 
               product.total_profit_on_sales, product.error_rate_in_weight, 
               product.image_address, product.category_id, 
               uom.uom_name, categories.category_name 
        FROM grocery_store.product 
        JOIN uom ON product.uom_id = uom.uom_id 
        JOIN categories ON product.category_id = categories.category_id 
        WHERE product.product_id = %s
    """

    cursor.execute(query, (product_id,))
    product = cursor.fetchone()

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    def safe_date(val):
        return val.isoformat() if isinstance(val, (datetime, date)) else val

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
        'expiration_date': safe_date(product[12]),
        'storage_conditions': product[13],
        'number_sold': product[14],
        'date_added_to_stock': safe_date(product[15]),
        'total_profit_on_sales': product[16],
        'error_rate_in_weight': product[17],
        'image_address': product[18],
        'category_id': product[19],
        'uom_name': product[20],
        'category_name': product[21]
    }

    return Response(
        json.dumps(response, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )










# Orders APIs
@app.route('/insertOrder', methods=['POST'])
@with_db_connection
def insert_order_api(connection, cursor):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    required = ('customer_name', 'customer_phone', 'payment_method_id', 'products')
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing one or more required fields'}), 400

    products_dict = data['products']
    if not isinstance(products_dict, dict) or not products_dict:
        return jsonify({'error': 'products must be a non-empty object'}), 400

    try:
        product_names = list(products_dict.keys())
        placeholders = ','.join(['%s'] * len(product_names))
        cursor.execute(
            f"""SELECT product_id, name, price_per_unit, category_id, available_quantity
                FROM product WHERE name IN ({placeholders})""",
            tuple(product_names)
        )
        rows = cursor.fetchall()
        if not rows:
            raise ValueError("None of the provided products were found in the database.")

        product_info_map = {
            row[1]: {
                'product_id': row[0],
                'price': row[2],
                'category_id': row[3],
                'available_quantity': row[4]
            }
            for row in rows
        }

        enriched_details = []
        total_sum = 0.0

        for name, qty in products_dict.items():
            if name not in product_info_map:
                raise ValueError(f"Product not found: {name}")

            if not isinstance(qty, (int, float)) or qty <= 0:
                raise ValueError(f"Invalid quantity for product: {name}")

            info = product_info_map[name]
            if info['available_quantity'] < qty:
                raise ValueError(f"Not enough stock for product '{name}' (available: {info['available_quantity']}, requested: {qty})")

            total_price = info['price'] * qty
            total_sum += total_price

            enriched_details.append({
                'product_name': name,
                'product_id': info['product_id'],
                'quantity': qty,
                'price_per_unit': info['price'],
                'total_price': total_price,
                'category_id': info['category_id']
            })

        # درج در جدول orders
        cursor.execute("""
            INSERT INTO orders (customer_name, customer_phone, payment_method_id, total, date_time)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['customer_name'],
            data['customer_phone'],
            data['payment_method_id'],
            total_sum,
            datetime.now()
        ))
        order_id = cursor.lastrowid

        # درج order_details
        cursor.executemany("""
            INSERT INTO order_detale (order_id, product_id, quantity, total_price, ppu, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [
            (
                order_id,
                d['product_id'],
                d['quantity'],
                d['total_price'],
                d['price_per_unit'],
                d['category_id']
            ) for d in enriched_details
        ])

        connection.commit()
        return jsonify({
            'order_id': order_id,
            'total': total_sum,
            'order_details': enriched_details
        }), 201

    except ValueError as ve:
        connection.rollback()
        return jsonify({'error': str(ve)}), 400

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({'error': db_err.msg}), 500

    finally:
        cursor.close()












# Global variables for Streamlit management
st_process = None
st_running = False
st_port = 8501

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(('localhost', port)) == 0

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(1)
    return False




PurchaseFlag = {'Purchase_Flag': False}


@app.route('/st1')
def launch_streamlit():
    global st_process, st_running, st_port

    port = st_port 
    
    try:
        def monitor_streamlit(process):
            global st_running
            while True:
                if process.poll() is not None:
                    st_running = False
                    break
                time.sleep(1)
        
        if st_process is None or st_process.poll() is not None:
            while is_port_in_use(port):
                port += 1
            st_port = port
            
            # Get the absolute path to the script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, 'st1.py')
            
            # Verify the file exists
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Streamlit script not found at {script_path}")
            
            # Correct command structure
            cmd = [
                sys.executable,
                '-m',
                'streamlit',
                'run',
                script_path,
                '--server.port',
                str(port),
                '--server.headless',
                'true',
                '--server.enableCORS',
                'false'
            ]
            
            print("Executing command:", ' '.join(cmd))  # Debug output
            
            # Start the process
            st_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=base_dir,  # Set working directory
                text=True
            )
            
            st_running = True
            threading.Thread(target=monitor_streamlit, args=(st_process,), daemon=True).start()
            
            if not wait_for_port(port, timeout=60):
                raise Exception(f"Streamlit did not start on port {port}")
        
        return jsonify({
            'status': 'success',
            'port': port,
            'url': f'http://localhost:{port}'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500







# راه‌اندازی Streamlit پس از رسیدن به مسیر /st1
@app.route('/submit', methods=['POST'])
@with_db_connection
def submit_purchase(connection, cursor):
    try:
        # دریافت داده JSON از درخواست
        purchase_data = request.get_json()
        
        # بررسی وجود داده
        if not purchase_data:
            return jsonify({'error': 'No purchase data provided'}), 400
        
        # تبدیل دیکشنری به رشته JSON برای ذخیره در دیتابیس
        json_purchase = json.dumps(purchase_data)
        
        # درج داده در جدول purchases
        query = """INSERT INTO purchases (purchase_data) VALUES (%s)"""
        cursor.execute(query, (json_purchase,))
        
        # اعمال تغییرات در دیتابیس
        connection.commit()
        


        PurchaseFlag['Purchase_Flag'] = not PurchaseFlag['Purchase_Flag'] 


        getPurchaseFlag = True
        # دریافت شناسه خرید ثبت شده
        purchase_id = cursor.lastrowid
        
        return jsonify({
            'message': 'Purchase submitted successfully',
            'purchase_id': purchase_id,
            'purchase_data': purchase_data
        }), 200

    except mysql.connector.Error as err:
        # بازگردانی تغییرات در صورت خطا
        connection.rollback()
        return jsonify({'error': f'Database error: {str(err)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    





@app.route('/getPurchaseFlag', methods=['GET'])
def total_products():

    return jsonify({'Purchase Flag': PurchaseFlag['Purchase_Flag']})






@app.route('/oldestPurchase', methods=['GET'])
@with_db_connection
def get_oldest_purchase(connection, cursor):
    try:
        # کوئری برای دریافت جدیدترین رکورد
        query = """
        SELECT id, purchase_data, created_at 
        FROM purchases 
        ORDER BY created_at DESC 
        LIMIT 1;
        """
        cursor.execute(query)
        record = cursor.fetchone()
        
        if not record:
            return jsonify({'message': 'No purchases found'}), 404
        
        # تبدیل داده‌ها
        purchase_id, purchase_data, created_at = record
        
        # اگر purchase_data به صورت رشته JSON است، آن را به دیکشنری تبدیل کن
        if isinstance(purchase_data, str):
            try:
                purchase_data = json.loads(purchase_data)
            except json.JSONDecodeError:
                pass  # در صورت خطا، رشته باقی می‌ماند
        
        # تغییر فلگ
        PurchaseFlag['Purchase_Flag'] = not PurchaseFlag['Purchase_Flag'] 
        
        # حذف رکورد از دیتابیس
        delete_query = "DELETE FROM purchases WHERE id = %s"
        cursor.execute(delete_query, (purchase_id,))
        connection.commit()

        return jsonify({
            'purchase_id': purchase_id,
            'purchase_data': purchase_data,
            'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {str(err)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500







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
                sql = "SELECT weight, error_rate_in_weight FROM product WHERE product_id = %s"
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

    1) دیکشنری مستقیم {product_name: quantity, …}
    2) {"order_details": [ {"product_id": X, "quantity": Y}, … ]}
    3) {"orders": [ {"order_details": [… ]}, … ]}

    هدف: کاهش available_quantity در جدول product
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # ————————————— تشخیص ورودی «نام محصول → تعداد» —————————————
    order_items = []
    # اگر خود payload دیکشنری از نام محصول به تعداد باشد:
    if all(isinstance(v, (int, float)) for v in data.values()) and not any(k in data for k in ("orders", "order_details")):
        # واکشی همه نام‌ها و یافتن product_id
        product_names = list(data.keys())
        placeholders = ','.join(['%s'] * len(product_names))
        cursor.execute(
            f"SELECT product_id, name FROM product WHERE name IN ({placeholders})",
            tuple(product_names)
        )
        rows = cursor.fetchall()
        # نام‌های پیدا شده
        found = {row[1]: row[0] for row in rows}
        # بررسی وجود همه‌ی نام‌ها
        missing = set(product_names) - set(found.keys())
        if missing:
            return jsonify({"error": f"Products not found: {', '.join(missing)}"}), 400

        # ساختار مشترک order_items
        for name, qty in data.items():
            order_items.append({
                'product_id': found[name],
                'quantity': qty
            })

    # حالت دوم: payload شامل orders یا order_details باشد
    elif "orders" in data:
        for order in data["orders"]:
            if "order_details" not in order:
                return jsonify({"error": "Missing order_details in one of the orders"}), 400
            order_items.extend(order["order_details"])

    elif "order_details" in data:
        order_items = data["order_details"]

    else:
        return jsonify({"error": "Missing order information"}), 400

    # ————————————— اجرای بروزرسانی موجودی —————————————
    try:
        update_sql = """
            UPDATE product
            SET available_quantity = available_quantity - %s
            WHERE product_id = %s
        """
        for item in order_items:
            if not all(k in item for k in ("product_id", "quantity")):
                raise ValueError("Each order detail must include product_id and quantity")

            pid = item["product_id"]
            qty = item["quantity"]
            if not isinstance(qty, (int, float)) or qty <= 0:
                raise ValueError(f"Invalid quantity for product_id {pid}")

            # بررسی موجودی فعلی
            cursor.execute("SELECT available_quantity FROM product WHERE product_id = %s", (pid,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Product ID {pid} does not exist")
            current_qty = row[0]
            if current_qty < qty:
                raise ValueError(f"Not enough stock for product_id {pid} (have {current_qty}, need {qty})")

            # کاهش موجودی
            cursor.execute(update_sql, (qty, pid))

        connection.commit()
        return jsonify({"message": "Stock levels updated successfully"}), 200

    except ValueError as ve:
        connection.rollback()
        return jsonify({"error": str(ve)}), 400

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({"error": db_err.msg}), 500

    finally:
        cursor.close()



@app.route('/customer_image/<filename>')
def serve_customer_image(filename):
    return send_from_directory(app.config["CUSTOMER_IMAGE"], filename)
        
@app.route('/insertCustomer', methods=['POST'])
@with_db_connection
def insert_customer(connection, cursor):
    try:
        phone = request.form.get('customer_phone')
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400

        # بررسی وجود مشتری با شماره تلفن داده شده
        cursor.execute("SELECT customer_id FROM customer WHERE customer_phone = %s", (phone,))
        existing_customer = cursor.fetchone()

        if existing_customer:
            # مشتری قبلا ثبت شده، فقط customer_id برگردان
            customer_id = existing_customer[0]
            return jsonify({'message': 'Customer already exists', 'customer_id': customer_id}), 200

        # اگر مشتری وجود نداشت، ثبت نام جدید انجام می‌شود
        file = request.files.get('file')
        if file:
            timestamp = int(time.time())
            file_extension = os.path.splitext(file.filename)[1]
            simple_filename = f"customer_{timestamp}{file_extension}"
            file_path = os.path.join(app.config['CUSTOMER_IMAGE'], simple_filename)
            file.save(file_path)
            relative_file_path = f"/customer_image/{simple_filename}"
        else:
            relative_file_path = None

        customer = {
            'customer_name': request.form.get('customer_name'),
            'customer_phone': phone,
            'membership_date': request.form.get('membership_date'),
            'number_of_purchases': request.form.get('number_of_purchases'),
            'total': request.form.get('total'),
            'image_address': relative_file_path
        }

        query = """INSERT INTO customer (
                    customer_name, customer_phone, membership_date, number_of_purchases, total, image_address
                ) VALUES (%s, %s, NOW(), %s, %s, %s)"""

        data = (
            customer['customer_name'],
            customer['customer_phone'],
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
    دریافت payload JSON با ساختار:
    {
      "customer_phone": "09123456789"
    }

    تغییرات:
    - پیدا کردن آخرین سفارش مشتری بر اساس شماره تماس از جدول orders
    - خواندن total آن سفارش
    - افزایش number_of_purchases و total در جدول customer
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    if "customer_phone" not in data:
        return jsonify({"error": "Missing customer_phone"}), 400

    customer_phone = data["customer_phone"]

    try:
        # 1. بررسی وجود مشتری
        cursor.execute(
            "SELECT total, number_of_purchases FROM customer WHERE customer_phone = %s",
            (customer_phone,)
        )
        row = cursor.fetchone()
        if row is None:
            return jsonify({"error": f"مشتری با شماره {customer_phone} یافت نشد"}), 404
        old_total, old_purchases = row

        # 2. گرفتن جدیدترین سفارش مشتری از جدول orders
        cursor.execute(
            """
            SELECT total FROM orders
            WHERE customer_phone = %s
            ORDER BY date_time DESC
            LIMIT 1
            """,
            (customer_phone,)
        )
        order_row = cursor.fetchone()
        if not order_row:
            return jsonify({"error": "هیچ سفارشی برای این مشتری ثبت نشده است"}), 404

        order_total = order_row[0]

        # 3. به‌روزرسانی اطلاعات مشتری
        cursor.execute("""
            UPDATE customer
            SET total = total + %s,
                number_of_purchases = number_of_purchases + 1
            WHERE customer_phone = %s
        """, (order_total, customer_phone))

        connection.commit()

        return jsonify({
            "message": "مشخصات مشتری با موفقیت به‌روز شد",
            "customer_phone": customer_phone,
            "added_total": order_total,
            "new_number_of_purchases": old_purchases + 1,
            "new_total": old_total + order_total
        }), 200

    except mysql.connector.Error as db_err:
        connection.rollback()
        return jsonify({"error": db_err.msg}), 500

    finally:
        cursor.close()






@app.route("/get_customer_info", methods=["POST"])
@with_db_connection
def get_customer_info(connection, cursor):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "داده‌های درخواست نامعتبر است"}), 400
        
        customer_phone = data.get("customer_phone")
        if not customer_phone:
            return jsonify({"error": "شماره تماس مشتری اجباری است"}), 400
        
        # استفاده از دیکشنری‌کرسر
        cursor = connection.cursor(dictionary=True)
        
        sql = """
        SELECT customer_name, customer_phone, image_address, membership_date, number_of_purchases
        FROM customer
        WHERE customer_phone = %s
        """
        cursor.execute(sql, (customer_phone,))
        customer = cursor.fetchone()
        
        if not customer:
            return jsonify({"error": "مشتری با این شماره تماس یافت نشد"}), 404
        
        customer_data = {
            "customer_name": customer["customer_name"],
            "customer_phone": customer["customer_phone"],
            "image_address": customer["image_address"] if customer["image_address"] not in [None, ""] else "/pic/avatar.png",
            "membership_date": customer["membership_date"].strftime("%Y-%m-%d") if customer["membership_date"] else None,
            "number_of_purchases": customer["number_of_purchases"] or 0
        }
        
        return jsonify(customer_data)

    except Exception as e:
        print(f"Error in get_customer_info: {str(e)}")
        return jsonify({
            "error": "خطای سرور",
            "details": str(e)
        }), 500

    
    

@app.route("/update_customer_info", methods=["POST"])
@with_db_connection
def update_customer_info(connection, cursor):
    try:
        data = request.get_json()

        customer_phone = data.get("customer_phone")
        customer_name = data.get("customer_name")


        if not customer_phone:
            return jsonify({"error": "شماره تماس مشتری اجباری است"}), 400

        sql = """
        UPDATE customer
        SET customer_name = %s
        WHERE customer_phone = %s
        """
        cursor.execute(sql, (
            customer_name, customer_phone
        ))
        connection.commit()

        return jsonify({"message": "اطلاعات با موفقیت به‌روزرسانی شد"})

    except Exception as e:
        print(f"Error in update_customer_info: {str(e)}")
        return jsonify({"error": "خطای سرور", "details": str(e)}), 500



@app.route("/get_customer_orders", methods=["POST"])
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
            FROM order_detale od
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

























if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)