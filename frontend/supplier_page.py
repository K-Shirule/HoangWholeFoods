import time
from utils import clear_screen
from logger_config import get_logger
from db_connector import db

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

        #show a list of all supplier orders this supplier
        cursor = db.cursor(dictionary = True)
        query = """
            SELECT *
            FROM supplier_order
            WHERE supplier_id = %s
            ORDER BY date_of_order DESC;
            """
        cursor.execute(query, (supplier_id))
        orders = cursor.fetchall()
        cursor.close()

        if not orders:
            print("No supplier orders found.")
            input("\nPress Enter to return...")
            return
        
        print("Orders needed to be fulfilled by you \n")
        print(
            f"| {'Supplier ID': <15}" \
            f"| {'Supplier Order ID': <20}" \
            f"| {'Date of Order': <15}" \
            f"| {'Total Amount': <15}" \
            f"| {'Payment Method': <15}" \
            f"| {'Status': <12}" \
            f"| {'Expected Delivery Date': <25}" \
            f"| {'Received Date': <15}" \
            f"| {'Tracking Number': <15}" \
            f"| {'Store ID': <8}" \
            f"| {'List ID': <8} |" 
        )
        print("-" * 90)
        for order in orders:
            print(
                f"| {order['supplier_id']: <15}" \
                f"| {order['so_id']: <20}" \
                f"| {order['date_of_order'].strftime('%Y-%m-%d'): <15}" \
                f"| ${order['total_amount']: <15.2f}" \
                f"| {order['payment_method'] if order['payment_method'] else 'NULL': <15}" \
                f"| {order['status'] if order['status'] else 'NULL': <12}" \
                f"| {order['expected_delivery_date'].strftime('%Y-%m-%d') if order['expected_delivery_date'] else 'NULL': <25}" \
                f"| {order['received_date'].strftime('%Y-%m-%d') if order['received_date'] else 'NULL': <15}" \
                f"| {order['tracking_number'] if order['tracking_number'] else 'NULL': <15}" \
                f"| {order['st_id'] if order['st_id'] is not None else 'NULL': <8}" \
                f"| {order['list_id'] if order['list_id'] is not None else 'NULL': <8} |" 
            )

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

    #show the order that this supplier chooses to view in more detail
    cursor = db.cursor(dictionary = True)
    query = """
        SELECT *
        FROM so_contains
        WHERE so_id = %s AND supplier_id = %s
        ORDER BY so_id DESC;
        """
    cursor.execute(query, (so_id, supplier_id))
    order_details = cursor.fetchall()
    cursor.close()

    if not order_details:
        print("Order not found or access denied.")
        input("\nPress Enter to return...")
        return
    
    print(
        f"| {'Supplier ID': <15}" \
        f"| {'Supplier Order ID': <20}" \
        f"| {'Product ID': <12}" \
        f"| {'Quantity': <10}" \
        f"| {'Cost at Purchase': <18} |" 
    )
    print("-" * 90)
    
    for detail in order_details:
        print(
            f"| {detail['supplier_id']: <15}" \
            f"| {detail['so_id']: <20}" \
            f"| {detail['prod_id']: <12}" \
            f"| {detail['quantity'] if detail['quantity'] is not None else 'NULL': <10}" \
            f"| ${detail['cost_at_purchase'] if detail['cost_at_purchase'] is not None else 'NULL': <18.2f} |"
        )

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
        
        #update the supplier_order table with the new status and any additional info if applicable
        cursor = db.cursor()
        query = """
            UPDATE supplier_order
            SET status = %s,
                tracking_number = %s,
                expected_delivery_date = %s,
                received_date = %s
            WHERE so_id = %s AND supplier_id = %s;
            """
        cursor.execute(query, (new_status, tracking_number, expected_delivery_date, received_date, so_id, supplier_id))
        db.commit()     #save changes to supplier table
        cursor.close()

        print(f"Supplier order {so_id} updated to status '{new_status}'.")
        logger.info(
            f"Supplier '{supplier_id}' updated supplier order '{so_id}' to '{new_status}'."
        )
        time.sleep(2)
        return

