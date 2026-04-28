# SJSU CMPE 138 SPRING 2026 TEAM6
import time

from db_connector import db
from logger_config import get_logger
from utils import print_load, clear_screen, reconnect

logger = get_logger(__name__)

RETAIL_MARKUP = 1.15


def _fetch_all(query, params=None):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    return rows

def _fetch_one(query, params=None):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    row = cursor.fetchone()
    cursor.close()
    return row

def _execute(query, params=None):
    cursor = db.cursor()
    cursor.execute(query, params or ())
    db.commit()
    cursor.close()

def _execute_insert(query, params=None):
    cursor = db.cursor()
    cursor.execute(query, params or ())
    db.commit()
    last_id = cursor.lastrowid
    cursor.close()
    return last_id

def _print_inventory_rows(rows):
    if not rows:
        print("No inventory rows found.")
        return

    for row in rows:
        size_text = f"{row['units'] or 'n/a'} {row['unit_type'] or ''}".strip()
        print(
            f"Product ID: {row['prod_id']} | "
            f"{row['product_name']} | "
            f"Category: {row['category_name']} | "
            f"Price: ${float(row['unit_price']):.2f} | "
            f"Stock: {row['quantity']} | "
            f"Size: {size_text}"
        )

def _calculate_weighted_price(current_qty, current_price, incoming_qty, incoming_cost):
    incoming_sell_price = round(float(incoming_cost) * RETAIL_MARKUP, 2)

    if current_qty is None or current_qty <= 0 or current_price is None:
        return incoming_sell_price

    total_qty = current_qty + incoming_qty
    if total_qty <= 0:
        return incoming_sell_price

    weighted_average = (
        (float(current_qty) * float(current_price))
        + (float(incoming_qty) * float(incoming_sell_price))
    ) / float(total_qty)

    return round(weighted_average, 2)

#landing page/menu for invneotry manager
def inventory_manager_menu(store_id, employee_id):
    while True:
        reconnect()
        clear_screen()
        print("\nInventory Manager Menu:")
        print("1. View Inventory")
        print("2. View supplier products")
        print("3. View restock list")
        print("4. View past restock lists")
        print("5. Remove a product from inventory")
        print("6. Add a product to inventory")
        print("7. Receive Supplier Order")
        print("8. View Product Catalog")
        print("9. View Supplier Orders")
        print("10. Logout")

        choice = input("\nPlease select an option (1-10): ").strip()

        if choice == "1":
            view_inventory(store_id)
        elif choice == "2":
            view_supplier_products(store_id, employee_id)
        elif choice == "3":
            view_restock_list(store_id, employee_id)
        elif choice == "4":
            view_past_restock_lists(store_id)
        elif choice == "5":
            remove_product(store_id, employee_id)
        elif choice == "6":
            add_new_product(store_id, employee_id)
        elif choice == "7":
            receive_supplier_orders_menu(store_id, employee_id)
        elif choice == "8":
            view_products()
        elif choice == "9":
            view_supplier_orders_for_store(store_id)
        elif choice == "10":
            print_load("Goodbye", 1.2)
            break
        else:
            print("\nInvalid option. Please try again.")
            time.sleep(2)

def view_inventory(store_id):
    clear_screen()
    print("\nViewing inventory...")
    rows = _fetch_all(
        """
        SELECT
            s.prod_id,
            p.name AS product_name,
            c.name AS category_name,
            p.unit_price,
            p.units,
            p.unit_type,
            s.quantity
        FROM stocks AS s
        JOIN product AS p
            ON s.prod_id = p.prod_id
        JOIN category AS c
            ON p.category_id = c.cat_id
        WHERE s.store_id = %s
        ORDER BY p.name
        """,
        (store_id,),
    )
    _print_inventory_rows(rows)

    print("Press Enter to return to the menu.")
    input()

