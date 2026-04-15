from time import sleep
from logger_config import get_logger
from utils import clear_screen, print_load

logger = get_logger(__name__)

def inventory_manager_menu(username, store_id, employee_id):
    while True:
        clear_screen()
        print("\nInventory Manager Menu:")
        print("1. View Inventory")
        print("2. View supplier products")
        print("3. View restock list")
        print("4. View past restock lists")
        print("5. Remove a product from inventory")
        print("6. Add a product to inventory")
        print("7. Mark restock list as delivered")
        print("8. Logout")

        choice = input("\nPlease select an option (1-8): ").strip()

        if choice == "1":
            view_inventory(store_id)

        elif choice == "2":
            view_supplier_products(store_id, employee_id)

        elif choice == "3":
            view_restock_list(store_id)

        elif choice == "4":
            view_past_restock_lists(store_id)

        elif choice == "5":
            remove_product(store_id)

        elif choice == "6":
            add_new_product(store_id)

        elif choice == "7":
            mark_restock_list_delivered(store_id, employee_id)

        elif choice == "8":
            print("\nLogging out...")
            break

        else:
            print("\nInvalid option. Please try again.")

def view_inventory(store_id):
    print("\nViewing inventory...")

    # TODO: Query database using store_id to fetch inventory (stocks + product)

    print("Press Enter to return to the menu.")
    input()

def view_supplier_products(store_id, employee_id):
    print("\nViewing supplier products...")
    sleep(3)
    while True:
        clear_screen()
        # TODO: Query database to fetch supplier products (product + supplies)
        print("\n1. Add a product to restock list")
        print("2. Return to the previous menu.")

        choice = input("Please select an option (1-2): ").strip()

        if choice == "1":
            product_id = input("Enter Product ID: ").strip()
            quantity = input("Enter quantity: ").strip()

            add_product_to_restock_list(product_id, quantity, store_id, employee_id)

        elif choice == "2":
            return

        else:
            print("Invalid option.")

def add_product_to_restock_list(product_id, quantity, store_id, employee_id):
    print("\nAdding product to restock list...")

    # TODO:
    # 1. Check if a pending restock_list exists for this store
    # 2. If not, create a new restock_list using store_id and employee_id
    # 3. Insert into restock_contains (list_id, product_id, quantity)

    print("Product added to restock list.")
    logger.info(f"Employee {employee_id} added product {product_id} (quantity: {quantity}) to restock list for store {store_id}.")
    sleep(3)

def view_restock_list(store_id):
    print("\nViewing current restock list...")


    while True:
        clear_screen()
        # TODO: Query restock_list where store_id = store_id AND status = 'pending' and show products in the list using restock_contains + product tables
        print("1. Remove a product from restock list")
        print("2. Return to the previous menu.")
        choice = input("\nPlease select an option (1-2): ").strip()

        if choice == "1":
            product_id = input("Enter Product ID: ").strip()
            remove_product_from_restock_list(product_id, store_id)
        elif choice == "2":
            return
        else:
            print("Invalid option.")

def remove_product_from_restock_list(product_id, store_id, employee_id):
    print("\nRemoving product from restock list...")
    sleep(3)
    #query to remove the product from the restock list using th store_id and product_id
    logger.info(f"Product {product_id} removed from restock list for store {store_id} by employee {employee_id}.")

def view_past_restock_lists(store_id):
    print("\nViewing past restock lists...")

    # TODO: Query restock_list where store_id = store_id AND status != 'pending'

    input("\nPress Enter to continue...")

def remove_product(store_id, employee_id):
    print("\nRemove product from inventory")

    product_id = input("Enter Product ID: ").strip()

    # TODO: Delete or update stock entry in stocks table using store_id + product_id

    print("Product removed from inventory.")
    logger.info(f"Product {product_id} removed from inventory for store {store_id} by employee {employee_id}.")
    sleep(3)

def add_new_product(store_id, employee_id):
    print("\nAdd product to inventory")

    product_id = input("Enter Product ID: ").strip()
    quantity = input("Enter quantity: ").strip()

    # TODO:
    # Insert into stocks (store_id, product_id, quantity)
    # OR update quantity if product already exists

    print("Product added/updated in inventory.")
    logger.info(f"Product {product_id} (quantity: {quantity}) added to inventory for store {store_id} by employee {employee_id}.")
    sleep(3)

def mark_restock_list_delivered(store_id, employee_id):
    print("\nMark Restock List as Delivered")

    list_id = input("Enter Restock List ID: ").strip()

    # TODO:
    # 1. Verify the restock list belongs to this store
    # 2. Verify the status is not already 'delivered'
    # 3. Fetch all products and quantities from restock_contains for this list
    # 4. For each product:
    #       - if product already exists in stocks for this store, increase quantity
    #       - otherwise insert a new row into stocks
    # 5. Update restock_list status to 'delivered'

    print(f"Restock list {list_id} marked as delivered and inventory updated.")
    logger.info(f"Restock list {list_id} marked as delivered for store {store_id} by employee {employee_id}.")
    sleep(3)

