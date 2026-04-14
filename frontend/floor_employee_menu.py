import time
from homepage import clear_screen
from logger_config import get_logger

logger = get_logger()


def floor_employee_page(store_id, employee_id):
    while True:
        clear_screen()
        print("Welcome to the Floor Employee Page")
        print("Here you can manage in-store orders and process return requests.")
        print("1. Process In-Store Order")
        print("2. Process Return Requests")
        print("3. Logout")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            process_instore_orders(store_id, employee_id)

        elif choice == "2":
            process_return_requests(store_id, employee_id)

        elif choice == "3":
            print("Logging out...")
            logger.info(f"Floor employee '{employee_id}' logged out successfully.")
            time.sleep(2)
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def process_instore_orders(store_id, employee_id):
    while True:
        clear_screen()
        print("Does customer have an account with us?(y/n)")
        has_account = input().strip().lower()
        if has_account == 'y':
            customer_email = input("Please enter customer's email: ").strip()
            #query to get customer_id using the email, make sure it is valid email
        elif has_account == 'n':
            customer_email = "null"
        print("Processing In-Store Order")
        print("-----------------------------")

        # Theoretically here you would scan products using like a scanner in the store
        # but for simplicity we'll just give some random product ids
        # that you can use for querying into the table
        
        order_items = {
            1:2,
            3:5,
            2:1
        } # dict of product_id: quantity pairs representing the order items
        
        while True:
            print("\nOptions:")
            print("1. Proceed to Payment and Finalize Order")
            print("2. Remove an item from the order")
            print("3. Cancel Order and Return to Floor Employee Page")
            #dont add any queries here just add them in the if-else statements below
            choice = input("Please enter your choice (1-3): ").strip()

            if choice == "1":
                #query to add the products to the order table and the order_contains table 
                #  with the store_id, customer_id (if exists), employee_id, product_ids 
                # and quantities from above - basically update all tables that need to be updated
                
                payments_entry = ["card",,"completed",] 
                # payment method, amount, payment status,order_id (from above query)
                #insert query into the payments table using above array/info
                logger.info(f"Floor employee '{employee_id}' approved return '{return_id} for store '{store_id}'.")

            elif choice == "2":
                prod_id = input("Enter Product ID to remove: ").strip()
                new_quantity = input("Enter new quantity: ").strip()
                order_items[prod_id] = new_quantity

            elif choice == "3":
                return

            else:
                print("Invalid choice. Please try again.")
                time.sleep(2)

def process_return_requests(store_id, employee_id):
    while True:
        clear_screen()
        print("Process Return Requests")
        print("-----------------------------")

        # TODO:
        # Query database for return requests related to this store.
        # Since return_record links to order_contains, you'll likely need joins through:
        # return_record -> order_contains -> orders
        #
        # Suggested filter:
        # - orders.st_id = store_id
        # - return_record.return_status = 'requested'
        #
        # Suggested fields:
        # - return_id
        # - order_id
        # - prod_id
        # - return_quantity
        # - return_reason
        # - requested_at

        print("\nOptions:")
        print("1. View Return Request Details")
        print("2. Approve Return")
        print("3. Deny Return")
        print("4. Return to Floor Employee Page")

        choice = input("Please enter your choice (1-4): ").strip()

        if choice == "1":
            return_id = input("Enter Return ID: ").strip()
            view_return_request_details(return_id, store_id)

        elif choice == "2":
            return_id = input("Enter Return ID to approve: ").strip()
            approve_return(return_id, store_id, employee_id)

        elif choice == "3":
            return_id = input("Enter Return ID to deny: ").strip()
            deny_return(return_id, store_id, employee_id)

        elif choice == "4":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_return_request_details(return_id, store_id):
    clear_screen()
    print(f"Viewing Return Request ID: {return_id}")
    print("-----------------------------")

    # TODO:
    # Query database to show full return request details.
    # Make sure it belongs to an order from this store.
    #
    # Suggested information:
    # - return_record fields
    # - related order_id
    # - product details
    # - original ordered quantity from order_contains

    input("\nPress Enter to return...")

def approve_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Approving Return ID: {return_id}...")
    print("-----------------------------")

    # TODO:
    # 1. Verify the return belongs to an order from this store
    # 2. Verify the return is still in 'requested' status
    # 3. Update return_record:
    #       - return_status = 'approved'
    #       - processed_by_employee_id = employee_id
    # 4. Optionally create/update refund-related payment record in payments
    # 5. Optionally restock returned quantity back into stocks if your team wants that behavior

    print("Return approved successfully.")
    logger.info(f"Floor employee '{employee_id}' approved return '{return_id}'.")
    time.sleep(2)

def deny_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Denying Return ID: {return_id}...")
    print("-----------------------------")

    # TODO:
    # 1. Verify the return belongs to an order from this store
    # 2. Verify the return is still in 'requested' status
    # 3. Update return_record:
    #       - return_status = 'denied'
    #       - processed_by_employee_id = employee_id

    print("Return denied successfully.")
    logger.info(f"Floor employee '{employee_id}' denied return '{return_id}'.")
    time.sleep(2)
