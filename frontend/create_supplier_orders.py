# SJSU CMPE 138 SPRING 2026 TEAM6
from time import sleep
from utils import clear_screen, reconnect
from logger_config import get_logger
from db_connector import db
from datetime import date

logger = get_logger(__name__)

# converts a restock list that contains multiplier products from different suppliers into individual supplier orders 
# to be sent to suppliers
def create_supplier_orders_from_restock_list(list_id, store_id):
    print(f"\nConverting Restock List {list_id} into Supplier Orders...")
    print("----------------------------------------------------------")
    reconnect()
    cursor = db.cursor(dictionary=True)

    try:
        # Get all approved/requested items from this restock list,
        # including the supplier that was explicitly chosen.
        query = """
            SELECT rc.list_id, rc.prod_id, rc.supplier_id, rc.quantity, sp.supplier_price
            FROM restock_contains rc
            JOIN supplies sp
              ON rc.prod_id = sp.prod_id
             AND rc.supplier_id = sp.supplier_id
            WHERE rc.list_id = %s
            ORDER BY rc.supplier_id, rc.prod_id
        """
        cursor.execute(query, (list_id,))
        restock_items = cursor.fetchall()

        if not restock_items:
            print(f"No items found in restock list {list_id}")
            cursor.close()
            return False

        # Group products by the chosen supplier
        supplier_orders = {}
        for item in restock_items:
            supplier_id = item["supplier_id"]
            prod_id = item["prod_id"]
            quantity = int(item["quantity"])
            supplier_price = float(item["supplier_price"])

            if supplier_id not in supplier_orders:
                supplier_orders[supplier_id] = []

            supplier_orders[supplier_id].append((prod_id, quantity, supplier_price))

        if not supplier_orders:
            print("No supplier orders could be created from this restock list.")
            cursor.close()
            return False

        today = date.today()

        # Create one supplier order per chosen supplier
        for supplier_id, products in supplier_orders.items():
            total_amount = 0.0
            for prod_id, quantity, price in products:
                total_amount += quantity * price

            # Since so_id is NOT auto-increment in your schema,
            # generate the next so_id for this supplier.
            cursor.execute(
                """
                SELECT COALESCE(MAX(so_id), 0) + 1 AS next_so_id
                FROM supplier_order
                WHERE supplier_id = %s
                """,
                (supplier_id,)
            )
            row = cursor.fetchone()
            so_id = row["next_so_id"]

            # Insert supplier_order using the chosen supplier and tie it to the restock list
            query = """
                INSERT INTO supplier_order (
                    so_id,
                    supplier_id,
                    date_of_order,
                    total_amount,
                    payment_method,
                    so_status,
                    expected_delivery_date,
                    received_date,
                    tracking_number,
                    st_id,
                    list_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    so_id,
                    supplier_id,
                    today,
                    round(total_amount, 2),
                    "credit_card",
                    "pending",
                    None,
                    None,
                    None,
                    store_id,
                    list_id,
                ),
            )

            # Insert line items
            query = """
                INSERT INTO so_contains (so_id, supplier_id, prod_id, quantity, cost_at_purchase)
                VALUES (%s, %s, %s, %s, %s)
            """

            values = []
            for prod_id, quantity, price in products:
                values.append((so_id, supplier_id, prod_id, quantity, price))

            cursor.executemany(query, values)

            logger.info(
                f"Supplier order '{so_id}' created for supplier {supplier_id} "
                f"using restock list {list_id} for store {store_id}"
            )
            print(
                f"Supplier order '{so_id}' created for supplier {supplier_id} "
                f"with total amount ${total_amount:.2f}"
            )

        # Mark restock list as ordered after supplier orders are created
        cursor.execute(
            """
            UPDATE restock_list
            SET restock_status = 'ordered'
            WHERE list_id = %s AND store_id = %s
            """,
            (list_id, store_id),
        )

        db.commit()
        cursor.close()

        print("Supplier orders created successfully from the approved restock list.")
        sleep(3)
        return True

    except Exception as e:
        db.rollback()
        cursor.close()
        logger.exception(
            f"Failed to create supplier orders from restock list {list_id} for store {store_id}"
        )
        print(f"An error occurred while creating supplier orders: {e}")
        sleep(3)
        return False
