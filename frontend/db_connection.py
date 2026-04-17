import mysql.connector
from mysql.connector import Error

def get_connection():
    """Return a fresh MySQL connection. Caller is responsible for closing it."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="HoangWholeFoods"
        )
        return conn
    except Error as e:
        raise RuntimeError(f"Database connection failed: {e}") from e