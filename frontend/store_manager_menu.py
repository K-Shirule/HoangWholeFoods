import time
from homepage import clear_screen
from logger_config import get_logger
from frontend.utils import clear_screen, print_load
from create_supplier_orders import create_supplier_orders_for_restock_list

logger = get_logger()


def store_manager_page(store_id, e_id):
    while True:
        clear_screen()
        print("Welcome to the Store Manager Page")
        print("Here you can manage employees, approve restock requests, and view store activity.")
        #get store name from store_id
        print("\nStore Name: {store_name}")
        print("1. View Employees")
        print("2. View Pending Restock Lists")
        print("3. View Past Restock Lists")
        print("4. View Store Orders")
        print("5. View Store Pin")
        print("6. View Supplier Pin")
        print("7. Logout")

        choice = input("Please enter your choice (1-7): ").strip()

        if choice == "1":
            view_employees(store_id, e_id)

        elif choice == "2":
            view_pending_restock_list(store_id, e_id)

        elif choice == "3":
            view_past_restock_lists(store_id)

        elif choice == "4":
            view_store_orders(store_id)

        elif choice == "5":
            view_store_pin(store_id)

        elif choice == "6":
            view_supplier_pin(store_id)

        elif choice == "7":
            print("Logging out...")
            time.sleep(2)
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_employees(store_id, e_id):
    while True:
        clear_screen()
        print("\nOptions:")
        print("1. View Current Employee Details")
        print("2. View Past Employee Details")
        print("3. Return to Store Manager Page")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            view_current_employee_details(store_id, e_id)

        elif choice == "2":
            view_past_employee_details(store_id)

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_current_employee_details(store_id, e_id):
    while True:
        clear_screen()
        print(f"Viewing details for current employees: ")

        # TODO: Query employees where store_id = store_id and current = TRUE

        print("\nOptions:")
        print("1. Mark Employee as Inactive")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            target_employee_id = input("Enter Employee ID to mark as inactive: ").strip()
            #make sure that the entered employee_id is valid and currently active before proceeding
            print(f"\nMarking Employee {target_employee_id} as inactive...")

            # TODO: Update employee is_current = FALSE, set end_date

            logger.info(f"Employee '{target_employee_id}' marked inactive by manager '{e_id}'.")
            time.sleep(2)

        elif choice == "2":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def view_past_employee_details(store_id):
    clear_screen()
    print(f"Viewing details for past employees: ")
    # TODO: Query employees where store_id = store_id and current = FALSE
    #don't need to do any update/creation ops here just display past employee details

def view_pending_restock_list(store_id, e_id):
    while True:
        clear_screen()
        print("Pending Restock Lists")

        # TODO: Query pending restock list

        print("\nOptions:")
        print("1. Approve Restock List")
        print("2. Deny/Cancel Restock List")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            approve_restock_list(list_id, store_id, employee_id)
            list_id = input("List Approved").strip()


        elif choice == "2":
            deny_restock_list(list_id, store_id, employee_id)
            list_id = input("List Sent Back to Inventory Manager: ").strip()


        elif choice == "3":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def approve_restock_list(list_id, store_id, employee_id):
    print(f"\nApproving Restock List {list_id}...")

    # TODO: Update status = 'approved', set approved_by and approved_at

    create_supplier_orders_for_restock_list(list_id, store_id)
    logger.info(f"Restock list '{list_id}' approved by '{employee_id}'.")
    time.sleep(2)

def deny_restock_list(list_id, store_id, employee_id):
    print(f"\nDenying Restock List {list_id}...")

    # TODO: Update status = 'cancelled' or 'denied'

    logger.info(f"Restock list '{list_id}' denied by '{employee_id}'.")
    time.sleep(2)

def view_past_restock_lists(store_id):
    while True:
        clear_screen()
        print("Past Restock Lists")

        # TODO: Query delivered/cancelled lists

        print("\nOptions:")
        print("1. View Details")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            list_id = input("Enter Restock List ID: ").strip()
            view_restock_list_details(list_id, store_id)

        elif choice == "2":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def view_restock_list_details(list_id, store_id):
    clear_screen()
    print(f"Viewing Restock List {list_id}")
    #TODO Query to print restock list details (products, quantities, status, timestamps, who created/approved)

def view_store_orders(store_id):
    while True:
        clear_screen()
        print("Store Orders")

        # TODO: Query orders for this store - show only breifly not all details

        print("\nOptions:")
        print("1. View Order Details")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            order_id = input("Enter Order ID: ").strip()
            view_store_order_details(order_id, store_id)

        elif choice == "2":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def view_store_order_details(order_id, store_id):
    clear_screen()
    print(f"Viewing Order {order_id}")

    # TODO: Show full order details

    input("\nPress Enter to return...")

def view_store_pin(store_id):
    print(f"Viewing Store PIN for Store {store_id}")
    # TODO: Query and display store PIN details from DB

def view_supplier_pin(store_id):
    print(f"Viewing Supplier PIN for Store {store_id}")
    #TODO: Query and display supplier PIN details from DB