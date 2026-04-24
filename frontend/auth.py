import time
import bcrypt
from db_connector import db
from logger_config import get_logger
from utils import clear_screen, print_load
import re

logger = get_logger(__name__)


def login_user(role):
    clear_screen()
    print("=== LOGIN ===")

    print("\nPlease enter your Username / Email: ")
    username = input().strip()

    print("\nPlease enter your Password: ")
    password = input().strip()

    print_load("Checking credentials", 1.2)

    if check_username(username, role):
        user_id = get_user_id(username, role)

        if check_password(username, password, role):
            print_load("Logging you in", 1)
            print("\nLogin successful.")
            time.sleep(1)
            clear_screen()

            if role == 'customer':
                from customer_page import customer_page
                customer_page(user_id)

            elif role == 'supplier':
                from supplier_page import supplier_page
                supplier_page(user_id)

            elif role == 'employee':
                employee_info = get_employee_info(username)

                if employee_info:
                    employee_id = employee_info["e_id"]
                    store_id = employee_info["st_id"]
                    employee_role = employee_info["role"]

                    if employee_role == "store_manager":
                        from store_manager_menu import store_manager_page
                        store_manager_page(store_id, employee_id)

                    elif employee_role == "inventory_manager":
                        from inventory_manager_menu import inventory_manager_menu
                        inventory_manager_menu(store_id, employee_id)

                    elif employee_role == "floor_employee":
                        from floor_employee_menu import floor_employee_page
                        floor_employee_page(store_id, employee_id)

                    elif employee_role == "delivery_associate":
                        from delivery_associate import delivery_associate_page
                        delivery_associate_page(store_id, employee_id)

                    else:
                        print("\nUnknown employee role.")
                        logger.warning(f"Employee '{username}' has unknown role '{employee_role}'.")
                else:
                    print("\nUnable to retrieve employee information.")
                    logger.warning(f"Employee '{username}' login succeeded but employee info lookup failed.")
                return
        else:
            print("\nIncorrect Login Credentials.")
            time.sleep(3)
            logger.warning(f"{role} '{username}' entered incorrect password.")
            return
    else:
        print("\nIncorrect Login Credentials.")
        time.sleep(3)
        logger.warning(f"{role} '{username}' - username not found in database.")
        return

