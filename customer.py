import os
import sys
import mysql.connector as MySQL

from classes import CartStatus, Rating, Customer


def view_categories(db):
    print()


def browse_category(db):
    print()


def view_cart(db, customer_id: int):
    print()


def add_to_cart(db, customer_id: int, product_id: int, quantity: int) -> int:
    return 0


def remove_from_cart(db, customer_id: int, product_id: int, quantity: int = None) -> int:
    return 0


def add_review(db, customer_id: int, product_id: int, rating: Rating, comment: str) -> int:
    return 0


def view_reviews(db, product_id: int) -> int:
    return 0


def show_customer_page():

    sql_pass = input("Enter password: ").strip()
    
    db = MySQL.connect(
        host = "localhost",
        user = "root",
        password = sql_pass,
        database = "hoangwholefoods"
    )




if __name__ == "__main__":
    show_customer_page()