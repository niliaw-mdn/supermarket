
def get_category(connection):
    cursor = connection.cursor()
    query = ("SELECT * from category")
    cursor.execute(query)
    
    response = []
    for (category_id, category_name) in cursor:
        response.append({
            'category_id': category_id,
            'category_name': category_name
        })
    return response


if __name__ == '__main__':
    from sql_connection import get_sql_connection
    
    connection = get_sql_connection()
    print(get_category(connection))