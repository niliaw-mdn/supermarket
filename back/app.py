import os
from flask import Flask, jsonify, request
import mysql.connector
import cv2
from sql_connection import get_sql_connection
from flask_cors import CORS
from flask import send_from_directory



app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
NEW_PRODUCT_IMG = os.path.join(BASE_DIR, 'new_product_img')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(NEW_PRODUCT_IMG, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NEW_PRODUCT_IMG'] = NEW_PRODUCT_IMG

connection = get_sql_connection()

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
# T
# 1. تعداد کل محصولات
@app.route('/total_products', methods=['GET'])
def total_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 2. میانگین قیمت هر واحد
@app.route('/average_price', methods=['GET'])
def average_price():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 3. بیشترین تخفیف داده شده
@app.route('/max_discount', methods=['GET'])
def max_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 4. کمترین وزن
@app.route('/min_weight', methods=['GET'])
def min_weight():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(weight) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 5. مجموع سود
@app.route('/total_profit', methods=['GET'])
def total_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 6. تعداد محصولات منقضی شده
@app.route('/expired_products', methods=['GET'])
def expired_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE expiration_date < CURDATE()")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 7. تعداد محصولات در حال انقضاء (در یک ماه آینده)
@app.route('/expiring_products', methods=['GET'])
def expiring_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE expiration_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 1 MONTH)")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 8. تعداد محصولات بدون تخفیف
@app.route('/no_discount_products', methods=['GET'])
def no_discount_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 9. مجموع وزن محصولات
@app.route('/total_weight', methods=['GET'])
def total_weight():
    cursor = connection.cursor()

    # گرفتن نام محصول، وزن، میزان خطا، و تعداد موجودی از دیتابیس
    cursor.execute("SELECT name, weight, error_rate_in_weight, available_quantity FROM product")
    results = cursor.fetchall()
    
    cursor.close()

    if results:
        total_weight_sum = 0
        products = []

        for name, weight, error_rate, quantity in results:
            corrected_weight = (weight + (weight * error_rate)) * quantity
            total_weight_sum += corrected_weight
            products.append({"name": name, "corrected_weight": corrected_weight})

        return jsonify({"total_weight": total_weight_sum, "products": products})

    else:
        return jsonify({"error": "No products found"}), 404

