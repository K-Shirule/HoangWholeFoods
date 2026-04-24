import time
import random
from db_connector import db
from utils import clear_screen, print_load
from logger_config import get_logger

logger = get_logger(__name__)


def floor_employee_page(store_id, employee_id):
    try:
        while True:
            clear_screen()
            print("Welcome to the Floor Employee Page")
            print("Here you can manage in-store orders and process returns.")
            print("1. Process In-Store Order")
            print("2. Process Return Requests")
            print("3. Process In-Store Return")
            print("4. Logout")

            choice = input("Please enter your choice (1-4): ").strip()

            if choice == "1":
                process_instore_orders(store_id, employee_id)

            elif choice == "2":
                process_return_requests(store_id, employee_id)

            elif choice == "3":
                process_instore_return(store_id, employee_id)

            elif choice == "4":
                print("Logging out...")
                logger.info(f"Floor employee '{employee_id}' logged out successfully.")
                time.sleep(2)
                break

            else:
                print("Invalid choice. Please try again.")
                time.sleep(2)
    finally:
        db.close()


def randomize_order(store_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.prod_id, p.name, s.quantity
        FROM product p
        JOIN stocks s ON p.prod_id = s.prod_id
        WHERE s.store_id = %s
          AND s.quantity > 0
        """,
        (store_id,)
    )
    products = cursor.fetchall()
    cursor.close()

    if not products:
        return {}

    max_items = min(5, len(products))
    num_items = random.randint(1, max_items)
    selected_products = random.sample(products, num_items)

    order_items = {}
    for product in selected_products:
        prod_id = product["prod_id"]
        stock_qty = product["quantity"]
        max_qty = min(stock_qty, 10)
        qty = random.randint(1, max_qty)
        order_items[prod_id] = qty

    return order_items


def get_return_summary(order_id, prod_id):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT quantity, price_at_purchase
        FROM order_contains
        WHERE order_id = %s AND prod_id = %s
        """,
        (order_id, prod_id)
    )
    order_item = cursor.fetchone()

    if not order_item:
        cursor.close()
        return None

    cursor.execute(
        """
        SELECT COALESCE(SUM(return_quantity), 0) AS approved_returned_qty
        FROM return_record
        WHERE order_id = %s
          AND prod_id = %s
          AND return_status = 'approved'
        """,
        (order_id, prod_id)
    )
    returned = cursor.fetchone()
    cursor.close()

    approved_returned_qty = returned["approved_returned_qty"] or 0
    original_qty = order_item["quantity"]

    return {
        "original_qty": original_qty,
        "approved_returned_qty": approved_returned_qty,
        "remaining_qty": original_qty - approved_returned_qty,
        "price_at_purchase": float(order_item["price_at_purchase"])
    }


