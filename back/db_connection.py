import mysql.connector
from mysql.connector import pooling
import os

# Database configuration
config = {
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', '@liSamani4371'),
    "host": os.getenv('DB_HOST', '127.0.0.1'),
    "database": os.getenv('DB_NAME', 'grocery_store'),
    "pool_name": "grocery_store_pool",
    "pool_size": 20  # Add pool size here
}

# Create connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(**config)

def get_db_connection():
    """Get a connection from the pool."""
    return db_pool.get_connection()

def close_connection(connection):
    """Close a connection and return it to the pool."""
    if connection.is_connected():
        connection.close()

# Example usage
if __name__ == "__main__":
    try:
        # Get a connection from the pool
        connection = get_db_connection()
        print("Successfully connected to the database.")
        
        # Perform some database operations
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        print("You're connected to database:", database_name)
        
    except mysql.connector.Error as error:
        print("Error while connecting to the database:", error)
    
    finally:
        # Close the connection
        if 'connection' in locals():
            close_connection(connection)
            print("Connection closed.")
