import time
from datetime import datetime

from utils import clear_screen
from logger_config import get_logger
from db_connector import db

logger = get_logger(__name__)

VALID_SUPPLIER_ORDER_STATUSES = ("pending", "shipped", "delivered", "received")


def parse_date(date_text):
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_supplier_order_header(so_id, supplier_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT supplier_id, so_id, date_of_order, total_amount, payment_method,
            so_status AS status, expected_delivery_date, received_date, tracking_number,
               st_id, list_id
        FROM supplier_order
        WHERE so_id = %s AND supplier_id = %s
        """,
        (so_id, supplier_id)
    )
    order = cursor.fetchone()
    cursor.close()
    return order


def get_supplier_order_lines(so_id, supplier_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT sc.supplier_id, sc.so_id, sc.prod_id, p.name,
               sc.quantity, sc.cost_at_purchase
        FROM so_contains sc
        JOIN product p ON sc.prod_id = p.prod_id
        WHERE sc.so_id = %s AND sc.supplier_id = %s
        ORDER BY p.name ASC
        """,
        (so_id, supplier_id)
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_supplier_product(supplier_id, prod_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT supplier_id, prod_id, supplier_price
        FROM supplies
        WHERE supplier_id = %s AND prod_id = %s
        """,
        (supplier_id, prod_id)
    )
    row = cursor.fetchone()
    cursor.close()
    return row


def get_product(prod_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT prod_id, category_id, name, description, unit_price, units, unit_type
        FROM product
        WHERE prod_id = %s
        """,
        (prod_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row


def category_exists(category_id):
    cursor = db.cursor()
    cursor.execute("SELECT cat_id FROM category WHERE cat_id = %s", (category_id,))
    row = cursor.fetchone()
    cursor.close()
    return row is not None


def get_all_categories():
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT cat_id, name, description
        FROM category
        ORDER BY name ASC
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    return rows


def supplier_page(supplier_id):
    while True:
        clear_screen()
        print("Welcome to the Supplier Page")
        print("Here you can view incoming supplier orders and manage the products you supply.")
        print("1. View Supplier Orders")
        print("2. View Products You Supply")
        print("3. Add Product You Supply")
        print("4. Remove Product You Supply")
        print("5. View Pending Supplier Orders")
        print("6. View Total Sales from Your Products")
        print("7. Logout")

        choice = input("Please enter your choice (1-7): ").strip()

        if choice == "1":
            view_supplier_orders(supplier_id)
        elif choice == "2":
            view_supplied_products(supplier_id)
        elif choice == "3":
            add_supplied_product(supplier_id)
        elif choice == "4":
            remove_supplied_product(supplier_id)
        elif choice == "5":
            view_pending_supplier_orders(supplier_id)
        elif choice == "6":
            view_total_sales_by_products(supplier_id)
        elif choice == "7":
            print("Logging out...")
            logger.info(f"Supplier '{supplier_id}' logged out successfully.")
            time.sleep(2)
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def print_supplier_orders_table(orders):
    print(
        f"| {'Supplier ID':<11} "
        f"| {'SO ID':<8} "
        f"| {'Order Date':<12} "
        f"| {'Total':<12} "
        f"| {'Payment':<12} "
        f"| {'Status':<11} "
        f"| {'Expected':<12} "
        f"| {'Received':<12} "
        f"| {'Tracking':<15} "
        f"| {'Store':<7} "
        f"| {'List':<7} |"
    )
    print("-" * 145)

    for order in orders:
        order_date = order["date_of_order"].strftime("%Y-%m-%d") if order["date_of_order"] else "NULL"
        expected = order["expected_delivery_date"].strftime("%Y-%m-%d") if order["expected_delivery_date"] else "NULL"
        received = order["received_date"].strftime("%Y-%m-%d") if order["received_date"] else "NULL"
        total_amount = float(order["total_amount"]) if order["total_amount"] is not None else 0.0

        print(
            f"| {order['supplier_id']:<11} "
            f"| {order['so_id']:<8} "
            f"| {order_date:<12} "
            f"| ${total_amount:<11.2f} "
            f"| {(order['payment_method'] or 'NULL'):<12} "
            f"| {(order['status'] or 'NULL'):<11} "
            f"| {expected:<12} "
            f"| {received:<12} "
            f"| {(order['tracking_number'] or 'NULL'):<15} "
            f"| {str(order['st_id']) if order['st_id'] is not None else 'NULL':<7} "
            f"| {str(order['list_id']) if order['list_id'] is not None else 'NULL':<7} |"
        )


def view_supplier_orders(supplier_id):
    while True:
        clear_screen()
        print("Supplier Orders")
        print("-----------------------------")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT supplier_id, so_id, date_of_order, total_amount, payment_method,
            so_status AS status, expected_delivery_date, received_date, tracking_number,
                   st_id, list_id
            FROM supplier_order
            WHERE supplier_id = %s
            ORDER BY date_of_order DESC, so_id DESC
            """,
            (supplier_id,)
        )
        orders = cursor.fetchall()
        cursor.close()

        if not orders:
            print("No supplier orders found.")
            input("\nPress Enter to return...")
            return

        print_supplier_orders_table(orders)

        print("\nOptions:")
        print("1. View Supplier Order Details")
        print("2. Update Supplier Order Status")
        print("3. Return to Supplier Page")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            so_id = input("Enter Supplier Order ID: ").strip()
            if not so_id.isdigit():
                print("Invalid Supplier Order ID.")
                time.sleep(2)
                continue
            view_supplier_order_details(int(so_id), supplier_id)

        elif choice == "2":
            so_id = input("Enter Supplier Order ID: ").strip()
            if not so_id.isdigit():
                print("Invalid Supplier Order ID.")
                time.sleep(2)
                continue
            update_supplier_order_status(int(so_id), supplier_id)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_supplier_order_details(so_id, supplier_id):
    clear_screen()
    print(f"Viewing Supplier Order ID: {so_id}")
    print("-----------------------------")

    header = get_supplier_order_header(so_id, supplier_id)
    if not header:
        print("Order not found or access denied.")
        input("\nPress Enter to return...")
        return

    order_details = get_supplier_order_lines(so_id, supplier_id)
    if not order_details:
        print("This supplier order has no line items.")
        input("\nPress Enter to return...")
        return

    print(f"Status: {header['status'] or 'NULL'}")
    print(f"Order Date: {header['date_of_order']}")
    print(f"Store ID: {header['st_id']}")
    print(f"List ID: {header['list_id']}")
    print(f"Tracking Number: {header['tracking_number'] or 'NULL'}")
    print()

    print(
        f"| {'Supplier ID':<11} "
        f"| {'SO ID':<8} "
        f"| {'Product ID':<10} "
        f"| {'Product Name':<24} "
        f"| {'Quantity':<10} "
        f"| {'Cost at Purchase':<17} |"
    )
    print("-" * 95)

    for detail in order_details:
        cost = float(detail["cost_at_purchase"]) if detail["cost_at_purchase"] is not None else 0.0
        print(
            f"| {detail['supplier_id']:<11} "
            f"| {detail['so_id']:<8} "
            f"| {detail['prod_id']:<10} "
            f"| {detail['name'][:24]:<24} "
            f"| {detail['quantity'] if detail['quantity'] is not None else 'NULL':<10} "
            f"| ${cost:<16.2f} |"
        )

    input("\nPress Enter to return...")


def update_supplier_order_status(so_id, supplier_id):
    order = get_supplier_order_header(so_id, supplier_id)
    if not order:
        print("Supplier order not found or access denied.")
        time.sleep(2)
        return

    current_status = (order["status"] or "").lower()

    while True:
        clear_screen()
        print(f"Update Status for Supplier Order ID: {so_id}")
        print(f"Current Status: {order['status'] or 'NULL'}")
        print("-----------------------------")
        print("1. Mark as Shipped")
        print("2. Mark as Delivered")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            new_status = "shipped"
        elif choice == "2":
            new_status = "delivered"
        elif choice == "3":
            return
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)
            continue

        if current_status == "received":
            print("Received orders cannot be updated further by the supplier.")
            time.sleep(2)
            return

        if current_status == "delivered" and new_status == "shipped":
            print("You cannot move a delivered order back to shipped.")
            time.sleep(2)
            continue

        if current_status == "pending" and new_status == "delivered":
            print("Order should be marked as shipped before delivered.")
            time.sleep(2)
            continue

        tracking_number = order["tracking_number"]
        expected_delivery_date = order["expected_delivery_date"]
        received_date = order["received_date"]

        if new_status == "shipped":
            tracking_number_input = input("Enter tracking number: ").strip()
            expected_input = input("Enter expected delivery date (YYYY-MM-DD): ").strip()

            if not tracking_number_input:
                print("Tracking number cannot be empty when marking as shipped.")
                time.sleep(2)
                continue

            parsed_expected = parse_date(expected_input)
            if not parsed_expected:
                print("Invalid expected delivery date format.")
                time.sleep(2)
                continue

            tracking_number = tracking_number_input
            expected_delivery_date = parsed_expected

        cursor = db.cursor()
        cursor.execute(
            """
            UPDATE supplier_order
            SET so_status = %s,
                tracking_number = %s,
                expected_delivery_date = %s,
                received_date = %s
            WHERE so_id = %s AND supplier_id = %s
            """,
            (new_status, tracking_number, expected_delivery_date, received_date, so_id, supplier_id)
        )
        db.commit()
        cursor.close()

        print(f"Supplier order {so_id} updated to status '{new_status}'.")
        logger.info(f"Supplier '{supplier_id}' updated supplier order '{so_id}' to '{new_status}'.")
        time.sleep(2)
        return


def view_supplied_products(supplier_id):
    while True:
        clear_screen()
        print("Products You Supply")
        print("-----------------------------")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                s.supplier_id,
                s.prod_id,
                s.supplier_price,
                p.name,
                p.description,
                p.units,
                p.unit_type,
                p.category_id,
                (
                    SELECT MIN(s2.supplier_price)
                    FROM supplies s2
                    WHERE s2.prod_id = s.prod_id
                      AND s2.supplier_id <> s.supplier_id
                ) AS lowest_competitor_price
            FROM supplies s
            JOIN product p ON s.prod_id = p.prod_id
            WHERE s.supplier_id = %s
            ORDER BY s.prod_id DESC
            """,
            (supplier_id,)
        )
        supplied_products = cursor.fetchall()
        cursor.close()

        if not supplied_products:
            print("You are not currently supplying any products.")
            input("\nPress Enter to return...")
            return

        print(
            f"| {'Supplier ID':<11} "
            f"| {'Product ID':<10} "
            f"| {'Product Name':<20} "
            f"| {'Your Price':<12} "
            f"| {'Lowest Competitor':<18} "
            f"| {'Units':<8} "
            f"| {'Unit Type':<12} "
            f"| {'Category':<10} |"
        )
        print("-" * 125)

        for supply in supplied_products:
            supplier_price = float(supply["supplier_price"]) if supply["supplier_price"] is not None else 0.0
            competitor_text = (
                f"${float(supply['lowest_competitor_price']):.2f}"
                if supply["lowest_competitor_price"] is not None
                else "None"
            )

            print(
                f"| {supply['supplier_id']:<11} "
                f"| {supply['prod_id']:<10} "
                f"| {supply['name'][:20]:<20} "
                f"| ${supplier_price:<11.2f} "
                f"| {competitor_text:<18} "
                f"| {str(supply['units']) if supply['units'] is not None else 'NULL':<8} "
                f"| {(supply['unit_type'] or 'NULL'):<12} "
                f"| {str(supply['category_id']) if supply['category_id'] is not None else 'NULL':<10} |"
            )

        input("\nPress Enter to return...")


def add_supplied_product(supplier_id):
    while True:
        clear_screen()
        print("Add Product You Supply")
        print("-----------------------------")

        print("Existing Product Catalog:")
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                p.prod_id,
                p.name,
                p.category_id,
                (
                    SELECT MIN(s.supplier_price)
                    FROM supplies s
                    WHERE s.prod_id = p.prod_id
                ) AS lowest_supplier_price,
                EXISTS (
                    SELECT 1
                    FROM supplies sx
                    WHERE sx.prod_id = p.prod_id
                      AND sx.supplier_id = %s
                ) AS already_supply
            FROM product p
            ORDER BY p.name ASC
            """,
            (supplier_id,)
        )
        products = cursor.fetchall()
        cursor.close()

        if not products:
            print("No products found in catalog yet.")
        else:
            print(
                f"| {'Product ID':<10} "
                f"| {'Product Name':<20} "
                f"| {'Category ID':<12} "
                f"| {'Lowest Supplier Price':<22} "
                f"| {'You Supply?':<11} |"
            )
            print("-" * 90)

            for product in products:
                lowest_price_text = (
                    f"${float(product['lowest_supplier_price']):.2f}"
                    if product["lowest_supplier_price"] is not None
                    else "None"
                )
                already_supply_text = "Yes" if product["already_supply"] else "No"

                print(
                    f"| {product['prod_id']:<10} "
                    f"| {product['name'][:20]:<20} "
                    f"| {str(product['category_id']) if product['category_id'] is not None else 'NULL':<12} "
                    f"| {lowest_price_text:<22} "
                    f"| {already_supply_text:<11} |"
                )

        print("\nOptions:")
        print("1. Supply an Existing Product")
        print("2. Add a New Product to Catalog")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            prod_id_text = input("Enter Product ID to supply: ").strip()
            price_text = input("Enter your supplier price for this product: ").strip()

            if not prod_id_text.isdigit():
                print("Invalid Product ID.")
                time.sleep(2)
                continue

            try:
                supplier_price = float(price_text)
                if supplier_price < 0:
                    raise ValueError
            except ValueError:
                print("Supplier price must be a non-negative number.")
                time.sleep(2)
                continue

            prod_id = int(prod_id_text)

            product = get_product(prod_id)
            if not product:
                print("Product ID does not exist.")
                time.sleep(2)
                continue

            existing_supply = get_supplier_product(supplier_id, prod_id)
            if existing_supply:
                print("You already supply this product.")
                time.sleep(2)
                continue

            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO supplies (supplier_id, prod_id, supplier_price)
                VALUES (%s, %s, %s)
                """,
                (supplier_id, prod_id, supplier_price)
            )
            db.commit()
            cursor.close()

            print(f"Product {prod_id} added to your supplied products.")
            logger.info(f"Supplier '{supplier_id}' added existing product '{prod_id}' to supplies.")
            time.sleep(2)

        elif choice == "2":
            print("\nAvailable Categories:")
            categories = get_all_categories()

            if not categories:
                print("No categories exist yet. Cannot add a new product.")
                time.sleep(2)
                continue

            print(
                f"| {'Category ID':<12} "
                f"| {'Category Name':<20} "
                f"| {'Description':<40} |"
            )
            print("-" * 80)

            for category in categories:
                description_text = (category["description"] or "NULL")[:40]
                print(
                    f"| {category['cat_id']:<12} "
                    f"| {category['name'][:20]:<20} "
                    f"| {description_text:<40} |"
                )

            print("\nEnter new product details:")
            name = input("Product name: ").strip()
            description = input("Description: ").strip()
            category_id_text = input("Pick the category that fits best (enter Category ID): ").strip()
            units_text = input("Units (optional): ").strip()
            unit_type = input("Unit type (optional): ").strip()
            supplier_price_text = input("Your supplier price: ").strip()

            if not name:
                print("Product name cannot be empty.")
                time.sleep(2)
                continue

            if not category_id_text.isdigit():
                print("Invalid Category ID.")
                time.sleep(2)
                continue

            category_id = int(category_id_text)
            if not category_exists(category_id):
                print("Category ID does not exist.")
                time.sleep(2)
                continue

            try:
                supplier_price = float(supplier_price_text)
                if supplier_price < 0:
                    raise ValueError
            except ValueError:
                print("Supplier price must be a non-negative number.")
                time.sleep(2)
                continue

            if units_text:
                try:
                    units = float(units_text)
                    if units < 0:
                        raise ValueError
                except ValueError:
                    print("Units must be a non-negative number.")
                    time.sleep(2)
                    continue
            else:
                units = None

            initial_unit_price = round(supplier_price * 1.15, 2)

            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO product (category_id, name, description, unit_price, units, unit_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (category_id, name, description or None, initial_unit_price, units, unit_type or None)
            )
            db.commit()
            new_prod_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO supplies (supplier_id, prod_id, supplier_price)
                VALUES (%s, %s, %s)
                """,
                (supplier_id, new_prod_id, supplier_price)
            )
            db.commit()
            cursor.close()

            print(f"New product '{name}' added and linked to your supplies.")
            logger.info(f"Supplier '{supplier_id}' created new product '{name}' and added it to supplies.")
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

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.supplier_id, s.prod_id, s.supplier_price, p.name
            FROM supplies s
            JOIN product p ON s.prod_id = p.prod_id
            WHERE s.supplier_id = %s
            ORDER BY s.prod_id DESC
            """,
            (supplier_id,)
        )
        supplied_products = cursor.fetchall()
        cursor.close()

        if not supplied_products:
            print("You are not currently supplying any products.")
            input("\nPress Enter to return...")
            return

        print("Your current supplied products:")
        print(
            f"| {'Product ID':<10} "
            f"| {'Product Name':<20} "
            f"| {'Supplier Price':<15} |"
        )
        print("-" * 55)

        for supply in supplied_products:
            supplier_price = float(supply["supplier_price"]) if supply["supplier_price"] is not None else 0.0
            print(
                f"| {supply['prod_id']:<10} "
                f"| {supply['name'][:20]:<20} "
                f"| ${supplier_price:<14.2f} |"
            )

        prod_id_text = input("Enter Product ID to remove (or press Enter to cancel): ").strip()
        if not prod_id_text:
            return

        if not prod_id_text.isdigit():
            print("Invalid Product ID.")
            time.sleep(2)
            continue

        prod_id = int(prod_id_text)

        existing = get_supplier_product(supplier_id, prod_id)
        if not existing:
            print("You do not supply this product.")
            time.sleep(2)
            continue

        confirmation = input(f"Are you sure you want to stop supplying product {prod_id}? (y/n): ").strip().lower()
        if confirmation != "y":
            print("Operation cancelled.")
            time.sleep(2)
            continue

        cursor = db.cursor()
        cursor.execute(
            """
            DELETE FROM supplies
            WHERE supplier_id = %s AND prod_id = %s
            """,
            (supplier_id, prod_id)
        )
        db.commit()
        cursor.close()

        print(f"Product {prod_id} removed from your supplied products list.")
        logger.info(f"Supplier '{supplier_id}' removed product '{prod_id}' from supplies.")
        time.sleep(2)