def process_instore_orders(store_id, employee_id):
    while True:
        clear_screen()
        print("Does customer have an account with us? (y/n)")
        has_account = input().strip().lower()

        if has_account not in ("y", "n"):
            print("Please enter 'y' or 'n'.")
            time.sleep(2)
            continue

        customer_id = None
        if has_account == "y":
            customer_email = input("Please enter customer's email: ").strip()

            if not customer_email:
                print("Customer email cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT c_id FROM customer WHERE email = %s",
                (customer_email,)
            )
            result = cursor.fetchone()
            cursor.close()

            if not result:
                print("No customer found with that email.")
                time.sleep(2)
                continue

            customer_id = result["c_id"]
            print(f"Customer found (ID: {customer_id}).")
            time.sleep(1)

        print("Processing In-Store Order")
        print("-----------------------------")

        order_items = randomize_order(store_id)

        if not order_items:
            print("No products with available stock found for this store.")
            time.sleep(2)
            return

        while True:
            clear_screen()
            print("Current Order Items:")
            print("-----------------------------")

            cursor = db.cursor(dictionary=True)
            total = 0.0
            valid_items = {}

            for prod_id, qty in order_items.items():
                cursor.execute(
                    """
                    SELECT p.prod_id, p.name, p.unit_price,
                           s.quantity AS stock_qty
                    FROM product p
                    JOIN stocks s ON p.prod_id = s.prod_id
                    WHERE p.prod_id = %s AND s.store_id = %s
                    """,
                    (prod_id, store_id)
                )
                product = cursor.fetchone()

                if product:
                    line_total = float(product["unit_price"]) * qty
                    total += line_total
                    valid_items[prod_id] = {
                        "qty": qty,
                        "price": float(product["unit_price"]),
                        "name": product["name"]
                    }
                    print(
                        f"  Prod ID: {prod_id}"
                        f"  |  {product['name']}"
                        f"  |  Qty: {qty}"
                        f"  |  Unit Price: ${product['unit_price']:,.2f}"
                        f"  |  Line Total: ${line_total:,.2f}"
                        f"  |  In Stock: {product['stock_qty']}"
                    )
                else:
                    print(f"  Prod ID: {prod_id} - not found in this store's inventory, skipping.")

            cursor.close()

            print(f"\n  Order Total: ${total:,.2f}")
            print("\nOptions:")
            print("1. Proceed to Payment and Finalize Order")
            print("2. Remove an item from the order")
            print("3. Cancel Order and Return to Floor Employee Page")

            choice = input("Please enter your choice (1-3): ").strip()

            if choice == "1":
                if not valid_items:
                    print("No valid items in order. Cannot proceed.")
                    time.sleep(2)
                    continue

                cursor = db.cursor(dictionary=True)

                stock_ok = True
                for prod_id, info in valid_items.items():
                    cursor.execute(
                        "SELECT quantity FROM stocks WHERE store_id = %s AND prod_id = %s",
                        (store_id, prod_id)
                    )
                    stock = cursor.fetchone()

                    if not stock:
                        print(f"Product {prod_id} is not stocked in this store.")
                        stock_ok = False
                        break

                    if stock["quantity"] < info["qty"]:
                        print(f"Insufficient stock for product {prod_id} ({info['name']}). Order cannot proceed.")
                        stock_ok = False
                        break

                if not stock_ok:
                    cursor.close()
                    time.sleep(2)
                    continue

                try:
                    cursor.execute(
                        """
                        INSERT INTO orders
                            (delivery_method, total_amount, order_type, order_status, c_id, st_id, e_id)
                        VALUES
                            ('In_store', %s, 'In_store', 'fulfilled', %s, %s, %s)
                        """,
                        (total, customer_id, store_id, employee_id)
                    )
                    order_id = cursor.lastrowid

                    for prod_id, info in valid_items.items():
                        cursor.execute(
                            """
                            INSERT INTO order_contains (order_id, prod_id, quantity, price_at_purchase)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (order_id, prod_id, info["qty"], info["price"])
                        )
                        cursor.execute(
                            """
                            UPDATE stocks
                            SET quantity = quantity - %s
                            WHERE store_id = %s AND prod_id = %s
                            """,
                            (info["qty"], store_id, prod_id)
                        )
                    clear_screen()
                    print("Payment is processed through a secure third-party provider.")
                    print("1. Credit/Debit Card")
                    print("2. Cash")
                    print("3. Mobile Wallet")
                    payment_choice = input("Please enter your choice (1-3): ").strip()

                    if payment_choice == '1':
                        payment_method = 'Card'
                    elif payment_choice == '2':
                        payment_method = 'Cash'
                    elif payment_choice == '3':
                        payment_method = 'Mobile Wallet'
                    else:
                        print_load("Invalid choice.", 1.5)


                    cursor.execute(
                        """
                        INSERT INTO payments (method, amount, payment_status, order_id)
                        VALUES (%s, %s, 'paid', %s)
                        """,
                        (payment_method, total, order_id)
                    )

                    db.commit()
                except Exception:
                    db.rollback()
                    cursor.close()
                    print("Could not finalize order due to a database error.")
                    time.sleep(2)
                    continue

                cursor.close()

                print(f"\nOrder #{order_id} finalized. Total charged: ${total:,.2f}")
                logger.info(
                    f"Floor employee '{employee_id}' finalized in-store order '{order_id}' "
                    f"for store '{store_id}' (customer_id={customer_id}, total=${total:.2f})."
                )
                time.sleep(3)
                return

            elif choice == "2":
                prod_id = input("Enter Product ID to remove or adjust (leave quantity 0 to remove): ").strip()

                if not prod_id:
                    print("Product ID cannot be empty.")
                    time.sleep(2)
                    continue

                if not prod_id.isdigit():
                    print("Product ID must be numeric.")
                    time.sleep(2)
                    continue

                prod_id = int(prod_id)

                if prod_id not in order_items:
                    print("Product ID not in current order.")
                    time.sleep(2)
                    continue

                new_quantity = input("Enter new quantity (0 to remove): ").strip()

                if not new_quantity:
                    print("Quantity cannot be empty.")
                    time.sleep(2)
                    continue

                if not new_quantity.isdigit():
                    print("Quantity must be a non-negative integer.")
                    time.sleep(2)
                    continue

                new_quantity = int(new_quantity)

                if new_quantity == 0:
                    del order_items[prod_id]
                    print(f"Product {prod_id} removed from order.")
                else:
                    order_items[prod_id] = new_quantity
                    print(f"Product {prod_id} quantity updated to {new_quantity}.")

                time.sleep(1)

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

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT rr.return_id, rr.order_id, rr.prod_id,
                   rr.return_quantity, rr.return_reason,
                   rr.return_status, rr.requested_at,
                   p.name AS product_name
            FROM return_record rr
            JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
            JOIN orders o ON oc.order_id = o.order_id
            JOIN product p ON rr.prod_id = p.prod_id
            WHERE o.st_id = %s
              AND rr.return_status = 'requested'
            ORDER BY rr.requested_at ASC
            """,
            (store_id,)
        )
        returns = cursor.fetchall()
        cursor.close()

        if not returns:
            print("No pending return requests.")
        else:
            for r in returns:
                print(
                    f"  Return ID: {r['return_id']}"
                    f"  |  Order ID: {r['order_id']}"
                    f"  |  Product: {r['product_name']} (ID: {r['prod_id']})"
                    f"  |  Qty: {r['return_quantity']}"
                    f"  |  Reason: {r['return_reason'] or 'N/A'}"
                    f"  |  Requested: {r['requested_at']}"
                )

        print("\nOptions:")
        print("1. View Return Request Details")
        print("2. Approve Return")
        print("3. Deny Return")
        print("4. Return to Floor Employee Page")

        choice = input("Please enter your choice (1-4): ").strip()

        if choice == "1":
            return_id = input("Enter Return ID: ").strip()

            if not return_id:
                print("Return ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT rr.return_id
                FROM return_record rr
                JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
                JOIN orders o ON oc.order_id = o.order_id
                WHERE rr.return_id = %s AND o.st_id = %s
                """,
                (return_id, store_id)
            )
            record = cursor.fetchone()
            cursor.close()

            if not record:
                print("Return request not found for this store.")
                time.sleep(2)
                continue

            view_return_request_details(return_id, store_id)

        elif choice == "2":
            return_id = input("Enter Return ID to approve: ").strip()

            if not return_id:
                print("Return ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT rr.return_id, rr.return_status
                FROM return_record rr
                JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
                JOIN orders o ON oc.order_id = o.order_id
                WHERE rr.return_id = %s AND o.st_id = %s
                """,
                (return_id, store_id)
            )
            record = cursor.fetchone()
            cursor.close()

            if not record:
                print("Return request not found for this store.")
                time.sleep(2)
                continue

            if record["return_status"] != "requested":
                print(f"Return {return_id} is already '{record['return_status']}' and cannot be approved.")
                time.sleep(2)
                continue

            approve_return(return_id, store_id, employee_id)

        elif choice == "3":
            return_id = input("Enter Return ID to deny: ").strip()

            if not return_id:
                print("Return ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT rr.return_id, rr.return_status
                FROM return_record rr
                JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
                JOIN orders o ON oc.order_id = o.order_id
                WHERE rr.return_id = %s AND o.st_id = %s
                """,
                (return_id, store_id)
            )
            record = cursor.fetchone()
            cursor.close()

            if not record:
                print("Return request not found for this store.")
                time.sleep(2)
                continue

            if record["return_status"] != "requested":
                print(f"Return {return_id} is already '{record['return_status']}' and cannot be denied.")
                time.sleep(2)
                continue

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

    if not return_id:
        print("Return ID cannot be empty.")
        input("\nPress Enter to return...")
        return

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT rr.return_id, rr.return_quantity, rr.return_reason,
               rr.return_status, rr.requested_at,
               rr.order_id, rr.prod_id,
               p.name AS product_name,
               oc.quantity AS original_quantity,
               oc.price_at_purchase,
               COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name
        FROM return_record rr
        JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
        JOIN orders o ON oc.order_id = o.order_id
        JOIN product p ON rr.prod_id = p.prod_id
        LEFT JOIN customer c ON o.c_id = c.c_id
        WHERE rr.return_id = %s AND o.st_id = %s
        """,
        (return_id, store_id)
    )
    record = cursor.fetchone()
    cursor.close()

    if not record:
        print("Return request not found for this store.")
        input("\nPress Enter to return...")
        return

    summary = get_return_summary(record["order_id"], record["prod_id"])
    already_returned = summary["approved_returned_qty"] if summary else 0
    remaining_qty = summary["remaining_qty"] if summary else 0
    refund = float(record["price_at_purchase"]) * record["return_quantity"]

    print(f"Return ID         : {record['return_id']}")
    print(f"Status            : {record['return_status']}")
    print(f"Requested At      : {record['requested_at']}")
    print(f"Order ID          : {record['order_id']}")
    print(f"Customer          : {record['customer_name']}")
    print(f"Product           : {record['product_name']} (ID: {record['prod_id']})")
    print(f"Return Quantity   : {record['return_quantity']} (originally ordered: {record['original_quantity']})")
    print(f"Already Returned  : {already_returned}")
    print(f"Still Returnable  : {remaining_qty}")
    print(f"Price at Purchase : ${record['price_at_purchase']:,.2f}")
    print(f"Estimated Refund  : ${refund:,.2f}")
    print(f"Reason            : {record['return_reason'] or 'N/A'}")

    input("\nPress Enter to return...")


