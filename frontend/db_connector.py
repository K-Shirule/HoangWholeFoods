# SJSU CMPE 138 SPRING 2026 TEAM6
import mysql.connector as MySQL

password: str = 'Thewumpus17!' # Set db server password here

db = MySQL.connect(
    host='localhost',
    user='admin',
    password='1234',
    database='hoangwholefoods'
)