def view_supplied_products(supplier_id):
    while True:
        clear_screen()
        print("Products You Supply")
        print("-----------------------------")

        #show a list of all products that this supplier supplies
        cursor = db.cursor(dictionary = True)
        query = """
            SELECT s.supplier_id, s.prod_id, p.name, p.description, p.unit_price, p.units, p.unit_type, p.category_id
            FROM supplies s JOIN product p ON s.prod_id = p.prod_id
            WHERE supplier_id = %s
            ORDER BY prod_id DESC;
            """
        cursor.execute(query, (supplier_id))
        supplied_products = cursor.fetchall()
        cursor.close()

        if not supplied_products:
            print("You are not currently supplying any products.")
            input("\nPress Enter to return...")
            return
        
        print(
            f"| {'Supplier ID': <15}" \
            f"| {'Product ID': <12}" \
            f"| {'Product Name': <20}" \
            f"| {'Description': <30}" \
            f"| {'Unit Price': <12}" \
            f"| {'Units': <8}" \
            f"| {'Unit Type': <12}" \
            f"| {'Category ID': <12} |"
        )
        print("-" * 90)

        for supply in supplied_products:
            print(
                f"| {supply['supplier_id']: <15}" \
                f"| {supply['prod_id']: <12}" \
                f"| {supply['name'][:20]: <20}" \
                f"| {supply['description'][:30]: <30}" \
                f"| ${supply['unit_price'] if supply['unit_price'] is not None else 'NULL': <12.2f}" \
                f"| {supply['units'] if supply['units'] is not None else 'NULL': <8}" \
                f"| {supply['unit_type'] if supply['unit_type'] else 'NULL': <12}" \
                f"| {supply['category_id'] if supply['category_id'] is not None else 'NULL': <12} |"
            )
        
        input("\nPress Enter to return...")

