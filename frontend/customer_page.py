from time import time

import bcrypt
from homepage import clear_screen
from auth import check_username
from product_page import view_product_catalog
from logger_config import get_logger

logger = get_logger()

def customer_page(customer_id, username):
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
            view_shopping_cart(customer_id)
        elif choice == '3':
            view_order_history(customer_id)
        elif choice == '4':
            manage_account_information(customer_id)
        elif choice == '5':
            print("Logging out...")
            time.sleep(2)
            logger.info(f"customer '{customer_id}' logged out successfully.")
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(3)

def view_shopping_cart(customer_id):
    clear_screen()
    print("Viewing shopping cart...")
    #sql query to view shpping cart using the customer_id variable passed as paramter.
    
    #in case query returns null: print("Your shopping cart is currently empty.")
    while(True):
        clear_screen()
        print("1. Proceed to Checkout")
        print("2. Remove an Item")
        print("3. Return to Customer Page")
        choice = input("Please enter your choice (1-3): ")
        if choice == '1':
            checkout(customer_id, cart_id)
        elif choice == '2':
            print("Please enter the product_id of the item you wish to remove: ")
            product_id = input().strip()
            print("Please enter the quantity of the item you wish to remove: ")
            quantity = input().strip()
            #make sure quantity is a positive integer and does not exceed quantity of item in cart
            #run query to remove item from cart using the customer_id, product_id, and quantity variables passed as parameters.
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
        print("To view details of a specific order, enter the order ID.")
        print("To return to the Customer Page, type 'back'")
        choice = input("Please enter your choice: ")
        if choice.lower() == 'back':
            return
        elif choice.isdigit():
            order_id = choice
            print(f"Viewing details for order ID: {order_id}...")
            view_order(order_id)
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
        print("1. Change First Name")
        print("2. Change Last Name")
        print("3. Change Phone Number")
        print("4. Change Email")
        print("5. Change Password")
        print("6. Return to Customer Page")
        choice = input("Please enter your choice (1-6): ")
        if choice == '1':
            print("Please enter your new first name: ")
            new_first_name = input().strip()
            #query to update first name in database
            logger.info(f"Customer '{customer_id}' updated their first name.")
        elif choice == '2':
            print("Please enter your new last name: ")
            new_last_name = input().strip()
            #query to update last name in database
            logger.info(f"Customer '{customer_id}' updated their last name.")
        elif choice == '3':
            print("Please enter your new phone number: ")
            new_phone_number = input().strip()
            #query to update phone number in database
            logger.info(f"Customer '{customer_id}' updated their phone number.")
        elif choice == '5':
            print("Please enter your new password: ")
            new_password = input().strip()
            hashed = bcrypt.hashpw(new_password, bcrypt.gensalt())
            #query to update password in database
            logger.info(f"Customer '{customer_id}' updated their password.")
        elif choice == '4':
            print("Please enter your new email: ")
            new_email = input().strip()
            check_username(new_email, "customer")
            #query to update email in database
            logger.info(f"Customer '{customer_id}' updated their email.")
        elif choice == '6':
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)
        print("Information updated successfully.")
        time.sleep(3)

def view_order(order_id, customer_id):
    print("Viewing order details...")
    #sql query to view order details using the order_id variable passed as paramter.
    while(True):
        clear_screen()
        print("1. Return an Item")
        print("2. Leave review for an item")
        print("3. Return to Order History")
        choice = input("Please enter your choice (1-3): ")
        if choice == '1':
            print("Please enter the product_id of the item you wish to return: ")
            product_id = input().strip()
            return_item(order_id, product_id, customer_id)
            #query to return item using the order_id and item_name variables passed as parameters.
        elif choice == '2':
            print("Please enter the product_id of the item you wish to review: ")
            product_id = input().strip()
            review_item(product_id, customer_id)
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def checkout(customer_id, cart_id):
    print("Proceeding to checkout...")
    #sql query to checkout using the customer_id and cart_id variables passed as paramter.
    #after successful checkout, generate order_id variable to pass as parameter in view_order function
    while(True):
        clear_screen()
        print("Please select if you would like to pick up your order in store or have it delivered.")
        print("1. In Store Pickup")
        print("2. Delivery")
        choice = input("Please enter your choice (1-2): ")
        if choice == '1':
            print("You have selected in store pickup. Please proceed to the pickup counter and pay when you arrive at the store.")
            break
        elif choice == '2':
            print("You have selected delivery. Please enter your delivery address: ")
            delivery_address = input().strip()
            print("Your order will be delivered to the provided address within the next 3-5 business days.")
            break
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)
        logger.info(f"Customer '{customer_id}' completed checkout for cart '{cart_id}'.")
        print("Checkout successful! Your order ID is: {order_id}")
        print("1. View Order Details")
        print("2. Return to Customer Page")
        choice = input("Please enter your choice (1-2): ")
        if choice == '1':
            view_order(order_id, customer_id)
        elif choice == '2':
            return
        else:
            print("Invalid choice. Try Again.")
            time.sleep(3)

def return_item(order_id, product_id, customer_id):
    print("Processing return...")
    #sql query to return item using the order_id and product_id variables passed as parameters.
    #make sure the product being returned is actually in the order
    #also make sure the return quantity does not exceed the quantity of the item in the order
    #add the return order to the return_order table
    print("Item return initiated. A floor employee will either approve or deny your return request within the next 24-48 hours.")
    logger.info(f"Customer '{customer_id}' initiated a return for product '{product_id}' in order '{order_id}'.")
    time.sleep(5)

def review_item(product_id, customer_id):
    print("Leaving review...")
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
    print("Thank you for leaving a review!")
    logger.info(f"Customer '{customer_id}' left a review for product '{product_id}' .")
    time.sleep(3)









