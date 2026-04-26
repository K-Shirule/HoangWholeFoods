# SJSU CMPE 138 SPRING 2026 TEAM6
import sys

from auth import login_user, register_user
from utils import clear_screen, print_load
from db_connector import db
from logger_config import get_logger
import bcrypt

logger = get_logger(__name__)

def pause():
    input("\nPress Enter to continue...")

def login():
    print("\nPlease select your role:")
    print("1. Customer")
    print("2. Employee")
    print("3. Supplier")
    
    role_choice = input("\nEnter your choice: ").strip()
    clear_screen()
    if role_choice == "1":
        login_user("customer")
    elif role_choice == "2":
        login_user("employee")
    elif role_choice == "3":
        login_user("supplier")
    else:
        print("\nInvalid choice.")
        pause()
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
    return

def show_homepage():
    initial_data()
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
            clear_screen()
            login()
        elif choice == "2":
            clear_screen()
            register()
        elif choice == "3":
            print("\nGoodbye.")
            db.close()
            sys.exit()
        else:
            print("\nInvalid choice.")
            pause()

def initial_data():
    cursor = db.cursor(dictionary=True)

    try:
        #random stores data
        stores = [
            ('San Jose, CA', 'Downtown SJ', '4085551234', 'sj_downtown@hwf.com', '123 Market St', 'K7M3X9', 'T5R8Q2'),
            ('Santa Clara, CA', 'Santa Clara Central', '4085552345', 'sc_central@hwf.com', '456 El Camino Real', 'P9L4W6', 'H3V7Z8'),
            ('Sunnyvale, CA', 'Sunnyvale Plaza', '4085553456', 'sv_plaza@hwf.com', '789 Mathilda Ave', 'R6T2Y8', 'M4X9K3'),
            ('Cupertino, CA', 'Cupertino Square', '4085554567', 'cupertino@hwf.com', '101 Infinite Loop', 'Z8Q5N2', 'B7C3W6')
        ]

        for store in stores:
            location, branch_name, phone, email, address, store_pin, supplier_pin = store

            cursor.execute(
                "SELECT st_id FROM store WHERE email = %s LIMIT 1",
                (email,)
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    """
                    INSERT INTO store (
                        location, branch_name, phone, email, address, store_pin, supplier_pin
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (location, branch_name, phone, email, address, store_pin, supplier_pin)
                )

        db.commit()

        #managers
        managers = [
            (1, 'Jim', 'Halpert', 'jim.halpert@hwf.com', '4085551111', 75000, True, 'Jim@123'),
            (2, 'Bruce', 'Wayne', 'bruce.wayne@hwf.com', '4085552222', 76000, True, 'Bruce@123'),
            (3, 'Arry', 'Potta', 'arry.potta@hwf.com', '4085553333', 74000, True, 'Arry@123'),
            (4, 'Ishow', 'Speed', 'ishow.speed@hwf.com', '4085554444', 77000, True, 'Speed@123')
        ]

        for manager in managers:
            st_id, first_name, last_name, email, phone, salary, is_current, plain_password = manager

            cursor.execute(
                "SELECT e_id FROM employee WHERE email = %s LIMIT 1",
                (email,)
            )
            exists = cursor.fetchone()

            if not exists:
                hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


                cursor.execute(
                    """
                    INSERT INTO employee (
                        st_id, first_name, last_name, email, phone,
                        salary, is_current, password_hash, role, start_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'store_manager', CURDATE())
                    """,
                    (st_id, first_name, last_name, email, phone,
                     salary, is_current, hashed_password)
                )

        db.commit()

        logger.info("Initial stores and store managers seeded successfully.")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding failed: {e}")

    finally:
        cursor.close()
        
if __name__ == "__main__":
    show_homepage()