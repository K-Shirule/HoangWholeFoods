# SJSU CMPE 138 SPRING 2026 TEAM6
import time
import bcrypt

from auth import get_valid_phone, get_valid_email
from utils import clear_screen, print_load
from products_page import view_product_catalog, _fetch_all, _fetch_one
from logger_config import get_logger
from db_connector import db

logger = get_logger(__name__)

#customer landing function/page
def customer_page(customer_id):
    while True:
        clear_screen()
        print("Welcome to the Customer Page!")
        print("Here you can view products, place orders, and manage your account.")
        print("1. View Product Catalog")
        print("2. View Shopping Cart")
        print("3. View Order History")
        print("4. View/Update Account Information")
        print("5. Logout")
        choice = input("Please enter your choice (1-5): ")

        if choice == '1':
            selected_store = select_store()
            if selected_store is not None:
                view_product_catalog(customer_id, selected_store)

        elif choice == '2':
            view_shopping_cart(customer_id)

        elif choice == '3':
            view_order_history(customer_id)

        elif choice == '4':
            manage_account_information(customer_id)

        elif choice == '5':
            print_load("Logging out.", 2)
            logger.info(f"customer '{customer_id}' logged out successfully.")
            from homepage import show_homepage
            show_homepage()
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(3)

#helper functions - names suggest what each function does

def _print_store_list():
    stores = _fetch_all(
        """
        SELECT st_id, branch_name, location, address
        FROM store
        ORDER BY st_id
        """
    )

    if not stores:
        print("No stores are available right now.")
        return []

    print("\nAvailable Stores:")
    for store in stores:
        print(
            f"Store {store['st_id']}: {store['branch_name']} | "
            f"{store['location']} | {store['address']}"
        )
    return stores

def select_store():
    print("Please select the store you want to browse:")
    _print_store_list()

    store_id = input("Enter Store ID: ").strip()
    if not store_id.isdigit():
        print("Store ID must be numeric.")
        time.sleep(2)
        return None

    store = _fetch_one(
        """
        SELECT st_id, branch_name, location
        FROM store
        WHERE st_id = %s
        """,
        (int(store_id),),
    )

    if not store:
        print("That store does not exist.")
        time.sleep(2)
        return None

    print(
        f"Product Catalog for Store {store['st_id']} - "
        f"{store['branch_name']} ({store['location']})"
    )
    print("-----------------------------")
    return store["st_id"]

def get_or_create_cart(customer_id):
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT cart_id, st_id, cart_status
            FROM shopping_cart
            WHERE c_id = %s
            LIMIT 1
            """,
            (customer_id,)
        )
        cart = cursor.fetchone()

        if cart:
            return cart

        cursor.execute(
            """
            INSERT INTO shopping_cart (cart_status, c_id, st_id)
            VALUES ('new', %s, NULL)
            """,
            (customer_id,)
        )
        db.commit()

        return {
            "cart_id": cursor.lastrowid,
            "st_id": None,
            "cart_status": "new"
        }

    finally:
        cursor.close()

def reset_cart(cart_id):
    cursor = db.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM cart_contains
            WHERE cart_id = %s
            """,
            (cart_id,)
        )

        cursor.execute(
            """
            UPDATE shopping_cart
            SET st_id = NULL, cart_status = 'new'
            WHERE cart_id = %s
            """,
            (cart_id,)
        )

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset cart {cart_id}: {e}")

    finally:
        cursor.close()

