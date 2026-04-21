import time

from db_connector import db
from logger_config import get_logger
from utils import print_load, clear_screen

logger = get_logger(__name__)


def _fetch_all(query, params=None):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    return cursor.fetchall()


def _fetch_one(query, params=None):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    return cursor.fetchone()


def _execute(query, params=None):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    db.commit()


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
            f"Price: ${row['unit_price']:.2f} | "
            f"Stock: {row['quantity']} | "
            f"Size: {size_text}"
        )


def inventory_manager_menu(store_id, employee_id):
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
        print("8. View Product Catalog")
        print("9. Logout")

        choice = input("\nPlease select an option (1-8): ").strip()

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
            print_load("Goodbye",1.2)
            break
        else:
            print("\nInvalid option. Please try again.")


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
                sp.supplier_price
            FROM supplies AS sp
            JOIN product AS p
                ON sp.prod_id = p.prod_id
            JOIN category AS c
                ON p.category_id = c.cat_id
            JOIN supplier AS sup
                ON sp.supplier_id = sup.supplier_id
            ORDER BY p.name, sup.supplier_name
            """
        )
        if not rows:
            print("No supplier products found.")
        else:
            for row in rows:
                print(
                    f"Product ID: {row['prod_id']} | "
                    f"{row['product_name']} | "
                    f"Category: {row['category_name']} | "
                    f"Supplier: {row['supplier_name']} ({row['supplier_id']}) | "
                    f"Supplier Price: ${row['supplier_price']:.2f}"
                )

        
        print("\n1. Add a product to restock list")
        print("2. Return to the previous menu.")

        choice = input("Please select an option (1-2): ").strip()

        if choice == "1":
            if(not rows):
                print("No Supplier Products")
                time.sleep(2)
                return
            product_id = input("Enter Product ID: ").strip()
            quantity = input("Enter quantity: ").strip()

            add_product_to_restock_list(product_id, quantity, store_id, employee_id)

        elif choice == "2":
            return

        else:
            print("Invalid option.")
            time.sleep(2)


def add_product_to_restock_list(product_id, quantity, store_id, employee_id):
    cursor = db.cursor(dictionary=True)
    print("\nAdding product to restock list...")

    if not product_id.isdigit() or not quantity.isdigit() or int(quantity) <= 0:
        print("Product ID and quantity must be valid positive integers.")
        time.sleep(2)
        return

    product = _fetch_one(
        """
        SELECT prod_id
        FROM product
        WHERE prod_id = %s
        """,
        (int(product_id),),
    )
    if not product:
        print("That product does not exist.")
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
        _execute(
            """
            INSERT INTO restock_list (store_id, created_by, approved_by, restock_status, created_at, approved_at)
            VALUES (%s, %s, NULL, 'pending', CURRENT_TIMESTAMP, NULL)
            """,
            (store_id, employee_id),
        )
        list_id = cursor.lastrowid
    else:
        list_id = restock_list["list_id"]

    existing_item = _fetch_one(
        """
        SELECT quantity
        FROM restock_contains
        WHERE list_id = %s AND prod_id = %s
        """,
        (list_id, int(product_id)),
    )
    if existing_item:
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
            INSERT INTO restock_contains (list_id, prod_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (list_id, int(product_id), int(quantity)),
        )

    print("Product added to restock list.")
    logger.info(
        f"Employee {employee_id} added product {product_id} "
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
                p.name AS product_name,
                rc.quantity
            FROM restock_list AS rl
            JOIN restock_contains AS rc
                ON rl.list_id = rc.list_id
            JOIN product AS p
                ON rc.prod_id = p.prod_id
            WHERE rl.store_id = %s
              AND rl.restock_status = 'pending'
            ORDER BY rl.created_at DESC, p.name
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
                    f"Quantity Requested: {row['quantity']}"
                )

        print("1. Remove a product from restock list")
        print("2. Return to the previous menu.")
        choice = input("\nPlease select an option (1-2): ").strip()

        if choice == "1":
            if(not rows):
                print("No Products in Restock List")
                time.sleep(2)
                return
            product_id = input("Enter Product ID: ").strip()
            remove_product_from_restock_list(product_id, store_id, employee_id)
        elif choice == "2":
            return
        else:
            print("Invalid option.")
            time.sleep(2)


def remove_product_from_restock_list(product_id, store_id, employee_id):
    print("\nRemoving product from restock list...")
    if not product_id.isdigit():
        print("Product ID must be numeric.")
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
        WHERE list_id = %s AND prod_id = %s
        """,
        (restock_list["list_id"], int(product_id)),
    )
    logger.info(
        f"Product {product_id} removed from restock list for store "
        f"{store_id} by employee {employee_id}."
    )
    time.sleep(2)


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
        f"Product {product_id} (quantity: {quantity}) added to inventory "
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
                status,
                expected_delivery_date,
                tracking_number
            FROM supplier_order
            WHERE st_id = %s
              AND status = 'delivered'
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
        return

    supplier_order = _fetch_one(
        """
        SELECT so_id, supplier_id, st_id, status, list_id
        FROM supplier_order
        WHERE so_id = %s AND supplier_id = %s
        """,
        (int(so_id), int(supplier_id)),
    )
    if not supplier_order or supplier_order["st_id"] != store_id:
        print("That supplier order does not belong to this store.")
        time.sleep(2)
        return
    if supplier_order["status"] != "delivered":
        print("Only supplier orders with status 'delivered' can be received.")
        time.sleep(2)
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
            if existing_stock:
                cursor.execute(
                    """
                    UPDATE stocks
                    SET quantity = quantity + %s
                    WHERE store_id = %s AND prod_id = %s
                    """,
                    (item["quantity"], store_id, item["prod_id"]),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO stocks (store_id, prod_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (store_id, item["prod_id"], item["quantity"]),
                )

            cursor.execute(
                """
                UPDATE product
                SET unit_price = ROUND(%s * 1.15, 2)
                WHERE prod_id = %s
                """,
                (item["cost_at_purchase"], item["prod_id"]),
            )

        cursor.execute(
            """
            UPDATE supplier_order
            SET status = 'received',
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
        return

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
        SELECT status
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
    else:
        next_status = "ordered"

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
            print(
                f"Product ID: {row['prod_id']} | "
                f"{row['product_name']} | "
                f"Category: {row['category_name']} | "
                f"Price: ${row['unit_price']:.2f} | "
                f"Size: {size_text} | "
                f"Description: {row['description']}"
            )

    input("\nPress Enter to return...")