# T
# 10. بیشترین قیمت هر واحد
@app.route('/max_price', methods=['GET'])
def max_price():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 11. کمترین قیمت هر واحد
@app.route('/min_price', methods=['GET'])
def min_price():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(price_per_unit) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 12. تعداد محصولات با قیمت بیش از 10000 تومان
@app.route('/price_above_10000', methods=['GET'])
def price_above_10000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit > 10000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 13. تعداد محصولات با وزن کمتر از 500 گرم
@app.route('/weight_below_500', methods=['GET'])
def weight_below_500():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE weight < 500")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 14. میانگین درصد تخفیف
@app.route('/average_discount', methods=['GET'])
def average_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 15. تعداد محصولات با سود بیش از 1000 تومان
@app.route('/profit_above_1000', methods=['GET'])
def profit_above_1000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales > 1000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 16. تعداد محصولات با تخفیف کمتر از 10 درصد
@app.route('/discount_below_10', methods=['GET'])
def discount_below_10():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE discount_percentage < 10")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 17. میانگین وزن محصولات
@app.route('/average_weight', methods=['GET'])
def average_weight():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(weight) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 18. بیشترین سود هر محصول
@app.route('/max_profit', methods=['GET'])
def max_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 19. کمترین سود هر محصول
@app.route('/min_profit', methods=['GET'])
def min_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 20. تعداد محصولات با سود منفی (ضرر)
@app.route('/negative_profit_products', methods=['GET'])
def negative_profit_products():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales < 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 21. مجموع تخفیف‌ها
@app.route('/total_discounts', methods=['GET'])
def total_discounts():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(discount_percentage) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 22. تعداد محصولات با قیمت بین 5000 تا 10000 تومان
@app.route('/price_between_5000_10000', methods=['GET'])
def price_between_5000_10000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit BETWEEN 5000 AND 10000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 23. میانگین سود هر محصول
@app.route('/average_profit', methods=['GET'])
def average_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 24. تعداد محصولات با وزن بین 500 تا 1000 گرم
@app.route('/weight_between_500_1000', methods=['GET'])
def weight_between_500_1000():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE weight BETWEEN 500 AND 1000")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 25. بیشترین سود در فروش
@app.route('/max_sales_profit', methods=['GET'])
def max_sales_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 26. کمترین سود در فروش
@app.route('/min_sales_profit', methods=['GET'])
def min_sales_profit():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(total_profit_on_sales) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 27. میانگین قیمت محصولات بدون تخفیف
@app.route('/average_price_no_discount', methods=['GET'])
def average_price_no_discount():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(price_per_unit) FROM product WHERE discount_percentage = 0")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 28. تعداد محصولات با سود بالای 500 تومان
@app.route('/profit_above_500', methods=['GET'])
def profit_above_500():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE total_profit_on_sales > 500")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 29. میانگین سود هر واحد
@app.route('/average_profit_per_unit', methods=['GET'])
def average_profit_per_unit():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(total_profit_on_sales / weight) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 30. مجموع تعداد واحدهای فروخته شده
@app.route('/total_units_sold', methods=['GET'])
def total_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 31. بیشترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/max_units_sold', methods=['GET'])
def max_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 32. کمترین تعداد واحدهای فروخته شده از یک محصول
@app.route('/min_units_sold', methods=['GET'])
def min_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT MIN(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 33. میانگین تعداد واحدهای فروخته شده از یک محصول
@app.route('/average_units_sold', methods=['GET'])
def average_units_sold():
    cursor = connection.cursor()
    cursor.execute("SELECT AVG(number_sold) FROM product")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 34. تعداد محصولات با قیمت بیش از میانگین قیمت
@app.route('/price_above_average', methods=['GET'])
def price_above_average():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE price_per_unit > (SELECT AVG(price_per_unit) FROM product)")
    result = cursor.fetchone()
    return jsonify(result)

# T
# 35. تعداد محصولات با تخفیف بیش از میانگین تخفیف
@app.route('/discount_above_average', methods=['GET'])
def discount_above_average():
    cursor = connection.cursor()
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
def profit_per_unit_above_average():
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM product WHERE (total_profit_on_sales / weight) > (SELECT AVG(total_profit_on_sales / weight) FROM product)")
    result = cursor.fetchone()
    return jsonify(result)

#------------------------------------------------------------------------------------------------------------------------------



# get available quantity of a product
@app.route('/getAvailableQuantity/<int:product_id>', methods=['GET'])
def get_available_quantity(product_id):

    cursor = connection.cursor()

    query = "SELECT available_quantity FROM grocery_store.product WHERE product_id = %s"
    cursor.execute(query, (product_id,))

    result = cursor.fetchone()

    cursor.close()
    # connection.close()

    if result:
        return jsonify({'available_quantity': result[0]})
    else:
        return jsonify({'error': 'Product not found'}), 404






# if its worked delete this line and replace it by T
# returning all products in page nation from db 
@app.route('/getProductspn', methods=['GET'])
def get_productspn():
    cursor = connection.cursor()

    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=20, type=int)
    search = request.args.get('search', default='', type=str)
    category_id = request.args.get('category_id', type=int)
    uom_id = request.args.get('uom_id', type=int)

    offset = (page - 1) * limit

    filters = []
    params = []

    if search:
        filters.append("(product.name LIKE %s OR category.category_name LIKE %s OR uom.uom_name LIKE %s)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    if category_id:
        filters.append("product.category_id = %s")
        params.append(category_id)

    if uom_id:
        filters.append("product.uom_id = %s")
        params.append(uom_id)

    filter_query = " WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
               product.available_quantity, product.image_address, product.category_id, 
               uom.uom_name, category.category_name 
        FROM grocery_store.product 
        JOIN uom ON product.uom_id = uom.uom_id 
        JOIN category ON product.category_id = category.category_id
        {filter_query}
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    cursor.execute(query, tuple(params))

    products = []
    for row in cursor.fetchall():
        products.append({
            'product_id': row[0],
            'name': row[1],
            'uom_id': row[2],
            'price_per_unit': row[3],
            'available_quantity': row[4],
            'image_address': row[5],
            'category_id': row[6],
            'uom_name': row[7],
            'category_name': row[8]
        })

    count_query = f"""
        SELECT COUNT(*) 
        FROM grocery_store.product 
        JOIN uom ON product.uom_id = uom.uom_id 
        JOIN category ON product.category_id = category.category_id
        {filter_query}
    """
    cursor.execute(count_query, tuple(params[:-2]))  # Exclude limit and offset
    total_products = cursor.fetchone()[0]

    cursor.close()

    return jsonify({
        'page': page,
        'limit': limit,
        'total_products': total_products,
        'total_pages': (total_products + limit - 1) // limit,
        'products': products
    })




# T
# returning all products in db
@app.route('/getProducts', methods=['GET'])
def get_products():
    cursor = connection.cursor()

    query = """SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
                    product.available_quantity, product.image_address, product.category_id, 
                    uom.uom_name, category.category_name 
                FROM grocery_store.product 
                JOIN uom ON product.uom_id = uom.uom_id 
                JOIN category ON product.category_id = category.category_id"""

    cursor.execute(query)
    
    products = []
    for row in cursor.fetchall():
        product = {
            'product_id': row[0],
            'name': row[1],
            'uom_id': row[2],
            'price_per_unit': row[3],
            'available_quantity': row[4],
            'image_address': row[5],
            'category_id': row[6],
            'uom_name': row[7],
            'category_name': row[8]
        }
        products.append(product)

    cursor.close()
    # connection.close()

    return jsonify(products)

@app.route('/productimages/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# T
# returning all entiteis of a specific product
@app.route('/getProduct/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    cursor = connection.cursor()

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
        'category_id': product[19],  # Now explicitly from product table
        'uom_name': product[20],
        'category_name': product[21]
    }

    return jsonify(response)




# T
# update all attribute of a product except id
@app.route('/updateProduct/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        # First, retrieve the current image path from the database (in case we don't upload a new image)
        cursor = connection.cursor()
        cursor.execute("SELECT image_address FROM product WHERE product_id = %s", (product_id,))
        current_image_path = cursor.fetchone()

        if current_image_path:
            current_image_path = current_image_path[0]
        else:
            return jsonify({'error': 'Product not found'}), 404

        # Check if a new image is uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':  # Ensure the file is not empty
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                # Use the new file path if a new image is uploaded
            else:
                file_path = current_image_path  # Use the existing image path if no file is uploaded
        else:
            file_path = current_image_path  # Use the existing image path if no file is uploaded

        # Extract product details from the form
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
            'image_address': file_path  # Set the image address (either new or old path)
        }

        # Prepare the SQL UPDATE query
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

        # Execute the update query
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
            # connection.close()


# T
# inserting all attribute of a product 
@app.route('/insertProduct', methods=['POST'])
def insert_product():
    try:
        # Get the uploaded file
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Generate the relative path for the image
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
            'image_address': relative_file_path  # Store the relative path
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
    try:
        # بررسی و اطمینان از زنده بودن اتصال
        if not connection.is_connected():
            connection.reconnect(attempts=3, delay=2)

        with connection.cursor() as cursor:
            query = "SELECT * FROM category"
            cursor.execute(query)
            categories = cursor.fetchall()

        response = [{'category_id': row[0], 'category_name': row[1]} for row in categories]

        return jsonify(response)
    
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500





if __name__ == "__main__":
    app.run(port=5000,debug=True)