def view_pending_supplier_orders(supplier_id):
    while True:
        clear_screen()
        print("Pending / Active Supplier Orders")
        print("-----------------------------")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT supplier_id, so_id, date_of_order, total_amount, payment_method,
            so_status AS status, expected_delivery_date, received_date, tracking_number,
                   st_id, list_id
            FROM supplier_order
            WHERE supplier_id = %s
          AND LOWER(COALESCE(so_status, 'pending')) <> 'received'
            ORDER BY date_of_order DESC, so_id DESC
            """,
            (supplier_id,)
        )
        orders = cursor.fetchall()
        cursor.close()

        if not orders:
            print("No pending/active supplier orders found.")
            input("\nPress Enter to return...")
            return

        print_supplier_orders_table(orders)

        print("\nOptions:")
        print("1. View Supplier Order Details")
        print("2. Update Supplier Order Status")
        print("3. Return")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            so_id = input("Enter Supplier Order ID: ").strip()
            if not so_id.isdigit():
                print("Invalid Supplier Order ID.")
                time.sleep(2)
                continue
            view_supplier_order_details(int(so_id), supplier_id)

        elif choice == "2":
            so_id = input("Enter Supplier Order ID: ").strip()
            if not so_id.isdigit():
                print("Invalid Supplier Order ID.")
                time.sleep(2)
                continue
            update_supplier_order_status(int(so_id), supplier_id)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_total_sales_by_products(supplier_id):
    while True:
        clear_screen()
        print("Total Sales from Your Products")
        print("-----------------------------")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT p.prod_id, p.name,
                   COALESCE(SUM(sc.quantity * sc.cost_at_purchase), 0) AS total_sales
            FROM so_contains sc
            JOIN product p ON sc.prod_id = p.prod_id
            WHERE sc.supplier_id = %s
            GROUP BY p.prod_id, p.name
            ORDER BY total_sales DESC, p.name ASC
            """,
            (supplier_id,)
        )
        sales_data = cursor.fetchall()
        cursor.close()

        if not sales_data:
            print("No sales data found for your products.")
            input("\nPress Enter to return...")
            return

        print(
            f"| {'Product ID':<10} "
            f"| {'Product Name':<20} "
            f"| {'Total Sales':<15} |"
        )
        print("-" * 55)

        for data in sales_data:
            total_sales = float(data["total_sales"]) if data["total_sales"] is not None else 0.0
            print(
                f"| {data['prod_id']:<10} "
                f"| {data['name'][:20]:<20} "
                f"| ${total_sales:<14.2f} |"
            )

        logger.info(f"Supplier '{supplier_id}' viewed total sales by products.")
        input("\nPress Enter to return...")
        return