def approve_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Approving Return ID: {return_id}...")
    print("-----------------------------")

    if not return_id:
        print("Return ID cannot be empty.")
        time.sleep(2)
        return

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT rr.return_id, rr.return_status, rr.prod_id,
               rr.return_quantity, oc.price_at_purchase, o.order_id
        FROM return_record rr
        JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
        JOIN orders o ON oc.order_id = o.order_id
        WHERE rr.return_id = %s AND o.st_id = %s
        """,
        (return_id, store_id)
    )
    record = cursor.fetchone()

    if not record:
        print("Return request not found for this store.")
        cursor.close()
        time.sleep(2)
        return

    if record["return_status"] != "requested":
        print(f"Return {return_id} is already '{record['return_status']}' - cannot approve.")
        cursor.close()
        time.sleep(2)
        return

    summary = get_return_summary(record["order_id"], record["prod_id"])

    if summary is None:
        cursor.close()
        print("Original order item not found.")
        time.sleep(2)
        return

    if summary["remaining_qty"] <= 0:
        cursor.close()
        print("This item has already been fully returned.")
        time.sleep(2)
        return

    if record["return_quantity"] > summary["remaining_qty"]:
        cursor.close()
        print(
            f"Cannot approve return. Requested quantity ({record['return_quantity']}) "
            f"exceeds remaining returnable quantity ({summary['remaining_qty']})."
        )
        time.sleep(2)
        return

    try:
        cursor.execute(
            """
            UPDATE return_record
            SET return_status = 'approved',
                processed_by_employee_id = %s
            WHERE return_id = %s
            """,
            (employee_id, return_id)
        )

        refund_amount = float(record["price_at_purchase"]) * record["return_quantity"]
        cursor.execute(
            """
            INSERT INTO payments (method, amount, payment_status, return_id)
            VALUES ('refund', %s, 'paid', %s)
            """,
            (refund_amount, return_id)
        )

        cursor.execute(
            """
            UPDATE stocks
            SET quantity = quantity + %s
            WHERE store_id = %s AND prod_id = %s
            """,
            (record["return_quantity"], store_id, record["prod_id"])
        )

        db.commit()
    except Exception:
        db.rollback()
        cursor.close()
        print("Could not approve return due to a database error.")
        time.sleep(2)
        return

    cursor.close()

    print(f"Return approved. Refund of ${refund_amount:,.2f} issued.")
    logger.info(f"Floor employee '{employee_id}' approved return '{return_id}' for store '{store_id}'.")
    time.sleep(2)


def deny_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Denying Return ID: {return_id}...")
    print("-----------------------------")

    if not return_id:
        print("Return ID cannot be empty.")
        time.sleep(2)
        return

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT rr.return_id, rr.return_status
        FROM return_record rr
        JOIN order_contains oc ON rr.order_id = oc.order_id AND rr.prod_id = oc.prod_id
        JOIN orders o ON oc.order_id = o.order_id
        WHERE rr.return_id = %s AND o.st_id = %s
        """,
        (return_id, store_id)
    )
    record = cursor.fetchone()

    if not record:
        print("Return request not found for this store.")
        cursor.close()
        time.sleep(2)
        return

    if record["return_status"] != "requested":
        print(f"Return {return_id} is already '{record['return_status']}' - cannot deny.")
        cursor.close()
        time.sleep(2)
        return

    try:
        cursor.execute(
            """
            UPDATE return_record
            SET return_status = 'denied',
                processed_by_employee_id = %s
            WHERE return_id = %s
            """,
            (employee_id, return_id)
        )
        db.commit()
    except Exception:
        db.rollback()
        cursor.close()
        print("Could not deny return due to a database error.")
        time.sleep(2)
        return

    cursor.close()

    print("Return denied successfully.")
    logger.info(f"Floor employee '{employee_id}' denied return '{return_id}' for store '{store_id}'.")
    time.sleep(2)


