import mysql.connector as MySQL

password: str = 'Thewumpus17!' # Set db server password here

db = MySQL.connect(
    host='localhost',
    user='root',
    password=password,
    database='hoangwholefoods'
)