def view_shopping_cart(customer_id):
    while True:
        clear_screen()

        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT cart.cart_id, cart.st_id, cc.prod_id, cc.quantity, "
            "prod.name, prod.description, prod.unit_price "
            "FROM shopping_cart AS cart "
            "JOIN cart_contains AS cc ON cart.cart_id = cc.cart_id "
            "JOIN product AS prod ON prod.prod_id = cc.prod_id "
            "WHERE cart.c_id = %s AND cart.cart_status = 'new'"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        cart_items = cursor.fetchall()
        cursor.close()

        if not cart_items:
            print_load("Cart is empty.", 1.5)
            return

        cart_id = cart_items[0]["cart_id"]
        store_id = cart_items[0]["st_id"]

        print(f"Your Cart (Store ID: {store_id})")
        print(
            f"| {'Product #':<10} "
            f"| {'Name':<15} "
            f"| {'Description':<40} "
            f"| {'Price':<10} "
            f"| {'Quantity':<10} |"
        )
        print("=" * 90)

        for row in cart_items:
            print(
                f"| {row['prod_id']:<10} "
                f"| {row['name']:<15} "
                f"| {row['description']:<40} "
                f"| ${row['unit_price']:<10} "
                f"| {row['quantity']:<10} |"
            )

        print("\n1. Proceed to Checkout")
        print("2. Remove an Item")
        print("3. Clear Cart")
        print("4. Return to Customer Page")
        choice = input("Please enter your choice (1-4): ")

        if choice == '1':
            checkout(customer_id, cart_id)
            return

        elif choice == '2':
            print("Please enter the product_id of the item you wish to remove: ")
            product_id = input().strip()

            print("Please enter the quantity of the item you wish to remove: ")
            quantity = input().strip()

            if not quantity.isdigit() or int(quantity) <= 0:
                print_load("Invalid quantity amount.", 2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT *
                FROM cart_contains
                WHERE cart_id = %s AND prod_id = %s
                """,
                (cart_id, product_id)
            )
            cc_row = cursor.fetchone()
            cursor.close()

            if not cc_row:
                print_load(f"Product with id ({product_id}) could not be found in cart.", 2)
                continue

            if int(quantity) > cc_row["quantity"]:
                print_load("Input quantity exceeds item quantity in cart.", 2)
                continue

            cursor = db.cursor(dictionary=True)

            if int(quantity) == cc_row["quantity"]:
                cursor.execute(
                    """
                    DELETE FROM cart_contains
                    WHERE cart_id = %s AND prod_id = %s
                    """,
                    (cart_id, product_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE cart_contains
                    SET quantity = quantity - %s
                    WHERE cart_id = %s AND prod_id = %s
                    """,
                    (quantity, cart_id, product_id)
                )

            db.commit()
            cursor.close()

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT 1
                FROM cart_contains
                WHERE cart_id = %s
                LIMIT 1
                """,
                (cart_id,)
            )
            still_has_items = cursor.fetchone()
            cursor.close()

            if not still_has_items:
                reset_cart(cart_id)

            print_load(f"Removing {quantity} items from cart.", 2)

        elif choice == '3':
            reset_cart(cart_id)
            print_load("Clearing cart.", 2)

        elif choice == '4':
            return

        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def view_order_history(customer_id):
    while True:
        clear_screen()

        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT o.* "
            "FROM orders AS o "
            "WHERE o.c_id = %s "
            "ORDER BY o.order_date ASC"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        order_history = cursor.fetchall()
        cursor.close()

        if not order_history:
            print_load("No orders have been made.", 1.5)
            return

        print(
            f"| {'Order #':<7} "
            f"| {'Date':<19} "
            f"| {'Delivery Method':<20} "
            f"| {'Order Type':<20} "
            f"| {'Status':<20} "
            f"| {'Total':<15} | "
        )
        print('=' * 120)
        for row in order_history:
            print(
                f"| {row['order_id']:<7} "
                f"| {row['order_date']} "
                f"| {row['delivery_method']:<20} "
                f"| {row['order_type']:<20} "
                f"| {row['order_status']:<20} "
                f"| ${row['total_amount']:<14} |"
            )

        print("\nTo view details of a specific order, enter the order ID.")
        print("To return to the Customer Page, type 'back'")
        choice = input("Please enter your choice: ")
        if choice.lower() == 'back':
            return
        elif choice.isdigit():
            order_id = choice

            order_found = False
            for row in order_history:
                if int(order_id) == row['order_id']:
                    order_found = True

            if not order_found:
                print_load("Invalid Order ID.", 2)
                continue

            view_order(order_id, customer_id)
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)
            return

def manage_account_information(customer_id):
    while True:
        clear_screen()

        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT c.* "
            "FROM customer AS c "
            "WHERE c.c_id = %s"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        customer_info = cursor.fetchone()

        if not customer_info:
            print("Error retrieving account information.")
            print_load("Returning.", 1.5)
            cursor.close()
            return

        print("[ Account Info ]")
        print(
            f" {'=' * 60}"
            f"\n| {'Name':<15} | {customer_info['first_name'] + ' ' + customer_info['last_name']:<40} |"
            f"\n| {'Phone':<15} | {customer_info['phone']:<40} |"
            f"\n| {'Email':<15} | {customer_info['email']:<40} |"
            f"\n| {'Member Since':<15} | {str(customer_info['created_at'])[:10]:<40} |"
            f"\n {'=' * 60}"
        )
        cursor.close()

        print("\n1. Change First Name")
        print("2. Change Last Name")
        print("3. Change Phone Number")
        print("4. Change Email")
        print("5. Change Password")
        print("6. Return to Customer Page")
        choice = input("Please enter your choice (1-6): ")

        if choice == '1':
            print("Please enter your new first name: ")
            new_first_name = input().strip()

            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c "
                "SET c.first_name = %s "
                "WHERE c.c_id = %s"
            )
            args = (new_first_name, customer_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            print_load("Updating first name.", 2)
            logger.info(f"Customer '{customer_id}' updated their first name.")

        elif choice == '2':
            print("Please enter your new last name: ")
            new_last_name = input().strip()

            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c "
                "SET c.last_name = %s "
                "WHERE c.c_id = %s"
            )
            args = (new_last_name, customer_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            print_load("Updating last name.", 2)
            logger.info(f"Customer '{customer_id}' updated their last name.")

        elif choice == '3':
            print("Please enter your new phone number: ")
            new_phone_number = get_valid_phone()

            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c "
                "SET c.phone = %s "
                "WHERE c.c_id = %s"
            )
            args = (new_phone_number, customer_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            print_load("Updating phone number.", 2)
            logger.info(f"Customer '{customer_id}' updated their phone number.")

        elif choice == '4':
            print("Please enter your new email: ")
            new_email = get_valid_email()

            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c "
                "SET c.email = %s "
                "WHERE c.c_id = %s"
            )
            args = (new_email, customer_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            print_load("Updating email.", 2)
            logger.info(f"Customer '{customer_id}' updated their email.")

        elif choice == '5':
            print("Please enter your new password: ")
            new_password = input().strip()

            print("Please re-enter new password: ")
            if input().strip() != new_password:
                print_load("Passwords do not match!\nReturning.", 2)
                continue

            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c "
                "SET c.password_hash = %s "
                "WHERE c.c_id = %s"
            )
            args = (hashed, customer_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            print_load("Updating password.", 2)
            logger.info(f"Customer '{customer_id}' updated their password.")

        elif choice == '6':
            return

        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def view_order(order_id, customer_id):
    while True:
        clear_screen()

        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT * "
            "FROM orders AS o JOIN order_contains AS oc JOIN product AS p "
            "   ON o.order_id = oc.order_id AND oc.prod_id = p.prod_id "
            "WHERE oc.order_id = %s"
        )
        args = (order_id,)
        cursor.execute(query, args)
        order_items = cursor.fetchall()
        cursor.close()

        if not order_items:
            print(f"Invalid order ID ({order_id}).")
            print_load("Returning.", 1.5)
            return

        order_status = order_items[0]['order_status']

        print(f"Order #{order_id}: ")
        print(f"Status: {order_status}")
        print(
            f"| {'Product #':<10} "
            f"| {'Name':<20} "
            f"| {'Description':<50} "
            f"| {'Price':<15} "
            f"| {'Quantity':<10} |"
        )
        print('=' * 121)

        for row in order_items:
            print(
                f"| {row['prod_id']:<10} "
                f"| {row['name']:<20} "
                f"| {row['description']:<50} "
                f"| ${row['unit_price']:<14} "
                f"| {row['quantity']:<10} |"
            )

        print(f"\n> Total: ${row['total_amount']}")

        print("\n1. Return an Item")
        print("2. Leave review for an item")
        print("3. Return to Order History")
        choice = input("Please enter your choice (1-3): ")

        if choice == '1':
            if order_status != 'fulfilled':
                print_load("Items can only be returned after the order is fulfilled.", 2)
                continue

            print("Please enter the product_id of the item you wish to return: ")
            product_id = input().strip()

            print("Enter quantity to return: ")
            return_quantity = input().strip()

            if not return_quantity.isdigit() or int(return_quantity) <= 0:
                print_load("Invalid quantity.", 2)
                continue

            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT * "
                "FROM orders AS o JOIN order_contains AS oc "
                "   ON o.order_id = oc.order_id "
                "WHERE oc.order_id = %s AND oc.prod_id = %s"
            )
            args = (order_id, product_id)
            cursor.execute(query, args)
            prod_in_order = cursor.fetchone()
            cursor.close()

            if not prod_in_order:
                print_load(f"Product with id ({product_id}) could not be found in order.", 2)
                continue

            if int(return_quantity) > prod_in_order['quantity']:
                print_load("Input quantity exceeds item quantity in order.", 2)
                continue

            print("Enter reason for return: ")
            return_reason = input().strip()

            cursor = db.cursor(dictionary=True)
            query = (
                "INSERT INTO return_record("
                "   order_id,"
                "   prod_id,"
                "   return_quantity,"
                "   return_reason,"
                "   processed_by_employee_id"
                ") VALUES(%s, %s, %s, %s, NULL)"
            )
            args = (order_id, product_id, return_quantity, return_reason)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            logger.info(f"Customer '{customer_id}' initiated a return for product '{product_id}' in order '{order_id}'.")
            print_load("Item return initiated. A floor employee will either approve or deny your return request within the next 24-48 hours.", 3)

        elif choice == '2':
            if order_status != 'fulfilled':
                print_load("You can only leave a review after the order is fulfilled.", 2)
                continue

            print("Please enter the product_id of the item you wish to review: ")
            product_id = input().strip()

            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT * "
                "FROM orders AS o JOIN order_contains AS oc "
                "   ON o.order_id = oc.order_id "
                "WHERE oc.order_id = %s AND oc.prod_id = %s"
            )
            args = (order_id, product_id)
            cursor.execute(query, args)
            prod_in_order = cursor.fetchone()
            cursor.close()

            if not prod_in_order:
                print_load(f"Product with id ({product_id}) could not be found in order.", 2)
                continue

            print("Please enter your rating for the product (1-5): ")
            rating = input().strip()
            while not rating.isdigit() or not (1 <= int(rating) <= 5):
                print("Invalid rating. Please enter a number between 1 and 5.")
                rating = input().strip()

            print("Please leave any additional comments: ")
            comments = input().strip()
            while len(comments) > 255:
                print("Comments cannot exceed 255 characters. Please try again.")
                comments = input().strip()

            cursor = db.cursor(dictionary=True)
            query = (
                "INSERT INTO review("
                "   rating,"
                "   r_comment,"
                "   c_id,"
                "   prod_id"
                ") VALUES(%s, %s, %s, %s)"
            )
            args = (rating, comments, customer_id, product_id)
            cursor.execute(query, args)
            db.commit()
            cursor.close()

            logger.info(f"Customer '{customer_id}' left a review for product '{product_id}'.")
            print("Thank you for leaving a review!")
            print_load("Returning.", 2)

        elif choice == '3':
            view_order_history(customer_id)
            return

        else:
            print_load("Invalid choice.", 2)

def checkout(customer_id, cart_id):
    delivery_method = None
    delivery_address = 'In-Store'
    payment_method = None

    while True:
        clear_screen()
        print("Checkout")
        print("-----------------------------")
        print("Please select how you would like to receive your order.")
        print("1. In Store Pickup")
        print("2. Delivery")
        choice = input("Please enter your choice (1-2): ").strip()

        if choice == '1':
            delivery_method = 'Pickup'
            delivery_address = 'In-Store'
            break
        elif choice == '2':
            delivery_method = 'Delivery'
            delivery_address = input("Please enter your delivery address: ").strip()
            if not delivery_address:
                print("Delivery address cannot be empty.")
                time.sleep(2)
                continue
            break
        else:
            print_load("Invalid choice.", 1.5)

    while True:
        clear_screen()
        print("Payment")
        print("-----------------------------")
        print("Payment is processed through a secure third-party provider.")
        print("1. Credit/Debit Card")
        print("2. Cash")
        print("3. Mobile Wallet")
        payment_choice = input("Please enter your choice (1-3): ").strip()

        if payment_choice == '1':
            payment_method = 'Card'
            break
        elif payment_choice == '2':
            payment_method = 'Cash'
            break
        elif payment_choice == '3':
            payment_method = 'Mobile Wallet'
            break
        else:
            print_load("Invalid choice.", 1.5)

    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT st_id
            FROM shopping_cart
            WHERE cart_id = %s
            """,
            (cart_id,)
        )
        cart_row = cursor.fetchone()

        if not cart_row or cart_row["st_id"] is None:
            print_load("Cart is not assigned to a store.", 2)
            return

        store_id = cart_row["st_id"]

        cursor.execute(
            """
            SELECT cc.prod_id, cc.quantity, p.unit_price, p.name
            FROM cart_contains AS cc
            JOIN product AS p ON cc.prod_id = p.prod_id
            WHERE cc.cart_id = %s
            """,
            (cart_id,)
        )
        cart_items = cursor.fetchall()

        if not cart_items:
            print_load("Cart is empty.", 2)
            return

        total = 0
        for item in cart_items:
            total += float(item["unit_price"]) * float(item["quantity"])

        print_load("Processing payment", 1.5)

        payment_status = 'paid'

        cursor.execute(
            """
            SELECT cc.prod_id, cc.quantity, p.unit_price, p.name
            FROM cart_contains AS cc
            JOIN product AS p ON cc.prod_id = p.prod_id
            WHERE cc.cart_id = %s
            """,
            (cart_id,)
        )
        cart_items = cursor.fetchall()

        if not cart_items:
            db.rollback()
            print_load("Cart is empty.", 2)
            return

        for item in cart_items:
            cursor.execute(
                """
                UPDATE stocks
                SET quantity = quantity - %s
                WHERE store_id = %s
                  AND prod_id = %s
                  AND quantity >= %s
                """,
                (item["quantity"], store_id, item["prod_id"], item["quantity"])
            )

            if cursor.rowcount == 0:
                db.rollback()
                print(
                    f"Checkout failed: '{item['name']}' is no longer available "
                    f"in the requested quantity."
                )
                print_load("Please update your cart and try again.", 2.5)
                return

        total = 0
        for item in cart_items:
            total += float(item["unit_price"]) * float(item["quantity"])

        cursor.execute(
            """
            INSERT INTO orders(
                delivery_method, total_amount, order_type, order_status, c_id, st_id, e_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, NULL)
            """,
            (delivery_method, total, 'Online', 'placed', customer_id, store_id)
        )
        order_id = cursor.lastrowid

        order_contains_args = [
            (order_id, item["prod_id"], item["quantity"], item["unit_price"])
            for item in cart_items
        ]

        cursor.executemany(
            """
            INSERT INTO order_contains(
                order_id, prod_id, quantity, price_at_purchase
            )
            VALUES (%s, %s, %s, %s)
            """,
            order_contains_args
        )

        cursor.execute(
            """
            INSERT INTO payments(
                method, amount, payment_status, order_id, return_id
            )
            VALUES (%s, %s, %s, %s, NULL)
            """,
            (payment_method, total, payment_status, order_id)
        )

        cursor.execute(
            """
            INSERT INTO delivery_record(
                delivered_at, delivered_to, delivery_status, order_id, e_id
            )
            VALUES (NULL, %s, 'pending', %s, NULL)
            """,
            (delivery_address, order_id)
        )

        cursor.execute(
            """
            DELETE FROM cart_contains
            WHERE cart_id = %s
            """,
            (cart_id,)
        )

        cursor.execute(
            """
            UPDATE shopping_cart
            SET st_id = NULL, cart_status = 'new'
            WHERE cart_id = %s
            """,
            (cart_id,)
        )

        db.commit()

        logger.info(f"Customer '{customer_id}' completed checkout for cart '{cart_id}'.")

        print("\nOrder placed successfully!")
        print(f"Your order ID is: {order_id}")
        print("1. View Order Details")
        print("2. Return to Customer Page")
        choice = input("Please enter your choice (1-2): ").strip()

        if choice == '1':
            view_order(order_id, customer_id)
        return

    except Exception as e:
        db.rollback()
        logger.error(f"Checkout failed for customer '{customer_id}', cart '{cart_id}': {e}")
        print("Checkout failed.")
        time.sleep(2)

    finally:
        cursor.close()
if __name__ == '__main__':
    customer = input("Enter customer ID to test: ").strip()
    customer_page(customer)