def process_instore_return(store_id, employee_id):
    while True:
        clear_screen()
        print("Process In-Store Return")
        print("-----------------------------")

        order_id = input("Enter Order ID (or press Enter to cancel): ").strip()
        if not order_id:
            return

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT o.order_id, o.order_date, o.order_type, o.order_status,
                   COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name
            FROM orders o
            LEFT JOIN customer c ON o.c_id = c.c_id
            WHERE o.order_id = %s AND o.st_id = %s
            """,
            (order_id, store_id)
        )
        order = cursor.fetchone()

        if not order:
            cursor.close()
            print("Order not found for this store.")
            time.sleep(2)
            continue

        if order["order_type"] != "In_store":
            cursor.close()
            print("Only in-store orders can be processed through this return flow.")
            time.sleep(2)
            continue

        print(f"\nOrder ID   : {order['order_id']}")
        print(f"Date       : {order['order_date']}")
        print(f"Type       : {order['order_type']}")
        print(f"Status     : {order['order_status']}")
        print(f"Customer   : {order['customer_name']}")
        print("\nOrder Items:")
        print("-----------------------------")

        cursor.execute(
            """
            SELECT oc.prod_id, p.name, oc.quantity, oc.price_at_purchase
            FROM order_contains oc
            JOIN product p ON oc.prod_id = p.prod_id
            WHERE oc.order_id = %s
            ORDER BY p.name
            """,
            (order_id,)
        )
        items = cursor.fetchall()

        if not items:
            cursor.close()
            print("This order has no items.")
            time.sleep(2)
            continue

        for item in items:
            summary = get_return_summary(order_id, item["prod_id"])
            returned_qty = summary["approved_returned_qty"] if summary else 0
            remaining_qty = summary["remaining_qty"] if summary else 0

            print(
                f"  Prod ID: {item['prod_id']}"
                f"  |  {item['name']}"
                f"  |  Bought: {item['quantity']}"
                f"  |  Already Returned: {returned_qty}"
                f"  |  Returnable: {remaining_qty}"
                f"  |  Price: ${item['price_at_purchase']:,.2f}"
            )

        prod_id = input("\nEnter Product ID to return (or press Enter to cancel): ").strip()
        if not prod_id:
            cursor.close()
            return

        if not prod_id.isdigit():
            cursor.close()
            print("Product ID must be numeric.")
            time.sleep(2)
            continue

        prod_id = int(prod_id)

        cursor.execute(
            """
            SELECT oc.prod_id, p.name, oc.quantity, oc.price_at_purchase
            FROM order_contains oc
            JOIN product p ON oc.prod_id = p.prod_id
            WHERE oc.order_id = %s AND oc.prod_id = %s
            """,
            (order_id, prod_id)
        )
        item = cursor.fetchone()

        if not item:
            cursor.close()
            print("That product is not part of this order.")
            time.sleep(2)
            continue

        summary = get_return_summary(order_id, prod_id)

        if summary is None:
            cursor.close()
            print("Original order item not found.")
            time.sleep(2)
            continue

        if summary["remaining_qty"] <= 0:
            cursor.close()
            print("This item has already been fully returned.")
            time.sleep(2)
            continue

        qty = input(f"Enter quantity to return (1-{summary['remaining_qty']}): ").strip()
        if not qty.isdigit():
            cursor.close()
            print("Return quantity must be a positive integer.")
            time.sleep(2)
            continue

        qty = int(qty)

        if qty < 1 or qty > summary["remaining_qty"]:
            cursor.close()
            print(f"Invalid return quantity. Only {summary['remaining_qty']} item(s) remain returnable.")
            time.sleep(2)
            continue

        reason = input("Enter return reason (optional): ").strip()
        refund_amount = float(item["price_at_purchase"]) * qty

        try:
            cursor.execute(
                """
                INSERT INTO return_record
                    (order_id, prod_id, return_quantity, return_reason, return_status, requested_at, processed_by_employee_id)
                VALUES
                    (%s, %s, %s, %s, 'approved', NOW(), %s)
                """,
                (order_id, prod_id, qty, reason if reason else None, employee_id)
            )
            return_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO payments (method, amount, payment_status, return_id)
                VALUES ('refund', %s, 'paid', %s)
                """,
                (refund_amount, return_id)
            )

            cursor.execute(
                """
                UPDATE stocks
                SET quantity = quantity + %s
                WHERE store_id = %s AND prod_id = %s
                """,
                (qty, store_id, prod_id)
            )

            db.commit()
        except Exception:
            db.rollback()
            cursor.close()
            print("Could not process in-store return due to a database error.")
            time.sleep(2)
            continue

        cursor.close()

        print(f"\nReturn processed successfully.")
        print(f"Return ID: {return_id}")
        print(f"Refund Amount: ${refund_amount:,.2f}")

        logger.info(
            f"Floor employee '{employee_id}' processed in-store return '{return_id}' "
            f"for order '{order_id}', product '{prod_id}', qty '{qty}', store '{store_id}'."
        )

        time.sleep(3)
        return