import mysql.connector

conn = mysql.connector.connect(
    host="localhost:303",
    user="root",
    password="",
    database="HoangWholeFoods"
)

cursor = conn.cursor(dictionary=True)