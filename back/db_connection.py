import mysql.connector
from mysql.connector import pooling
import os


config = {
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', '@liSamani4371'),
    "host": os.getenv('DB_HOST', '127.0.0.1'),
    "database": os.getenv('DB_NAME', 'grocery_store'),
    "pool_name": "grocery_store_pool",
    "pool_size": 20  
}


db_pool = mysql.connector.pooling.MySQLConnectionPool(**config)

def get_db_connection():
    """Get a connection from the pool."""
    return db_pool.get_connection()

def close_connection(connection):
    """Close a connection and return it to the pool."""
    if connection.is_connected():
        connection.close()


if __name__ == "__main__":
    try:

        connection = get_db_connection()
        print("Successfully connected to the database.")
        

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        print("You're connected to database:", database_name)
        
    except mysql.connector.Error as error:
        print("Error while connecting to the database:", error)
    
    finally:

        if 'connection' in locals():
            close_connection(connection)
            print("Connection closed.")
