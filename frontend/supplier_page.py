import time
from utils import clear_screen
from logger_config import get_logger

logger = get_logger()

def supplier_page(supplier_id):
    while True:
        clear_screen()
        print("Welcome to the Supplier Page")
        print("Here you can view incoming supplier orders and update their status.")
        print("1. View Supplier Orders")
        print("2. View Products You Supply")
        print("3. Add Product You Supply")
        print("4. Remove Product You Supply")
        print("5. Logout")

        choice = input("Please enter your choice (1-5): ").strip()

        if choice == "1":
            view_supplier_orders(supplier_id)

        elif choice == "2":
            view_supplied_products(supplier_id)

        elif choice == "3":
            add_supplied_product(supplier_id)

        elif choice == "4":
            remove_supplied_product(supplier_id)

        elif choice == "5":
            print("Logging out...")
            logger.info(f"Supplier '{supplier_id}' logged out successfully.")
            time.sleep(2)
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_supplier_orders(supplier_id):
    while True:
        clear_screen()
        print("Supplier Orders")
        print("-----------------------------")

        # TODO:
        # Query database for all supplier_order rows for this supplier_id
        #
        # Suggested fields to show:
        # - so_id
        # - date_of_order
        # - total_amount
        # - payment_method
        # - status
        # - expected_delivery_date
        # - received_date
        # - tracking_number
        # - st_id

        print("\nOptions:")
        print("1. View Supplier Order Details")
        print("2. Update Supplier Order Status")
        print("3. Return to Supplier Page")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            so_id = input("Enter Supplier Order ID: ").strip()
            view_supplier_order_details(so_id, supplier_id)

        elif choice == "2":
            so_id = input("Enter Supplier Order ID: ").strip()
            update_supplier_order_status(so_id, supplier_id)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_supplier_order_details(so_id, supplier_id):
    clear_screen()
    print(f"Viewing Supplier Order ID: {so_id}")
    print("-----------------------------")

    # TODO:
    # Query database for supplier_order details using:
    # - so_id
    # - supplier_id
    #
    # Also query so_contains to show:
    # - prod_id
    # - quantity
    # - cost_at_purchase
    #
    # Optionally join product table to display product names

    input("\nPress Enter to return...")

def update_supplier_order_status(so_id, supplier_id):
    while True:
        clear_screen()
        print(f"Update Status for Supplier Order ID: {so_id}")
        print("-----------------------------")
        print("1. Mark as Confirmed")
        print("2. Mark as Processing")
        print("3. Mark as Shipped")
        print("4. Mark as Delivered")
        print("5. Return")

        choice = input("Please enter your choice (1-5): ").strip()

        if choice == "1":
            new_status = "confirmed"

        elif choice == "2":
            new_status = "processing"

        elif choice == "3":
            new_status = "shipped"

        elif choice == "4":
            new_status = "delivered"

        elif choice == "5":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)
            continue

        tracking_number = None
        expected_delivery_date = None
        received_date = None

        if new_status == "shipped":
            tracking_number = input("Enter tracking number: ").strip()
            expected_delivery_date = input("Enter expected delivery date (YYYY-MM-DD): ").strip()

        elif new_status == "delivered":
            received_date = input("Enter received/delivery date (YYYY-MM-DD): ").strip()

        # TODO:
        # 1. Verify supplier_order belongs to this supplier_id
        # 2. Update supplier_order.status = new_status
        # 3. If shipped:
        #       - update tracking_number
        #       - update expected_delivery_date
        # 4. If delivered:
        #       - update received_date
        #
        # Note:
        # This only updates supplier_order.
        # Inventory should be updated later by the inventory manager
        # when they confirm receipt.

        print(f"Supplier order {so_id} updated to status '{new_status}'.")
        logger.info(
            f"Supplier '{supplier_id}' updated supplier order '{so_id}' to '{new_status}'."
        )
        time.sleep(2)
        return

def view_supplied_products(supplier_id):
    clear_screen()
    print("Products You Supply")
    print("-----------------------------")

    # TODO:
    # Query database using supplies table for all products supplied by this supplier.
    #
    # Suggested join:
    # supplies + product
    #
    # Suggested fields:
    # - prod_id
    # - name
    # - description
    # - unit_price
    # - units
    # - unit_type
    # - category if desired

    input("\nPress Enter to return...")

def add_supplied_product(supplier_id):
    while True:
        clear_screen()
        print("Add Product You Supply")
        print("-----------------------------")

        print("Existing Product Catalog:")
        #query to show all the products that exist in the product catalog
        print("(Select a product to supply OR add a new one)\n")

        # TODO:
        # Query and display all products from product table
        # Suggested fields:
        # - prod_id
        # - name
        # - category
        # - unit_price

        print("\nOptions:")
        print("1. Supply an Existing Product")
        print("2. Add a New Product to Catalog")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        # -------------------------
        # OPTION 1: EXISTING PRODUCT
        # -------------------------
        if choice == "1":
            prod_id = input("Enter Product ID to supply: ").strip()

            if not prod_id.isdigit():
                print("Invalid Product ID.")
                time.sleep(2)
                continue

            prod_id = int(prod_id)

            # TODO:
            # 1. Verify prod_id exists in product table
            # 2. Check if (supplier_id, prod_id) already exists in supplies
            # if it does exist then let them know they already supply it
            # 3. If not, insert into supplies table

            print(f"Product {prod_id} added to your supplied products.")
            logger.info(f"Supplier '{supplier_id}' added existing product '{prod_id}' to supplies.")
            time.sleep(2)

        # -------------------------
        # OPTION 2: NEW PRODUCT
        # -------------------------
        elif choice == "2":
            print("\nEnter new product details:")

            #show them the category table to pick from 

            name = input("Product name: ").strip()
            description = input("Description: ").strip()
            category_id = input("Category ID: ").strip()
            unit_price = input("Price: ").strip()
            units = input("Units: ").strip()
            unit_type = input("Unit type: ").strip()

            if not name or not category_id.isdigit():
                print("Invalid input.")
                time.sleep(2)
                continue

            try:
                unit_price = float(unit_price)
            except ValueError:
                print("Invalid price.")
                time.sleep(2)
                continue

            units = int(units) if units.isdigit() else None
            category_id = int(category_id)

            # TODO:
            # 1. Insert into product table
            # 2. Get new prod_id
            # 3. Insert into supplies table (supplier_id, prod_id)

            print(f"New product '{name}' added and linked to your supplies.")
            logger.info(f"Supplier '{supplier_id}' created new product '{name}' and added to supplies.")
            time.sleep(2)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Try again.")
            time.sleep(2)

def remove_supplied_product(supplier_id):
    clear_screen()
    print("Remove Product You Supply")
    print("-----------------------------")
    
    view_supplied_products(supplier_id)

    product_id = input("Enter Product ID to remove: ").strip()

    # TODO:
    # 1. Verify (supplier_id, product_id) exists in supplies
    # 2. Remove that row from supplies

    print(f"Product {product_id} removed from your supplied products list.")
    logger.info(f"Supplier '{supplier_id}' removed product '{product_id}' from supplies.")
    time.sleep(2)