def view_supplier_products(store_id, employee_id):
    print("\nViewing supplier products...")
    time.sleep(1)

    while True:
        clear_screen()
        rows = _fetch_all(
            """
            SELECT
                p.prod_id,
                p.name AS product_name,
                c.name AS category_name,
                sp.supplier_id,
                sup.supplier_name,
                sp.supplier_price,
                (
                    SELECT MIN(sp2.supplier_price)
                    FROM supplies sp2
                    WHERE sp2.prod_id = sp.prod_id
                ) AS lowest_supplier_price
            FROM supplies AS sp
            JOIN product AS p
                ON sp.prod_id = p.prod_id
            JOIN category AS c
                ON p.category_id = c.cat_id
            JOIN supplier AS sup
                ON sp.supplier_id = sup.supplier_id
            ORDER BY p.name, sp.supplier_price ASC, sup.supplier_name
            """
        )

        if not rows:
            print("No supplier products found.")
        else:
            for row in rows:
                is_lowest = float(row["supplier_price"]) == float(row["lowest_supplier_price"])
                cheapest_text = "CHEAPEST" if is_lowest else ""
                print(
                    f"Product ID: {row['prod_id']} | "
                    f"{row['product_name']} | "
                    f"Category: {row['category_name']} | "
                    f"Supplier: {row['supplier_name']} ({row['supplier_id']}) | "
                    f"Supplier Price: ${float(row['supplier_price']):.2f} | "
                    f"Lowest Price: ${float(row['lowest_supplier_price']):.2f} {cheapest_text}"
                )

        print("\n1. Add a product to restock list")
        print("2. Return to the previous menu.")

        choice = input("Please select an option (1-2): ").strip()

        if choice == "1":
            if not rows:
                print("No supplier products available.")
                time.sleep(2)
                return

            product_id = input("Enter Product ID: ").strip()
            supplier_id = input("Enter Supplier ID for that product: ").strip()
            quantity = input("Enter quantity: ").strip()

            add_product_to_restock_list(product_id, supplier_id, quantity, store_id, employee_id)

        elif choice == "2":
            return

        else:
            print("Invalid option.")
            time.sleep(2)

def add_product_to_restock_list(product_id, supplier_id, quantity, store_id, employee_id):
    print("\nAdding product to restock list...")

    if (
        not product_id.isdigit()
        or not supplier_id.isdigit()
        or not quantity.isdigit()
        or int(quantity) <= 0
    ):
        print("Product ID, Supplier ID, and quantity must be valid positive integers.")
        time.sleep(2)
        return

    supply_row = _fetch_one(
        """
        SELECT sp.prod_id, sp.supplier_id, sp.supplier_price, p.name AS product_name
        FROM supplies sp
        JOIN product p ON sp.prod_id = p.prod_id
        WHERE sp.prod_id = %s AND sp.supplier_id = %s
        """,
        (int(product_id), int(supplier_id)),
    )

    if not supply_row:
        print("That supplier does not supply that product.")
        time.sleep(2)
        return

    restock_list = _fetch_one(
        """
        SELECT list_id
        FROM restock_list
        WHERE store_id = %s AND restock_status = 'pending'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (store_id,),
    )

    if not restock_list:
        list_id = _execute_insert(
            """
            INSERT INTO restock_list (store_id, created_by, approved_by, restock_status, created_at, approved_at)
            VALUES (%s, %s, NULL, 'pending', CURRENT_TIMESTAMP, NULL)
            """,
            (store_id, employee_id),
        )
    else:
        list_id = restock_list["list_id"]

    existing_item = _fetch_one(
        """
        SELECT quantity, supplier_id
        FROM restock_contains
        WHERE list_id = %s AND prod_id = %s
        """,
        (list_id, int(product_id)),
    )

    if existing_item:
        if int(existing_item["supplier_id"]) != int(supplier_id):
            print(
                "This product is already on the current restock list with a different supplier. "
                "Create a new list if you want the same product from another supplier."
            )
            time.sleep(3)
            return

        _execute(
            """
            UPDATE restock_contains
            SET quantity = quantity + %s
            WHERE list_id = %s AND prod_id = %s
            """,
            (int(quantity), list_id, int(product_id)),
        )
    else:
        _execute(
            """
            INSERT INTO restock_contains (list_id, prod_id, supplier_id, quantity)
            VALUES (%s, %s, %s, %s)
            """,
            (list_id, int(product_id), int(supplier_id), int(quantity)),
        )

    print(f"Product {product_id} added to restock list using supplier {supplier_id}.")
    logger.info(
        f"Employee {employee_id} added product {product_id} from supplier {supplier_id} "
        f"(quantity: {quantity}) to restock list for store {store_id}."
    )
    time.sleep(2)

def view_restock_list(store_id, employee_id):
    while True:
        clear_screen()
        print("\nViewing current restock list...")
        rows = _fetch_all(
            """
            SELECT
                rl.list_id,
                rl.created_at,
                rl.restock_status,
                rc.prod_id,
                rc.supplier_id,
                p.name AS product_name,
                s.supplier_name,
                rc.quantity
            FROM restock_list AS rl
            JOIN restock_contains AS rc
                ON rl.list_id = rc.list_id
            JOIN product AS p
                ON rc.prod_id = p.prod_id
            JOIN supplier AS s
                ON rc.supplier_id = s.supplier_id
            WHERE rl.store_id = %s
              AND rl.restock_status = 'pending'
            ORDER BY rl.created_at DESC, p.name, s.supplier_name
            """,
            (store_id,),
        )

        if not rows:
            print("No pending restock list found.")
        else:
            current_list_id = rows[0]["list_id"]
            print(f"Pending Restock List ID: {current_list_id}")
            for row in rows:
                print(
                    f"Product ID: {row['prod_id']} | "
                    f"{row['product_name']} | "
                    f"Supplier: {row['supplier_name']} ({row['supplier_id']}) | "
                    f"Quantity Requested: {row['quantity']}"
                )

        print("1. Remove a product from restock list")
        print("2. Return to the previous menu.")
        choice = input("\nPlease select an option (1-2): ").strip()

        if choice == "1":
            if not rows:
                print("No products in restock list.")
                time.sleep(2)
                return
            product_id = input("Enter Product ID: ").strip()
            supplier_id = input("Enter Supplier ID: ").strip()
            remove_product_from_restock_list(product_id, supplier_id, store_id, employee_id)
        elif choice == "2":
            return
        else:
            print("Invalid option.")
            time.sleep(2)

def remove_product_from_restock_list(product_id, supplier_id, store_id, employee_id):
    print("\nRemoving product from restock list...")

    if not product_id.isdigit() or not supplier_id.isdigit():
        print("Product ID and Supplier ID must be numeric.")
        time.sleep(2)
        return

    restock_list = _fetch_one(
        """
        SELECT list_id
        FROM restock_list
        WHERE store_id = %s AND restock_status = 'pending'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (store_id,),
    )
    if not restock_list:
        print("No pending restock list exists for this store.")
        time.sleep(2)
        return

    _execute(
        """
        DELETE FROM restock_contains
        WHERE list_id = %s AND prod_id = %s AND supplier_id = %s
        """,
        (restock_list["list_id"], int(product_id), int(supplier_id)),
    )

    print("Product removed from restock list.")
    logger.info(
        f"Product {product_id} from supplier {supplier_id} removed from restock list "
        f"for store {store_id} by employee {employee_id}."
    )
    time.sleep(2)

