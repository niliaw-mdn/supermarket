import cv2
from flask import Flask, jsonify, redirect, request, Response, send_from_directory, render_template_string
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

from datetime import datetime, date 

import signal

from statistics import median

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
NEW_PRODUCT_IMG = os.path.join(BASE_DIR, 'new_product_img')
CUSTOMER_IMAGE = os.path.join(BASE_DIR, 'customer_image')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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
    if 'customer_name' not in data or 'total' not in data or 'order_detale' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    cursor = connection.cursor()
    try:
        # ۱) درج در جدول orders
        insert_order_sql = """
            INSERT INTO orders (customer_name, total, date_time, payment_method_id, customer_phone )
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_order_sql, (
            data['customer_name'],
            data['total'],
            datetime.now(),
            data['payment_method_id'],
            data['customer_phone']
        ))
        order_id = cursor.lastrowid

        # ۲) برای هر جزئیات سفارش: بررسی موجودی و آماده‌سازی دیتای batch
        insert_details_sql = """
            INSERT INTO order_detale (order_id, product_id, quantity, total_price, price_per_unit, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        details_params = []
        for item in data['order_details']:
            # اعتبارسنجی هر آیتم
            if not all(k in item for k in ('product_id', 'quantity', 'total_price', 'price_per_unit', 'category_id')):
                raise ValueError("Each order detail must include product_id, quantity, total_price, price_per_unit and category_id")
            
            # --- بررسی موجودی محصول ---
            cursor.execute(
                "SELECT available_quantity FROM product WHERE product_id = %s",
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

# راه‌اندازی Streamlit پس از رسیدن به مسیر /st1
@app.route('/st1')
def start_streamlit():
    # اجرای Streamlit به‌عنوان پروسس فرعی
    subprocess.Popen(['streamlit', 'run', 'st1.py'])
    # ریدایرکت به رابط Streamlit (به پورت پیش‌فرض 8501)
    return redirect("http://localhost:8501", code=302)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    print("لیست نهایی خرید دریافت شد:", data)
    # در اینجا می‌توانید داده را ذخیره یا پردازش کنید
    return "OK", 200




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
            if "order_detale" not in order:
                return jsonify({"error": "Missing order_details in one of the orders"}), 400
            order_items.extend(order["order_details"])
    elif "order_details" in data:
        order_items = data["order_details"]
    else:
        return jsonify({"error": "Missing order information"}), 400

    try:
        update_sql = """
            UPDATE product
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
            select_sql = "SELECT available_quantity FROM product WHERE product_id = %s"
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