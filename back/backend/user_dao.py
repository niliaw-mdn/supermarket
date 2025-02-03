from back.sql_connection import get_sql_connection

#from werkzeug.security import generate_password_hash



# Helper Function: Fetch User by Email
def fetch_user_by_email(email):
    connection = get_sql_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    connection.close()
    return user

# Helper Function: Create New User
def create_user(email, password_hash, password_salt):
    connection = get_sql_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (email, password_hash, password_salt) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, password_hash, password_salt))
    connection.commit()
    connection.close()

# Helper Function: Delete User by ID
def delete_user_by_id(user_id):
    connection = get_sql_connection()
    cursor = connection.cursor()
    query = "DELETE FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    connection.commit()
    connection.close()

# Helper Function: Fetch All Users
def fetch_all_users():
    connection = get_sql_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT user_id, email FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users

# Helper Function: Fetch User by ID
def fetch_user_by_id(user_id):
    connection = get_sql_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT user_id, email FROM users WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user