def view_supplier_orders_for_store(store_id):
    clear_screen()
    print("Supplier Orders for This Store")
    print("-----------------------------")

    rows = _fetch_all(
        """
        SELECT
            so.so_id,
            so.supplier_id,
            s.supplier_name,
            so.list_id,
            so.date_of_order,
            so.so_status AS status,
            so.expected_delivery_date,
            so.received_date,
            so.tracking_number,
            so.total_amount
        FROM supplier_order so
        JOIN supplier s
            ON so.supplier_id = s.supplier_id
        WHERE so.st_id = %s
        ORDER BY so.date_of_order DESC, so.so_id DESC
        """,
        (store_id,),
    )

    if not rows:
        print("No supplier orders found for this store.")
        input("\nPress Enter to return...")
        return

    for row in rows:
        print(
            f"SO ID: {row['so_id']} | "
            f"Supplier: {row['supplier_name']} ({row['supplier_id']}) | "
            f"List ID: {row['list_id']} | "
            f"Order Date: {row['date_of_order']} | "
            f"Status: {row['status']} | "
            f"Expected: {row['expected_delivery_date'] or 'N/A'} | "
            f"Received: {row['received_date'] or 'N/A'} | "
            f"Tracking: {row['tracking_number'] or 'N/A'} | "
            f"Total: ${float(row['total_amount']):.2f}"
        )

    input("\nPress Enter to return...")

def view_past_restock_lists(store_id):
    clear_screen()
    print("\nViewing past restock lists...")
    rows = _fetch_all(
        """
        SELECT list_id, restock_status, created_at, approved_at, approved_by
        FROM restock_list
        WHERE store_id = %s AND restock_status <> 'pending'
        ORDER BY created_at DESC
        """,
        (store_id,),
    )
    if not rows:
        print("No past restock lists found.")
    else:
        for row in rows:
            print(
                f"List ID: {row['list_id']} | "
                f"Status: {row['restock_status']} | "
                f"Created: {row['created_at']} | "
                f"Approved At: {row['approved_at']} | "
                f"Approved By: {row['approved_by']}"
            )

    input("\nPress Enter to continue...")

