from sql_connection import get_sql_connection


def get_all_products(connection):
    cursor = connection.cursor()

    query = ("SELECT  product.product_id, product.name, product.uom_id, product.price_per_unit, "
            "product.available_quantity, image_address, uom.uom_name FROM grocery_store.product inner join uom on "
            "product.uom_id=uom.uom_id;")

    cursor.execute(query)

    response = []
    for (product_id, name, uom_id, price_per_unit, available_quantity, uom_name, image_address) in cursor:
        response.append(
            {
                'product_id': product_id,
                'name': name,
                'uom_id': uom_id,
                'price_per_unit': price_per_unit,
                'uom_name': uom_name,
                'available_quantity': available_quantity,
                'image_address': image_address
            }
        )

    return response


def get_product(connection, product_id):
    cursor = connection.cursor()

    query = ("""SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
    product.available_quantity, manufacturer_name, weight, purchase_price, discount_percentage, voluminosity, 
    combinations, nutritional_information, expiration_date, storage_conditions, number_sold, date_added_to_stock, 
    total_profit_on_sales, error_rate_in_weight, image_address, uom.uom_name FROM grocery_store.product join uom on 
    product.uom_id=uom.uom_id WHERE product.product_id = %s""")

    cursor.execute(query, (product_id,))

    product = cursor.fetchone()

    if product is None:
        return None

    response = {
        'name': product[0],
        'uom_id': product[1],
        'price_per_unit': product[2],
        'available_quantity': product[3],
        'manufacturer_name': product[4],
        'weight': product[5],
        'purchase_price': product[6],
        'discount_percentage': product[7],
        'voluminosity': product[8],
        'combinations': product[9],
        'nutritional_information': product[10],
        'expiration_date': product[11],
        'storage_conditions': product[12],
        'number_sold': product[13],
        'date_added_to_stock': product[14],
        'total_profit_on_sales': product[15],
        'error_rate_in_weight': product[16],
        'uom_name': product[17],
        'image_address': product[18]
    }

    return response



def insert_new_product(connection, product):
    cursor = connection.cursor()

    query = ("""insert into product (name, uom_id, price_per_unit, available_quantity,
                manufacturer_name, weight, purchase_price, discount_percentage, voluminosity,
                combinations, nutritional_information, expiration_date, storage_conditions,
                number_sold, date_added_to_stock, total_profit_on_sales, error_rate_in_weight, image_address)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")

    data = (product['name'], product['uom_id'], product['price_per_unit'], product['available_quantity'],
            product['manufacturer_name'], product['weight'], product['purchase_price'],
            product['discount_percentage'], product['voluminosity'], product['combinations'],
            product['nutritional_information'], product['expiration_date'], product['storage_conditions'], product['number_sold'],
            product['date_added_to_stock'], product['total_profit_on_sales'], product['error_rate_in_weight'], product['image_address'])

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid



def delete_product(connection, product_id):
    # sourcery skip: use-fstring-for-concatenation
    cursor = connection.cursor()

    query = ("DELETE FROM product where product_id=" + str(product_id))

    cursor.execute(query)
    connection.commit()


def update_product(connection, product_id, product_data):
    cursor = connection.cursor()

    # Define the expected keys
    expected_keys = [
        'name', 'uom_id', 'price_per_unit', 'available_quantity',
        'manufacturer_name', 'weight', 'purchase_price', 'discount_percentage',
        'voluminosity', 'combinations', 'nutritional_information', 'expiration_date',
        'storage_conditions', 'number_sold', 'date_added_to_stock', 'total_profit_on_sales',
        'error_rate_in_weight', 'image_address'
    ]

    # Ensure all expected keys are present
    for key in expected_keys:
        if key not in product_data:
            raise ValueError(f"Missing key: {key}")

    sql = """ UPDATE product SET name = %s,
                uom_id = %s,
                price_per_unit = %s,
                available_quantity = %s,
                manufacturer_name = %s,
                weight = %s,
                purchase_price = %s,
                discount_percentage = %s,
                voluminosity = %s,
                combinations = %s,
                nutritional_information = %s,
                expiration_date = %s,
                storage_conditions = %s,
                number_sold = %s,
                date_added_to_stock = %s,
                total_profit_on_sales = %s,
                error_rate_in_weight = %s
                WHERE product_id = %s """

    values = (product_data['name'], product_data['uom_id'], product_data['price_per_unit'],
                product_data['available_quantity'], product_data['manufacturer_name'],
                product_data['weight'], product_data['purchase_price'], product_data['discount_percentage'],
                product_data['voluminosity'], product_data['combinations'], product_data['nutritional_information'],
                product_data['expiration_date'], product_data['storage_conditions'], product_data['number_sold'],
                product_data['date_added_to_stock'], product_data['total_profit_on_sales'],
                product_data['error_rate_in_weight'],
                product_id)

    cursor.execute(sql, values)
    connection.commit()
    cursor.close()


#have to be complete for availablity
def get_available_quantity(connection, product_id):
    cursor = connection.cursor()

    query = f"SELECT product.available_quantity FROM grocery_store.product WHERE product_id={[product_id]}"

    cursor.execute(query)

    return [
        {'available_quantity': available_quantity}
        for available_quantity in cursor
    ]


if __name__ == '__main__':
    connection = get_sql_connection()
    product = {
        'Ali' ,
    }
    print(get_product(connection,1))
