from sql_connection import get_sql_connection

def get_all_products(connection):
    cursor = connection.cursor()
    query = "SELECT  product.product_id, product.name, product.uom_id, product.price_per_unit, product.available_quantity, uom.uom_name FROM grocery_store.product inner join uom on product.uom_id=uom.uom_id;"
    cursor.execute(query)
    response = []
    for (product_id, name, uom_id, price_per_unit, available_quantity, uom_name) in cursor:
        response.append(
            {    
                'product_id' : product_id,
                'name' : name,
                'uom_id' : uom_id,
                'price_per_unit' : price_per_unit,
                'uom_name' : uom_name,
                'available_quantity' : available_quantity
            }   
        )        
    return response


#product arg is a dictionary of a product
def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = ("insert into product (name, uom_id, price_per_unit, available_quantity) values (%s, %s, %s, %s)")
    data = (product['product_name'], product['uom_id'], product['price_per_unit'], product['available_quantity'])
    cursor.execute(query, data)
    connection.commit()
    
    return cursor.lastrowid
    
    
def delete_product(connection, product_id):
    # sourcery skip: use-fstring-for-concatenation
    cursor = connection.cursor()
    query = ("DELETE FROM product where product_id=" + str(product_id))
    cursor.execute(query)
    connection.commit()
    
    
def update_product(connection, product_id, amount):
    cursor = connection.cursor()
    query = ("UPDATE product SET available_quantity = available_quantity" + [amount] + " WHERE product_id= " + str([product_id]) )
    cursor.execute(query)
    connection.commit()
    
    
    

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