def remove_product(store_id, employee_id):
    print("\nRemove product from inventory")

    product_id = input("Enter Product ID: ").strip()
    if not product_id.isdigit():
        print("Product ID must be numeric.")
        time.sleep(2)
        return

    existing_stock = _fetch_one(
        """
        SELECT quantity
        FROM stocks
        WHERE store_id = %s AND prod_id = %s
        """,
        (store_id, int(product_id)),
    )

    if not existing_stock:
        print("That product does not exist in this store's inventory.")
        time.sleep(2)
        return

    _execute(
        """
        DELETE FROM stocks
        WHERE store_id = %s AND prod_id = %s
        """,
        (store_id, int(product_id)),
    )

    print("Product removed from inventory.")
    logger.info(
        f"Product {product_id} removed from inventory for store "
        f"{store_id} by employee {employee_id}."
    )
    time.sleep(2)

def add_new_product(store_id, employee_id):
    print("\nAdd product to inventory")

    product_id = input("Enter Product ID: ").strip()
    quantity = input("Enter quantity: ").strip()
    if not product_id.isdigit() or not quantity.isdigit() or int(quantity) <= 0:
        print("Product ID and quantity must be valid positive integers.")
        time.sleep(2)
        return

    product_row = _fetch_one(
        """
        SELECT prod_id, name
        FROM product
        WHERE prod_id = %s
        """,
        (int(product_id),),
    )
    if not product_row:
        print("That product ID does not exist in the product catalog.")
        print("Use 'View Product Catalog' to find a valid Product ID first.")
        time.sleep(3)
        return

    existing_stock = _fetch_one(
        """
        SELECT quantity
        FROM stocks
        WHERE store_id = %s AND prod_id = %s
        """,
        (store_id, int(product_id)),
    )
    if existing_stock:
        _execute(
            """
            UPDATE stocks
            SET quantity = quantity + %s
            WHERE store_id = %s AND prod_id = %s
            """,
            (int(quantity), store_id, int(product_id)),
        )
    else:
        _execute(
            """
            INSERT INTO stocks (store_id, prod_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (store_id, int(product_id), int(quantity)),
        )

    print("Product added/updated in inventory.")
    logger.info(
        f"Product {product_id} - {product_row['name']} (quantity: {quantity}) added to inventory "
        f"for store {store_id} by employee {employee_id}."
    )
    time.sleep(2)

def receive_supplier_orders_menu(store_id, employee_id):
    while True:
        clear_screen()
        print("Receive Supplier Orders")
        print("-----------------------------")

        rows = _fetch_all(
            """
            SELECT
                so_id,
                supplier_id,
                list_id,
                date_of_order,
                so_status AS status,
                expected_delivery_date,
                tracking_number
            FROM supplier_order
            WHERE st_id = %s
            AND so_status = 'delivered'
            ORDER BY expected_delivery_date, so_id
            """,
            (store_id,),
        )

        if not rows:
            print("No delivered supplier orders are waiting to be received.")
        else:
            for row in rows:
                print(
                    f"Supplier Order: ({row['so_id']}, {row['supplier_id']}) | "
                    f"List ID: {row['list_id']} | "
                    f"Ordered: {row['date_of_order']} | "
                    f"Expected: {row['expected_delivery_date']} | "
                    f"Tracking: {row['tracking_number']}"
                )

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
    cursor = db.cursor(dictionary=True)
    print(f"Receiving Supplier Order ({so_id}, {supplier_id})")
    print("---------------------------------------------")

    if not so_id.isdigit() or not supplier_id.isdigit():
        print("Supplier order ID and supplier ID must be numeric.")
        time.sleep(2)
        cursor.close()
        return

    supplier_order = _fetch_one(
        """
        SELECT so_id, supplier_id, st_id, so_status AS status, list_id
        FROM supplier_order
        WHERE so_id = %s AND supplier_id = %s
        """,
        (int(so_id), int(supplier_id)),
    )
    if not supplier_order or supplier_order["st_id"] != store_id:
        print("That supplier order does not belong to this store.")
        time.sleep(2)
        cursor.close()
        return

    if supplier_order["status"] != "delivered":
        print("Only supplier orders with status 'delivered' can be received.")
        time.sleep(2)
        cursor.close()
        return

    items = _fetch_all(
        """
        SELECT prod_id, quantity, cost_at_purchase
        FROM so_contains
        WHERE so_id = %s AND supplier_id = %s
        """,
        (int(so_id), int(supplier_id)),
    )
    if not items:
        print("No line items were found for this supplier order.")
        time.sleep(2)
        cursor.close()
        return

    try:
        for item in items:
            existing_stock = _fetch_one(
                """
                SELECT quantity
                FROM stocks
                WHERE store_id = %s AND prod_id = %s
                """,
                (store_id, item["prod_id"]),
            )

            product_row = _fetch_one(
                """
                SELECT unit_price
                FROM product
                WHERE prod_id = %s
                """,
                (item["prod_id"],),
            )

            current_qty = int(existing_stock["quantity"]) if existing_stock else 0
            current_price = float(product_row["unit_price"]) if product_row and product_row["unit_price"] is not None else None
            incoming_qty = int(item["quantity"])
            incoming_cost = float(item["cost_at_purchase"])

            new_unit_price = _calculate_weighted_price(
                current_qty=current_qty,
                current_price=current_price,
                incoming_qty=incoming_qty,
                incoming_cost=incoming_cost,
            )

            if existing_stock:
                cursor.execute(
                    """
                    UPDATE stocks
                    SET quantity = quantity + %s
                    WHERE store_id = %s AND prod_id = %s
                    """,
                    (incoming_qty, store_id, item["prod_id"]),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO stocks (store_id, prod_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (store_id, item["prod_id"], incoming_qty),
                )

            cursor.execute(
                """
                UPDATE product
                SET unit_price = %s
                WHERE prod_id = %s
                """,
                (new_unit_price, item["prod_id"]),
            )

        cursor.execute(
            """
            UPDATE supplier_order
            SET so_status = 'received',
                received_date = CURDATE()
            WHERE so_id = %s AND supplier_id = %s
            """,
            (int(so_id), int(supplier_id)),
        )

        db.commit()

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to receive supplier order (%s, %s) for store %s.",
            so_id,
            supplier_id,
            store_id,
        )
        print("An error occurred while receiving the supplier order.")
        time.sleep(2)
        cursor.close()
        return

    cursor.close()

    list_id = supplier_order["list_id"]
    sync_restock_list_status(list_id, store_id)

    print(f"Supplier order ({so_id}, {supplier_id}) marked as received.")
    logger.info(
        f"Employee '{employee_id}' received supplier order ({so_id}, {supplier_id}) "
        f"for store '{store_id}'."
    )
    time.sleep(2)

def sync_restock_list_status(list_id, store_id):
    if list_id is None:
        return

    rows = _fetch_all(
        """
        SELECT so_status AS status
        FROM supplier_order
        WHERE list_id = %s AND st_id = %s
        """,
        (list_id, store_id),
    )
    if not rows:
        return

    statuses = {row["status"] for row in rows}
    if statuses == {"received"}:
        next_status = "delivered"
    elif "received" in statuses:
        next_status = "partially_delivered"
    elif "delivered" in statuses or "shipped" in statuses or "pending" in statuses:
        next_status = "ordered"
    else:
        next_status = "approved"

    _execute(
        """
        UPDATE restock_list
        SET restock_status = %s
        WHERE list_id = %s AND store_id = %s
        """,
        (next_status, list_id, store_id),
    )

def view_products():
    clear_screen()
    print("\nProduct Catalog:\n")

    rows = _fetch_all(
        """
        SELECT
            p.prod_id,
            p.name AS product_name,
            p.description,
            c.name AS category_name,
            p.unit_price,
            p.units,
            p.unit_type
        FROM product AS p
        JOIN category AS c
            ON p.category_id = c.cat_id
        ORDER BY p.name
        """
    )

    if not rows:
        print("No products found in catalog.")
    else:
        for row in rows:
            size_text = f"{row['units'] or 'n/a'} {row['unit_type'] or ''}".strip()
            price_text = float(row["unit_price"]) if row["unit_price"] is not None else 0.0
            print(
                f"Product ID: {row['prod_id']} | "
                f"{row['product_name']} | "
                f"Category: {row['category_name']} | "
                f"Price: ${price_text:.2f} | "
                f"Size: {size_text} | "
                f"Description: {row['description']}"
            )

    input("\nPress Enter to return...")
