# main.py

import os
import sys

from auth import login_user, register_user
from utils import clear_screen
from db_connector import db

def pause():
    input("\nPress Enter to continue...")

def login():
    print("\nPlease select your role:")
    print("1. Customer")
    print("2. Employee")
    print("3. Supplier")
    
    role_choice = input("\nEnter your choice: ").strip()

    if role_choice == "1":
        login_user("customer")
    elif role_choice == "2":
        login_user("employee")
    elif role_choice == "3":
        login_user("supplier")
    else:
        print("\nInvalid choice.")
        pause()
    login_user(role_choice)
    return

def register():
    print("\nPlease select your role:")
    print("1. Customer")
    print("2. Employee")
    print("3. Supplier")
    
    role_choice = input("\nEnter your choice: ").strip()

    if role_choice == "1":
        register_user("customer")
    elif role_choice == "2":
        register_user("employee")
    elif role_choice == "3":
        register_user("supplier")
    else:
        print("\nInvalid choice.")
        pause()
    register_user(role_choice)
    return

def show_homepage():
    while True:
        clear_screen()
        print("=" * 50)
        print("         Hoang Whole Foods")
        print("=" * 50)
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            login()
        elif choice == "2":
            #register_user()
            pause()
        elif choice == "3":
            print("\nGoodbye.")
            db.close()
            sys.exit()
        else:
            print("\nInvalid choice.")
            pause()


if __name__ == "__main__":
    show_homepage()