import time
import bcrypt

from frontend.auth import check_username
from frontend.utils import clear_screen, print_load
from frontend.product_page import view_product_catalog
from frontend.logger_config import get_logger
from frontend.db_connector import db

logger = get_logger(__name__)

def customer_page(customer_id, store_id):
    while(True):
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
            view_product_catalog(customer_id)
        elif choice == '2':
            view_shopping_cart(customer_id, store_id)
        elif choice == '3':
            view_order_history(customer_id)
        elif choice == '4':
            manage_account_information(customer_id)
        elif choice == '5':
            print_load("Logging out.", 2)
            logger.info(f"customer '{customer_id}' logged out successfully.")
            from frontend.homepage import show_homepage
            show_homepage()
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(3)


def view_shopping_cart(customer_id, store_id):

    while(True):
        clear_screen()

        # Get shopping carts with 'new' status
        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT * " \
            "FROM shopping_cart AS cart JOIN cart_contains AS cc JOIN product AS prod " \
            "  ON cart.cart_id = cc.cart_id AND prod.prod_id = cc.prod_id " \
            "WHERE cart.cart_status = 'new' AND cart.c_id = %s"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        cart_items = cursor.fetchall()

        cursor.close()

        # Check if cart is empty
        if not cart_items:
            print_load("Cart is empty.", 1.5)
            return
        
        cart_id = cart_items[0]['cart_id'] # All rows should have same id

        print("Your Cart: ")
        print(
            f"| {'Product #':<10} " \
            f"| {'Name':<20} " \
            f"| {'Description':<50} " \
            f"| {'Price':<15} " \
            f"| {'Quantity':<10} |"
        )
        print("=" * 121)
        for row in cart_items:
            print(
                f"| {row['prod_id']:<10} " \
                f"| {row['name']:<20} " \
                f"| {row['description']:<50} " \
                f"| ${row['unit_price']:<14} " \
                f"| {row['quantity']:<10} |"
            )

        print("\n1. Proceed to Checkout")
        print("2. Remove an Item")
        print("3. Return to Customer Page")
        choice = input("Please enter your choice (1-3): ")
        if choice == '1':
            checkout(customer_id, cart_id, store_id)
            return
        elif choice == '2':
            print("Please enter the product_id of the item you wish to remove: ")
            product_id = input().strip()
            print("Please enter the quantity of the item you wish to remove: ")
            quantity = input().strip()

            if int(quantity) < 0:
                print_load("Invalid quantity amount.", 2)
                continue

            # Get desired product
            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT cc.* " \
                "FROM cart_contains AS cc " \
                "WHERE cc.cart_id = %s AND cc.prod_id = %s"
            )
            args = (cart_id, product_id,)
            cursor.execute(query, args)
            cc_row = cursor.fetchone()
            cursor.close()

            # Check that product exists in cart
            if not cc_row:
                print_load(f"Product with id ({product_id}) could not be found in cart.", 2)
                continue

            # Ensure input quantity is not more than what exists in cart
            if int(quantity) > cc_row['quantity']:
                print_load(f"Input quantity exceeds item quantity in cart.", 2)
                continue

            # If input quantity matches product quantity, delete db entry
            if int(quantity) == cc_row['quantity']:
                cursor = db.cursor(dictionary=True)
                query = (
                    "DELETE cc.* " \
                    "FROM cart_contains AS cc " \
                    "WHERE cc.cart_id = %s AND cc.prod_id = %s"
                )
                args = (cart_id, product_id,)
                cursor.execute(query, args)
                db.commit()

                # print(f"Deleted {cursor.rowcount} record(s).") # Debug check: Only 1 row should be deleted
                cursor.close()

            # If input quantity less than product quantity, modify entry quantity attribute
            if int(quantity) < cc_row['quantity']:
                cursor = db.cursor(dictionary=True)
                query = (
                    "UPDATE cart_contains AS cc " \
                    "SET cc.quantity = cc.quantity - %s " \
                    "WHERE cc.cart_id = %s AND cc.prod_id = %s"
                )
                args = (quantity, cart_id, product_id,)
                cursor.execute(query, args)
                db.commit()

                # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected
                cursor.close()

            print_load(f"Removing {quantity} items from cart.", 2)

        elif choice == '3':
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def view_order_history(customer_id):
    print("Viewing order history...")
    #sql query to view order history using the customer_id variable passed as paramter.
    
    #in case query returns null: print("You have no past orders.")
    while(True):
        clear_screen()

        # Get order history
        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT o.* " \
            "FROM orders AS o " \
            "WHERE o.c_id = %s " \
            "ORDER BY o.order_date ASC"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        order_history = cursor.fetchall()

        cursor.close()

        # Check if history is empty
        if not order_history:
            print_load("No orders have been made.", 1.5)
            return

        print(
            f"| {'Order #':<7} " \
            f"| {'Date':<19} " \
            f"| {'Delivery Method':<20} " \
            f"| {'Order Type':<20} " \
            f"| {'Status':<20} " \
            f"| {'Total':<15} | "
        )
        print('=' * 120)
        for row in order_history:
            print(
                f"| {row['order_id']:<7} " \
                f"| {row['order_date']} " \
                f"| {row['delivery_method']:<20} " \
                f"| {row['order_type']:<20} " \
                f"| {row['order_status']:<20} " \
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
    print("Viewing account information...")

    #sql query to view account information using the customer_id variable passed as paramter.
    #probably have a for loop here that displays all the appropriate entries of account info like first name, phone etc so user can change
    while(True):
        clear_screen()

        # Get customer account info
        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT c.* " \
            "FROM customer AS c " \
            "WHERE c.c_id = %s"
        )
        args = (customer_id,)
        cursor.execute(query, args)
        customer_info = cursor.fetchone()

        # Ensure customer info exists (should always be the case)
        if not customer_info:
            print("Error retrieving account information.")
            print_load("Returning.", 1.5)

        print("[ Account Info ]")
        print(
            f" {'=' * 60}"
            f"\n| {'Name':<15} | {customer_info['first_name'] + ' ' + customer_info['last_name']:<40} |" \
            f"\n| {'Phone':<15} | {customer_info['phone']:<40} |" \
            f"\n| {'Email':<15} | {customer_info['email']:<40} |" \
            f"\n| {'Member Since':<15} | {str(customer_info['created_at'])[:10]:<40} |" \
            f"\n {'=' * 60}"
        )

        print("\n1. Change First Name")
        print("2. Change Last Name")
        print("3. Change Phone Number")
        print("4. Change Email")
        print("5. Change Password")
        print("6. Return to Customer Page")
        choice = input("Please enter your choice (1-7): ")
        if choice == '1':
            print("Please enter your new first name: ")
            new_first_name = input().strip()

            #query to update first name in database
            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c " \
                "SET c.first_name = %s " \
                "WHERE c.c_id = %s"
            )
            args = (new_first_name, customer_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected 
            cursor.close()

            print_load("Updating first name.", 2)
            logger.info(f"Customer '{customer_id}' updated their first name.")
        elif choice == '2':
            print("Please enter your new last name: ")
            new_last_name = input().strip()

            #query to update last name in database
            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c " \
                "SET c.last_name = %s " \
                "WHERE c.c_id = %s"
            )
            args = (new_last_name, customer_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected 
            cursor.close()

            print_load("Updating last name.", 2)
            logger.info(f"Customer '{customer_id}' updated their last name.")
        elif choice == '3':
            print("Please enter your new phone number: ")
            new_phone_number = input().strip()

            #query to update phone number in database
            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c " \
                "SET c.phone = %s " \
                "WHERE c.c_id = %s"
            )
            args = (new_phone_number, customer_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected 
            cursor.close()

            print_load("Updating phone number.", 2)
            logger.info(f"Customer '{customer_id}' updated their phone number.")
        elif choice == '5':

            print("Please enter your new password: ")
            new_password = input().strip()

            print("Please re-enter new password: ")
            if (input().strip() != new_password):
                print_load("Passwords do not match!\nReturning.")
                continue

            encoded_pass = bytes(new_password.encode('utf-8'))
            hashed = bcrypt.hashpw(encoded_pass, bcrypt.gensalt())

            #query to update password in database
            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c " \
                "SET c.password_hash = %s " \
                "WHERE c.c_id = %s"
            )
            args = (hashed, customer_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected 
            cursor.close()

            print_load("Updating password.", 2)
            logger.info(f"Customer '{customer_id}' updated their password.")
        elif choice == '4':
            print("Please enter your new email: ")
            new_email = input().strip()
            check_username(new_email, "customer")

            #query to update email in database
            cursor = db.cursor(dictionary=True)
            query = (
                "UPDATE customer AS c " \
                "SET c.email = %s " \
                "WHERE c.c_id = %s"
            )
            args = (new_email, customer_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be affected 
            cursor.close()

            print_load("Updating email.", 2)
            logger.info(f"Customer '{customer_id}' updated their email.")
        elif choice == '6':
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def view_order(order_id, customer_id):
    #sql query to view order details using the order_id variable passed as paramter.
    while(True):
        clear_screen()

        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT * " \
            "FROM orders AS o JOIN order_contains AS oc JOIN product AS p " \
            "   ON o.order_id = oc.order_id AND oc.prod_id = p.prod_id " \
            "WHERE oc.order_id = %s"
        )
        args = (order_id,)
        cursor.execute(query, args)
        order_items = cursor.fetchall()

        cursor.close()

        # Check that order exists
        if not order_items:
            print(f"Invalid order ID ({order_id}).")
            print_load("Returning.", 1.5)
            return

        print(f"Order #{order_id}: ")
        print(
            f"| {'Product #':<10} " \
            f"| {'Name':<20} " \
            f"| {'Description':<50} " \
            f"| {'Price':<15} " \
            f"| {'Quantity':<10} |"
        )
        print('=' * 121)
        for row in order_items:
            print(
                f"| {row['prod_id']:<10} " \
                f"| {row['name']:<20} " \
                f"| {row['description']:<50} " \
                f"| ${row['unit_price']:<14} " \
                f"| {row['quantity']:<10} |"
            )

        print(f"\n> Total: ${row['total_amount']}")

        print("\n1. Return an Item")
        print("2. Leave review for an item")
        print("3. Return to Order History")
        choice = input("Please enter your choice (1-3): ")
        if choice == '1':
            print("Please enter the product_id of the item you wish to return: ")
            product_id = input().strip()

            print("Enter quantity to return: ")
            return_quantity = input().strip()

            if int(return_quantity) < 0:
                print_load("Invalid quantity.", 2)
                continue

            # Get desired product
            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT * " \
                "FROM orders AS o JOIN order_contains AS oc " \
                "   ON o.order_id = oc.order_id " \
                "WHERE oc.order_id = %s AND oc.prod_id = %s"
            )
            args = (order_id, product_id,)
            cursor.execute(query, args)
            prod_in_order = cursor.fetchone()
            cursor.close()

            # Check that product exists in order
            if not prod_in_order:
                print_load(f"Product with id ({product_id}) could not be found in order.", 2)
                continue

            # Ensure input quantity is not more than what exists in order
            if int(return_quantity) > prod_in_order['quantity']:
                print_load(f"Input quantity exceeds item quantity in order.", 2)
                continue

            print("Enter reason for return: ")
            return_reason = input().strip()

            # Create return order for employees to view
            cursor = db.cursor(dictionary=True)
            query = (
                "INSERT INTO return_record(" \
                "   order_id," \
                "   prod_id," \
                "   return_quantity," \
                "   return_reason," \
                "   processed_by_employee_id" \
                ") VALUES(%s, %s, %s, %s, NULL)"
            )
            args = (order_id, product_id, return_quantity, return_reason,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Inserted {cursor.rowcount} record(s).") # Debug check. Only 1 row should be inserted
            cursor.close()

            logger.info(f"Customer '{customer_id}' initiated a return for product '{product_id}' in order '{order_id}'.")
            print_load("Item return initiated. A floor employee will either approve or deny your return request within the next 24-48 hours.", 3)
        elif choice == '2':
            print("Please enter the product_id of the item you wish to review: ")
            product_id = input().strip()

            # Get desired product
            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT * " \
                "FROM orders AS o JOIN order_contains AS oc " \
                "   ON o.order_id = oc.order_id " \
                "WHERE oc.order_id = %s AND oc.prod_id = %s"
            )
            args = (order_id, product_id,)
            cursor.execute(query, args)
            prod_in_order = cursor.fetchone()
            cursor.close()

            # Check that product exists in order
            if not prod_in_order:
                print_load(f"Product with id ({product_id}) could not be found in order.", 2)
                continue

            print("Please enter your rating for the product (1-5): ")
            #make sure rating is an integer between 1 and 5
            rating = input().strip()
            while not rating.isdigit() or not (1 <= int(rating) <= 5):
                print("Invalid rating. Please enter a number between 1 and 5.")
                rating = input().strip()
            print("Please leave any additional comments: ")
            comments = input().strip()
            while len(comments) > 255:
                print("Comments cannot exceed 255 characters. Please try again.")
                comments = input().strip()
            #add the review to the reviews table in the database using the product_id, customer_id, review, and rating variables passed as parameters.

            cursor = db.cursor(dictionary=True)
            query = (
                "INSERT INTO review(" \
                "   rating," \
                "   r_comment," \
                "   c_id," \
                "   prod_id" \
                ") VALUES(%s, %s, %s, %s)"
            )
            args = (rating, comments, customer_id, product_id,)
            cursor.execute(query, args)
            db.commit()

            # print(f"Inserted {cursor.rowcount} record(s).") # Debug check. Only 1 row should be inserted
            cursor.close()

            logger.info(f"Customer '{customer_id}' left a review for product '{product_id}' .")
            print("Thank you for leaving a review!")
            print_load("Returning.", 2)
        elif choice == '3':
            view_order_history(customer_id)
            return
        else:
            print_load("Invalid choice.", 2)

