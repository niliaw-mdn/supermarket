from back.sql_connection import get_sql_connection


def get_all_products(connection):
    cursor = connection.cursor()

    query = ("SELECT  product.product_id, product.name, product.uom_id, product.price_per_unit, "
            "product.available_quantity, image_address, category_id, uom.uom_name FROM grocery_store.product inner join uom on "
            "product.uom_id=uom.uom_id,category.category_name FROM grocery_store.product inner join category on "
            "product.category_id=category.category;")

    cursor.execute(query)

    response = []
    for (product_id, name, uom_id, price_per_unit, available_quantity, uom_name, image_address, category_id,category_name) in cursor:
        response.append(
            {
                'product_id': product_id,
                'name': name,
                'uom_id': uom_id,
                'price_per_unit': price_per_unit,
                'uom_name': uom_name,
                'available_quantity': available_quantity,
                'image_address': image_address,
                'category_id': category_id,
                'category_name': category_name
            }
        )

    return response


def get_product(connection, product_id):
    cursor = connection.cursor()

    query = ("""SELECT product.product_id, product.name, product.uom_id, product.price_per_unit, 
    product.available_quantity, manufacturer_name, weight, purchase_price, discount_percentage, voluminosity, 
    combinations, nutritional_information, expiration_date, storage_conditions, number_sold, date_added_to_stock, 
    total_profit_on_sales, error_rate_in_weight, image_address, category_id, uom.uom_name FROM grocery_store.product join uom on 
    product.uom_id=uom.uom_id , category.category_name FROM grocery_store.product inner join category on 
    product.category_id=category.category WHERE product.product_id = %s""")

    cursor.execute(query, (product_id,))

    product = cursor.fetchone()

    if product is None:
        return None

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
        'uom_name': product[18],
        'image_address': product[19],
        'category_id': product[20],
        'category_name': product[21]
    }

    return response









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
