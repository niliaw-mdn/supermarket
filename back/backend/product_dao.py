from sql_connection import get_sql_connection



def get_all_products(connection):
    cursor = connection.cursor()
    query = """ SELECT  product.product_id, product.name, product.uom_id,
    product.price_per_unit, product.available_quantity, product.image_data,
    uom.uom_name FROM grocery_store.product inner join uom on product.uom_id=uom.uom_id;"""
    cursor.execute(query)
    response = []
    for (product_id, name, uom_id, price_per_unit, available_quantity, uom_name, image_data) in cursor:
        response.append(
            {    
                'product_id' : product_id,
                'name' : name,
                'uom_id' : uom_id,
                'price_per_unit' : price_per_unit,
                'uom_name' : uom_name,
                'available_quantity' : available_quantity,
                'image_data' : image_data
            }   
        )        
    return response



def get_product(connection, product_id):
    cursor = connection.cursor()
    query = ("""SELECT product.product_id, product.name, product.uom_id, product.price_per_unit,
                product.available_quantity, product.image_data, manufacturer_name, weight,
                purchase_price, discount_percentage, voluminosity, combinations,
                nutritional_information, expiration_date, storage_conditions, number_sold,
                date_added_to_stock, total_profit_on_sales, error_rate_in_weight,
                uom.uom_name FROM grocery_store.product inner join uom on product.uom_id=uom.uom_id WHERE product_id=""" + str(product_id))
    cursor.execute(query)
    response = []
    for (product_id, name, uom_id, price_per_unit, available_quantity, uom_name,
            image_data, manufacturer_name, weight, purchase_price, discount_percentage,
            voluminosity, combinations, nutritional_information, expiration_date,
            storage_conditions, number_sold, date_added_to_stock, total_profit_on_sales, error_rate_in_weight) in cursor:
        response.append(
            {    
                'product_id' : product_id,
                'name' : name,
                'uom_id' : uom_id,
                'price_per_unit' : price_per_unit,
                'uom_name' : uom_name,
                'available_quantity' : available_quantity,
                'image_data' : image_data,
                'manufacturer_name' : manufacturer_name,
                'weight' : weight,
                'purchase_price' : purchase_price, 
                'discount_percentage' : discount_percentage,
                'voluminosity' : voluminosity,
                'combinations' : combinations,
                'nutritional_information' : nutritional_information,
                'expiration_date' : expiration_date,
                'storage_conditions' : storage_conditions,
                'number_sold' : number_sold,
                'date_added_to_stock' : date_added_to_stock,
                'total_profit_on_sales' : total_profit_on_sales,
                'error_rate_in_weight' : error_rate_in_weight
            }   
        )        
    return response
    
    
def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = ("""insert into product (name, uom_id, price_per_unit, available_quantity, image_data,
                manufacturer_name, weight, purchase_price, discount_percentage, voluminosity,
                combinations, nutritional_information, expiration_date, storage_conditions,
                number_sold, date_added_to_stock, total_profit_on_sales, error_rate_in_weight)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""") # this line has too be complete
    
    data = (product['product_name'], product['uom_id'], product['price_per_unit'], product['available_quantity'],
            product['image_data'], product['manufacturer_name'], product['weight'], product['purchase_price'], 
            product['discount_percentage'], product['voluminosity'], product['combinations'], product['nutritional_information'], 
            product['expiration_date'], product['storage_conditions'], product['number_sold'], product['date_added_to_stock'],
            product['total_profit_on_sales'], product['error_rate_in_weight'])
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
    sql = """ UPDATE products SET product_name = %s,
                uom_id = %s,
                price_per_unit = %s,
                available_quantity = %s,
                image_data = %s,
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
    
    values = ( product_data['product_name'], product_data['uom_id'], product_data['price_per_unit'],
                product_data['available_quantity'], product_data['image_data'], product_data['manufacturer_name'],
                product_data['weight'], product_data['purchase_price'], product_data['discount_percentage'],
                product_data['voluminosity'], product_data['combinations'], product_data['nutritional_information'],
                product_data['expiration_date'], product_data['storage_conditions'], product_data['number_sold'],
                product_data['date_added_to_stock'], product_data['total_profit_on_sales'], product_data['error_rate_in_weight'],
                product_id )
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




if __name__=='__main__':
    connection = get_sql_connection()
    print(delete_product(connection, 4))