def checkout(customer_id, cart_id, store_id):
    #sql query to checkout using the customer_id and cart_id variables passed as paramter.
    #after successful checkout, generate order_id variable to pass as parameter in view_order function

    delivery_method = 'N/A'
    delivery_address = 'In-Store'

    while(True):
        clear_screen()
        print("Please select if you would like to pick up your order in store or have it delivered.")
        print("1. In Store Pickup")
        print("2. Delivery")
        choice = input("Please enter your choice (1-2): ")
        if choice == '1':
            delivery_method = 'Pickup'
            print("You have selected in store pickup. Please proceed to the pickup counter and pay when you arrive at the store.")
        elif choice == '2':
            delivery_method = 'Delivery'
            print("You have selected delivery. Please enter your delivery address: ")
            delivery_address = input().strip()
            print("Your order will be delivered to the provided address within the next 3-5 business days.")
        else:
            print_load("Invalid choice.", 1.5)
            continue

        # Query to retrieve total cost
        total = 0
        cursor = db.cursor(dictionary=True)
        query = (
            "SELECT * " \
            "FROM cart_contains AS cc JOIN product AS p "
            "   ON cc.prod_id = p.prod_id " \
            "WHERE cc.cart_id = %s"
        )
        args = (cart_id,)
        cursor.execute(query, args,)
        cart_items = cursor.fetchall()

        # Add cost * quantity of each item to total
        for item in cart_items:
            total += float(item['unit_price']) * float(item['quantity'])

        # Query to add new order
        cursor = db.cursor(dictionary=True)
        query = (
            "INSERT INTO orders(" \
            "   delivery_method, " \
            "   total_amount, " \
            "   order_type, " \
            "   order_status, " \
            "   c_id, " \
            "   st_id, " \
            "   e_id" \
            ") VALUES (%s, %s, %s, %s, %s, %s, NULL)"
        )
        args = (delivery_method, total, 'Online', 'In-progress', customer_id, store_id,)
        cursor.execute(query, args)

        # Get newly created order id
        order_id = cursor.lastrowid
        db.commit()

        # print(f"Inserted {cursor.rowcount} row(s).") # Debug check: Only 1 row should be inserted
        cursor.close()

        # Query to add to order_contains
        cursor = db.cursor(dictionary=True)
        query = (
            "INSERT INTO order_contains(" \
            "   order_id," \
            "   prod_id," \
            "   quantity," \
            "   price_at_purchase" \
            ") VALUES (%s, %s, %s, %s)"
        )
        args = []
        for item in cart_items:
            args.append((order_id, item['prod_id'], item['quantity'], item['unit_price']))

        cursor.executemany(query, args)
        db.commit()

        # print(f"Inserted {cursor.rowcount} row(s).") # Debug check: Rows inserted should match rows in cart
        cursor.close()

        # Query to add to delivery_record
        cursor = db.cursor(dictionary=True)
        query = (
            "INSERT INTO delivery_record(" \
            "   delivered_at, " \
            "   delivered_to, " \
            "   delivery_status, " \
            "   order_id, " \
            "   e_id" \
            ") VALUES (NULL, %s, 'In-Progress', %s, NULL)"
        )
        args = (delivery_address, order_id)
        cursor.execute(query, args)
        db.commit()

        #print(f"Inserted {cursor.rowcount} row(s).") # Debug check. Only 1 row should be inserted
        cursor.close()

        # Query to update old cart status
        cursor = db.cursor(dictionary=True)
        query = (
            "UPDATE shopping_cart AS sc " \
            "SET sc.cart_status = 'done' " \
            "WHERE sc.cart_id = %s"
        )
        args = (cart_id,)
        cursor.execute(query, args)
        db.commit()

        # print(f"Updated {cursor.rowcount} row(s).") # Debug check: Only 1 row should be updated
        cursor.close()

        logger.info(f"Customer '{customer_id}' completed checkout for cart '{cart_id}'.")
        print(f"Checkout successful! Your order ID is: {order_id}")
        print("1. View Order Details")
        print("2. Return to Customer Page")
        choice = input("Please enter your choice (1-2): ")
        if choice == '1':
            view_order(order_id, customer_id)
            return
        elif choice == '2':
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

# For testing purposes only. Remove once finalized.
if __name__ == '__main__':
    customer = input("Enter customer ID to test: ").strip()
    customer_page(customer, 1)