def add_supplied_product(supplier_id):
    while True:
        clear_screen()
        print("Add Product You Supply")
        print("-----------------------------")

        print("Existing Product Catalog:")
        #query to show all the products that currently supplied by any supplier so that they can choose to add an existing product if they want instead of creating a new one
        cursor = db.cursor(dictionary = True)
        query = """
            SELECT prod_id, name, category_id, unit_price
            FROM product
            ORDER BY name ASC;
            """
        cursor.execute(query)
        products = cursor.fetchall()
        cursor.close()

        if not products:
            print("No products found in catalog yet")

        print("Existing Products:")
        print(
            f"| {'Product ID': <12}" \
            f"| {'Product Name': <20}" \
            f"| {'Category ID': <12}" \
            f"| {'Unit Price': <12} |"
        )
        print("-" * 90)

        for product in products: 
            print(
                f"| {product['prod_id']: <12}" \
                f"| {product['name'][:20]: <20}" \
                f"| {product['category_id'] if product['category_id'] is not None else 'NULL': <12}" \
                f"| ${product['unit_price'] if product['unit_price'] is not None else 'NULL': <12.2f} |"
            )   
            
        print("(Select a product to supply OR add a new one)\n")
        print("\nOptions:")
        print("1. Supply an Existing Product")
        print("2. Add a New Product to Catalog")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            prod_id = input("Enter Product ID to supply: ").strip()

            if not prod_id.isdigit():
                print("Invalid Product ID.")
                time.sleep(2)
                continue

            prod_id = int(prod_id)

            #check if product id exists in the product table
            cursor = db.cursor()
            query = """
                SELECT prod_id 
                FROM product
                WHERE prod_id = %s;
                """
            cursor.execute(query, (prod_id,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                print("Product ID does not exist.")
                time.sleep(2)
                continue
            
            #check if the product is already supplied by this supplier
            cursor = db.cursor()
            query = """
                SELECT *
                FROM supplies
                WHERE supplier_id = %s AND prod_id = %s;
                """
            cursor.execute(query, (supplier_id, prod_id))
            existing_supply = cursor.fetchone()
            cursor.close()

            if existing_supply:
                print("You already supply this product.")
                time.sleep(2)
                continue

            #add to supplies table if not already supplying
            cursor = db.cursor()
            query = """
                INSERT INTO supplies (supplier_id, prod_id)
                VALUES (%s, %s);
                """
            cursor.execute(query, (supplier_id, prod_id))
            db.commit()     #save changes to supplies table
            cursor.close()

            print(f"Product {prod_id} added to your supplied products.")
            logger.info(f"Supplier '{supplier_id}' added existing product '{prod_id}' to supplies.")
            time.sleep(2)

        elif choice == "2":
            print("\nEnter new product details:")
            #prod_id = None   
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

            try:    #validate price input
                unit_price = float(unit_price)
                units = int(units) if units.isdigit() else None
                category_id = int(category_id)
            except ValueError:
                print("Invalid numberic input.")
                time.sleep(2)
                continue

            #insert new product into product table 
            cursor = db.cursor()
            query = """
                INSERT INTO product (name, description, category_id, unit_price, units, unit_type)
                VALUES (%s, %s, %s, %s, %s, %s);
                """
            cursor.execute(query, (name, description, category_id, unit_price, units, unit_type))  
            db.commit()     #save changes to product table
            new_prod_id = cursor.lastrowid      #get the prod_id of the newly row
            cursor.close()

            #link to this supplier in supplies table, new row to supppies table
            cursor = db.cursor()
            query = """
                INSERT INTO supplies (supplier_id, prod_id, supply_price)
                VALUES (%s, %s, %s);
                """
            cursor.execute(query, (supplier_id, new_prod_id, unit_price))
            db.commit()
            cursor.close()

            print(f"New product '{name}' added and linked to your supplies.")
            logger.info(f"Supplier '{supplier_id}' created new product '{name}' and added to supplies.")
            time.sleep(2)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Try again.")
            time.sleep(2)

def remove_supplied_product(supplier_id):
    while True:
        clear_screen()
        print("Remove Product You Supply")
        print("-----------------------------")

        #show current supplied products
        cursor = db.cursor(dictionary = True)
        query = """
            SELECT s.supplier_id, s.prod_id, p.name
            FROM supplies s JOIN product p ON s.prod_id = p.prod_id
            WHERE supplier_id = %s
            ORDER BY prod_id DESC;
            """
        cursor.execute(query, (supplier_id))
        supplied_products = cursor.fetchall()
        cursor.close()

        if not supplied_products:
            print("You are not currently supplying any products.")
            input("\nPress Enter to return...")
            return
        
        print("Your current supplied products:")
        print(
            f"| {'Product ID': <12}" \
            f"| {'Product Name': <20} |"
        )
        print("-" * 90)

        for supply in supplied_products:
            print(
                f"| {supply['prod_id']: <12}" \
                f"| {supply['name'][:20]: <20} |"
            )

        prod_id = input("Enter Product ID to remove: ").strip()

        if not prod_id.isdigit():
            print("Invalid Product ID.")
            time.sleep(2)
            continue

        prod_id = int(prod_id)
        
        #check if this supplier actually supplies this product
        cursor = db.cursor(dictionary = True)
        query = """
            SELECT *
            FROM supplies
            WHERE supplier_id = %s AND prod_id = %s;
            """
        cursor.execute(query, (supplier_id, prod_id))
        existing = cursor.fetchone()
        cursor.close()

        if not existing:
            print("You do not supply this product.")
            time.sleep(2)
            continue

        confirmation = input(f"Are you sure you want to stop supplying product {prod_id}? (y/n): ").strip().lower()
        if confirmation != 'y':
            print("Operation cancelled.")
            time.sleep(2)
            continue

        #proceed to remove the product from this supplier's supplied products list
        cursor = db.cursor()
        query = """
            DELETE FROM supplies
            WHERE supplier_id = %s AND prod_id = %s;
            """
        cursor.execute(query, (supplier_id, prod_id))
        db.commit()     #save changes to supplies table
        cursor.close()

        print(f"Product {prod_id} removed from your supplied products list.")
        logger.info(f"Supplier '{supplier_id}' removed product '{prod_id}' from supplies.")
        time.sleep(2)
