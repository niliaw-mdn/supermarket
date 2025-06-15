from functools import wraps
from flask import jsonify
import mysql
from db_connection import close_connection, get_db_connection


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


# Helper Function: Fetch User by Email
def fetch_user_by_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    connection.close()
    return user

# Helper Function: Create New User
def create_user(email, password_hash, password_salt):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "INSERT INTO user (email, password_hash, password_salt) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, password_hash, password_salt))
    connection.commit()
    connection.close()

# Helper Function: Delete User by ID
def delete_user_by_id(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "DELETE FROM user WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    connection.commit()
    connection.close()

# Helper Function: Fetch All Users
def fetch_all_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT user_id, email FROM user"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users

# Helper Function: Fetch User by ID
def fetch_user_by_id(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT user_id, email FROM user WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user
