import os
import MySQLdb
import jwt
from hashlib import pbkdf2_hmac
from sql_connection import get_sql_connection

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def validate_user_input( **kwargs):
    if len(kwargs["email"]) <= 255 and len(kwargs["password"]) <= 255:
        return True
    else:
        return False
        

def generate_salt():
    salt = os.urandom(16)
    return salt.hex()


def generate_hash(plain_password, password_salt):
    password_hash = pbkdf2_hmac(
        "sha256",
        b"%b" % bytes(plain_password, "utf-8"),
        b"%b" % bytes(password_salt, "utf-8"),
        10000,
    )
    return password_hash.hex()

def db_write(connection, query, params):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        cursor.close()

        return True

    except MySQLdb._exceptions.IntegrityError:
        cursor.close()
        return False
    
def db_read(connection, query, params):
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        entries = cursor.fetchall()
        cursor.close()

        content = []

        for entry in entries:
            content.append(entry)

        return content
    
    

def generate_jwt_token(content):
    encoded_content = jwt.encode(content, JWT_SECRET_KEY, algorithm="HS256")
    token = str(encoded_content).split("'")[1]
    
    
def validate_user(connection, email, password):
    current_user = db_read(connection, """SELECT * FROM grocery_store.user WHERE email = %s""", (email,))
    print(f"Current user: {current_user}")  # Debugging print

    if len(current_user) == 1:
        user = current_user[0]  # Assuming `current_user` is a list of tuples
        print(f"User tuple: {user}")  # Debugging print for the user tuple
        print(f"User tuple length: {len(user)}")  # Debugging print for the length of the user tuple

        # Verify indices
        if len(user) >= 4:
            
            saved_password_salt = user[2]  # Accessing password_salt
            saved_password_hash = user[3]  # Accessing password_hash
            password_hash = generate_hash(password, saved_password_salt)
            print(f"Generated password hash: {password_hash}")  # Debugging print
            print(f"Saved password hash: {saved_password_hash}")  # Debugging print

            if password_hash == saved_password_hash:
                user_id = user[0]  # Accessing id
                jwt_token = generate_jwt_token({"id": user_id})
                return jwt_token
            else:
                print("Password hash does not match")  # Debugging print
                return False
        else:
            print("User tuple does not have expected number of elements")  # Debugging print
            return False
    else:
        print("User not found or multiple entries found")  # Debugging print
        return False