def register_user(role):
    clear_screen()
    print("=== REGISTER ===")

    store_id = None
    employee_role = None
    cursor = db.cursor(dictionary=True)

    if role == "employee":
        print("Please enter the store pin provided by your store manager: ")
        store_pin = input().strip()

        print_load("Verifying store pin", 1)

        cursor.execute("""
                SELECT st_id
                FROM store
                WHERE store_pin = %s
                LIMIT 1
            """, (store_pin,))
        row = cursor.fetchone()

        if row:
            store_id = row["st_id"]
            print("\nStore pin accepted.")
        else:
            print("\nInvalid store pin.")
            logger.warning("Employee attempted to register with invalid store pin.")
            print_load("Returning to homepage", 2)
            cursor.close()
            return

        print("Please select your exact role:")
        print("1. Inventory Manager")
        print("2. Floor Employee")
        print("3. Delivery Associate")

        role_choice = input("\nEnter your choice: ").strip()

        role_map = {
            "1": "inventory_manager",
            "2": "floor_employee",
            "3": "delivery_associate",
        }

        if role_choice not in role_map:
            print("\nInvalid role selection.")
            cursor.close()
            return

        employee_role = role_map[role_choice]

    elif role == "supplier":
        print("Please enter the supplier pin provided by the store manager:")
        supplier_pin = input().strip()

        print_load("Verifying supplier pin", 1)

        cursor.execute("""
                SELECT st_id
                FROM store
                WHERE supplier_pin = %s
                LIMIT 1
            """, (supplier_pin,))
        row = cursor.fetchone()

        if row:
            print("\nSupplier pin accepted.")
        else:
            print("\nInvalid supplier pin.")
            logger.warning("Supplier attempted to register with invalid company pin.")
            cursor.close()
            return

    print("\nPlease enter your desired username / email: ")
    username = get_valid_email()

    print_load("Checking availability", 1)

    while check_username(username, role):
        print("\nUsername already exists. Please choose a different username.")
        logger.info(f"Attempted registration with existing username: '{username}'.")
        username = get_valid_email()

    print("\nPlease enter your desired password: ")
    password = input().strip()
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        print_load("Creating account", 1.4)

        if role == "employee":
            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()
            phone = get_valid_phone()
            
            cursor.execute(
                """
                INSERT INTO employee
                (st_id, first_name, last_name, email, phone, salary, is_current,
                 password_hash, role, start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
                """,
                (
                    store_id,
                    first_name,
                    last_name,
                    username,
                    phone if phone else None,
                    0.00,
                    True,
                    hashed,
                    employee_role
                )
            )

        elif role == "supplier":
            supplier_name = input("Enter supplier/company name: ").strip()
            phone = get_valid_phone()
            address = input("Enter address: ").strip()
            billing_term = input("Enter billing term (leave blank if none): ").strip()

            cursor.execute(
                """
                INSERT INTO supplier
                (supplier_name, email, address, password_hash, billing_term, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    supplier_name,
                    username,
                    address if address else None,
                    hashed,
                    billing_term if billing_term else None,
                    phone if phone else None
                )
            )

        else:
            first_name = input("Enter first name: ").strip()
            last_name = input("Enter last name: ").strip()
            phone = get_valid_phone()

            cursor.execute(
                """
                INSERT INTO customer
                (first_name, last_name, email, password_hash, phone, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (
                    first_name,
                    last_name,
                    username,
                    hashed,
                    phone if phone else None
                )
            )

        db.commit()
        new_id = cursor.lastrowid

        print_load("Finalizing", 0.8)
        print("\nRegistration successful. You may now log in with your new credentials.")
        logger.info(f"New {role} registered and given id: '{new_id}'.")
        time.sleep(3)
        clear_screen()
        return

    except Exception as e:
        db.rollback()
        print_load("Rolling back changes", 0.8)
        print("\nRegistration failed.")
        logger.error(f"Registration failed for {role} '{username}': {e}")

    finally:
        cursor.close()

def check_username(username, role):
    cursor = db.cursor(dictionary=True)

    try:
        if role == "employee":
            cursor.execute(
                "SELECT 1 FROM employee WHERE email = %s LIMIT 1",
                (username,)
            )
        elif role == "supplier":
            cursor.execute(
                "SELECT 1 FROM supplier WHERE email = %s LIMIT 1",
                (username,)
            )
        else:
            cursor.execute(
                "SELECT 1 FROM customer WHERE email = %s LIMIT 1",
                (username,)
            )

        result = cursor.fetchone()
        return result is not None

    finally:
        cursor.close()

def check_password(username, password, role):
    cursor = db.cursor(dictionary=True)

    try:
        if role == "employee":
            cursor.execute(
                "SELECT password_hash FROM employee WHERE email = %s",
                (username,)
            )
        elif role == "supplier":
            cursor.execute(
                "SELECT password_hash FROM supplier WHERE email = %s",
                (username,)
            )
        else:
            cursor.execute(
                "SELECT password_hash FROM customer WHERE email = %s",
                (username,)
            )

        result = cursor.fetchone()

        if not result:
            return False

        stored_hash = result["password_hash"]
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))

    finally:
        cursor.close()

def get_user_id(username, role):
    cursor = db.cursor(dictionary=True)

    try:
        if role == "employee":
            cursor.execute(
                "SELECT e_id FROM employee WHERE email = %s",
                (username,)
            )
            result = cursor.fetchone()
            return result["e_id"] if result else None

        elif role == "supplier":
            cursor.execute(
                "SELECT supplier_id FROM supplier WHERE email = %s",
                (username,)
            )
            result = cursor.fetchone()
            return result["supplier_id"] if result else None

        else:
            cursor.execute(
                "SELECT c_id FROM customer WHERE email = %s",
                (username,)
            )
            result = cursor.fetchone()
            return result["c_id"] if result else None

    finally:
        cursor.close()

def get_employee_info(username):
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT e_id, st_id, role
            FROM employee
            WHERE email = %s
            """,
            (username,)
        )
        return cursor.fetchone()

    finally:
        cursor.close()

def get_valid_email():
    while True:
        email = input("Enter email: ").strip().lower()

        # simple but solid email regex
        if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email):
            return email
        else:
            print("Invalid email format. Please try again.")

def get_valid_phone():
    while True:
        phone = input("Enter phone number (digits only): ").strip()

        if phone.isdigit() and len(phone) == 10:
            return phone
        else:
            print("Invalid phone number. Please enter digits only (0-9).")
            time.sleep(3)