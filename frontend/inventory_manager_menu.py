import time
from logger_config import get_logger
from homepage import clear_screen

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
        print("7. Receive Supplier Order")
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
            remove_product(store_id, employee_id)

        elif choice == "6":
            add_new_product(store_id, employee_id)

        elif choice == "7":
            receive_supplier_orders_menu(store_id, employee_id)

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
    time.sleep(3)
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
    time.sleep(3)

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
    time.sleep(3)
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
    time.sleep(3)

def add_new_product(store_id, employee_id):
    print("\nAdd product to inventory")

    product_id = input("Enter Product ID: ").strip()
    quantity = input("Enter quantity: ").strip()

    # TODO:
    # Insert into stocks (store_id, product_id, quantity)
    # OR update quantity if product already exists

    print("Product added/updated in inventory.")
    logger.info(f"Product {product_id} (quantity: {quantity}) added to inventory for store {store_id} by employee {employee_id}.")
    time.sleep(3)

def receive_supplier_orders_menu(store_id, employee_id):
    while True:
        clear_screen()
        print("Receive Supplier Orders")
        print("-----------------------------")

        # TODO:
        # Query supplier orders for this store that are incoming.
        #
        # display supplier orders with the status of:
        # - delivered
        #
        # Suggested fields:
        # - so_id
        # - supplier_id
        # - list_id
        # - date_of_order
        # - status
        # - expected_delivery_date
        # - tracking_number

        print("\nOptions:")
        print("1. Mark Supplier Order as Received")
        print("2. Return to Inventory Manager Page")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            so_id = input("Enter Supplier Order ID: ").strip()
            supplier_id = input("Enter Supplier ID: ").strip()
            receive_supplier_order(so_id, supplier_id, store_id, employee_id)

        elif choice == "2":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def receive_supplier_order(so_id, supplier_id, store_id, employee_id):
    clear_screen()
    print(f"Receiving Supplier Order ({so_id}, {supplier_id})")
    print("---------------------------------------------")

    # TODO:
    # 1. Verify this supplier_order belongs to store_id
    # 2. Verify the current status is 'delivered'
    # 3. Fetch supplier_order info, including list_id if available
    # 4. Fetch all rows from so_contains for this supplier order:
    #       - prod_id
    #       - quantity
    #       - cost_at_purchase
    #
    # 5. For each item:
    #       - if product exists in stocks for this store, increase quantity
    #       - otherwise insert a new row into stocks
    #       - update product.unit_price = round(cost_at_purchase * 1.15, 2)
    #
    # 6. Update supplier_order:
    #       - status = 'received'
    #       - received_date = current date
    #
    # 7. Call sync_restock_list_status(list_id, store_id)

    # Replace this with the actual list_id that this supplier order belongs to.
    list_id = None

    sync_restock_list_status(list_id, store_id)

    print(f"Supplier order ({so_id}, {supplier_id}) marked as received.")
    logger.info(
        f"Employee '{employee_id}' received supplier order ({so_id}, {supplier_id}) for store '{store_id}'."
    )
    time.sleep(2)


def sync_restock_list_status(list_id, store_id):
    # This needs supplier_order.list_id to exist for clean tracking.
    if list_id is None:
        return

    # TODO:
    # 1. Query all supplier_order rows tied to this list_id
    # 2. Collect all their statuses
    # 3. Suggested rules:
    #       - if all are 'received' -> restock_list.status = 'delivered'
    #       - if some are 'received' -> restock_list.status = 'partially_delivered'
    #       - otherwise -> restock_list.status = 'ordered'
    # 4. Update restock_list for this list_id

    pass

