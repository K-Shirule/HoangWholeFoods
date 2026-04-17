import time
from db_connection import get_connection
from utils import clear_screen
from logger_config import get_logger

logger = get_logger(__name__)


def floor_employee_page(store_id, employee_id):
    while True:
        clear_screen()
        print("Welcome to the Floor Employee Page")
        print("Here you can manage in-store orders and process return requests.")
        print("1. Process In-Store Order")
        print("2. Process Return Requests")
        print("3. Logout")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            process_instore_orders(store_id, employee_id)

        elif choice == "2":
            process_return_requests(store_id, employee_id)

        elif choice == "3":
            print("Logging out...")
            logger.info(f"Floor employee '{employee_id}' logged out successfully.")
            time.sleep(2)
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def process_instore_orders(store_id, employee_id):
    while True:
        clear_screen()
        print("Does customer have an account with us?(y/n)")
        has_account = input().strip().lower()

        customer_id = None
        if has_account == 'y':
            customer_email = input("Please enter customer's email: ").strip()
            #query to get customer_id using the email, make sure it is valid email
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT c_id FROM customer WHERE email = %s",
                (customer_email,)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
 
            if not result:
                print("No customer found with that email.")
                time.sleep(2)
                continue
            customer_id = result["c_id"]
            print(f"Customer found (ID: {customer_id}).")
        elif has_account == 'n':
            customer_email = "null"
        print("Processing In-Store Order")
        print("-----------------------------")

        # Theoretically here you would scan products using like a scanner in the store
        # but for simplicity we'll just give some random product ids
        # that you can use for querying into the table
        
        order_items = {
            1:2,
            3:5,
            2:1
        } # dict of product_id: quantity pairs representing the order items
        
        while True:
            clear_screen()
            print("Current Order Items:")
            print("-----------------------------")
 
            # Show current items with names and prices
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
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
                    valid_items[prod_id] = {"qty": qty, "price": float(product["unit_price"]), "name": product["name"]}
                    print(
                        f"  Prod ID: {prod_id}"
                        f"  |  {product['name']}"
                        f"  |  Qty: {qty}"
                        f"  |  Unit Price: ${product['unit_price']:,.2f}"
                        f"  |  Line Total: ${line_total:,.2f}"
                        f"  |  In Stock: {product['stock_qty']}"
                    )
                else:
                    print(f"  Prod ID: {prod_id} — not found in this store's inventory, skipping.")
            cursor.close()
            conn.close()
 
            print(f"\n  Order Total: ${total:,.2f}")
            print("\nOptions:")
            print("1. Proceed to Payment and Finalize Order")
            print("2. Remove an item from the order")
            print("3. Cancel Order and Return to Floor Employee Page")
            #dont add any queries here just add them in the if-else statements below
            choice = input("Please enter your choice (1-3): ").strip()

            if choice == "1":
                #query to add the products to the order table and the order_contains table 
                #  with the store_id, customer_id (if exists), employee_id, product_ids 
                # and quantities from above - basically update all tables that need to be updated
                if not valid_items:
                    print("No valid items in order. Cannot proceed.")
                    time.sleep(2)
                    continue
 
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
 
                # Check stock availability before committing
                stock_ok = True
                for prod_id, info in valid_items.items():
                    cursor.execute(
                        "SELECT quantity FROM stocks WHERE store_id = %s AND prod_id = %s",
                        (store_id, prod_id)
                    )
                    stock = cursor.fetchone()
                    if not stock or stock["quantity"] < info["qty"]:
                        print(f"Insufficient stock for product {prod_id} ({info['name']}). Order cannot proceed.")
                        stock_ok = False
                        break
 
                if not stock_ok:
                    cursor.close()
                    conn.close()
                    time.sleep(2)
                    continue
 
                # Insert into orders
                cursor.execute(
                    """
                    INSERT INTO orders
                        (delivery_method, total_amount, order_type, order_status, c_id, st_id, e_id)
                    VALUES
                        ('in_store', %s, 'in_store', 'completed', %s, %s, %s)
                    """,
                    (total, customer_id, store_id, employee_id)
                )
                order_id = cursor.lastrowid
 
                # Insert into order_contains and deduct stock
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
 
                # Insert into payments
                cursor.execute(
                    """
                    INSERT INTO payments (method, amount, payment_status, order_id)
                    VALUES ('card', %s, 'completed', %s)
                    """,
                    (total, order_id)
                )
 
                conn.commit()
                cursor.close()
                conn.close()
 
                print(f"\nOrder #{order_id} finalized. Total charged: ${total:,.2f}")
                logger.info(
                    f"Floor employee '{employee_id}' finalized in-store order '{order_id}' "
                    f"for store '{store_id}' (customer_id={customer_id}, total=${total:.2f})."
                )
                time.sleep(3)
                return

            elif choice == "2":
                prod_id = input("Enter Product ID to remove or adjust (leave quantity 0 to remove): ").strip()
                if not prod_id.isdigit() or int(prod_id) not in order_items:
                    print("Product ID not in current order.")
                    time.sleep(2)
                    continue
                new_quantity = input("Enter new quantity (0 to remove): ").strip()
                if not new_quantity.isdigit() or int(new_quantity) < 0:
                    print("Quantity must be a non-negative integer.")
                    time.sleep(2)
                    continue
                if int(new_quantity) == 0:
                    del order_items[int(prod_id)]
                    print(f"Product {prod_id} removed from order.")
                else:
                    order_items[int(prod_id)] = int(new_quantity)
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

        # Query database for return requests related to this store.
        # Since return_record links to order_contains, you'll likely need joins through:
        # return_record -> order_contains -> orders
        #
        # Suggested filter:
        # - orders.st_id = store_id
        # - return_record.return_status = 'requested'
        #
        # Suggested fields:
        # - return_id
        # - order_id
        # - prod_id
        # - return_quantity
        # - return_reason
        # - requested_at
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
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
        conn.close()
 
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
            view_return_request_details(return_id, store_id)

        elif choice == "2":
            return_id = input("Enter Return ID to approve: ").strip()
            approve_return(return_id, store_id, employee_id)

        elif choice == "3":
            return_id = input("Enter Return ID to deny: ").strip()
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

    # Query database to show full return request details.
    # Make sure it belongs to an order from this store.
    #
    # Suggested information:
    # - return_record fields
    # - related order_id
    # - product details
    # - original ordered quantity from order_contains
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT rr.return_id, rr.return_quantity, rr.return_reason,
               rr.return_status, rr.requested_at,
               rr.order_id, rr.prod_id,
               p.name AS product_name, p.unit_price,
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
    conn.close()
 
    if not record:
        print("Return request not found for this store.")
        input("\nPress Enter to return...")
        return
 
    refund = float(record["price_at_purchase"]) * record["return_quantity"]
    print(f"Return ID         : {record['return_id']}")
    print(f"Status            : {record['return_status']}")
    print(f"Requested At      : {record['requested_at']}")
    print(f"Order ID          : {record['order_id']}")
    print(f"Customer          : {record['customer_name']}")
    print(f"Product           : {record['product_name']} (ID: {record['prod_id']})")
    print(f"Return Quantity   : {record['return_quantity']}  (originally ordered: {record['original_quantity']})")
    print(f"Price at Purchase : ${record['price_at_purchase']:,.2f}")
    print(f"Estimated Refund  : ${refund:,.2f}")
    print(f"Reason            : {record['return_reason'] or 'N/A'}")

    input("\nPress Enter to return...")

def approve_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Approving Return ID: {return_id}...")
    print("-----------------------------")

    # 1. Verify the return belongs to an order from this store
    # 2. Verify the return is still in 'requested' status
    # 3. Update return_record:
    #       - return_status = 'approved'
    #       - processed_by_employee_id = employee_id
    # 4. Optionally create/update refund-related payment record in payments
    # 5. Optionally restock returned quantity back into stocks if your team wants that behavior

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
 
    # Verify the return belongs to this store and is still 'requested'
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
        conn.close()
        time.sleep(2)
        return
 
    if record["return_status"] != "requested":
        print(f"Return {return_id} is already '{record['return_status']}' — cannot approve.")
        cursor.close()
        conn.close()
        time.sleep(2)
        return
 
    # Approve the return
    cursor.execute(
        """
        UPDATE return_record
        SET return_status = 'approved',
            processed_by_employee_id = %s
        WHERE return_id = %s
        """,
        (employee_id, return_id)
    )
 
    # Create a refund payment record
    refund_amount = float(record["price_at_purchase"]) * record["return_quantity"]
    cursor.execute(
        """
        INSERT INTO payments (method, amount, payment_status, return_id)
        VALUES ('refund', %s, 'completed', %s)
        """,
        (refund_amount, return_id)
    )
 
    # Restock the returned quantity back into inventory
    cursor.execute(
        """
        UPDATE stocks
        SET quantity = quantity + %s
        WHERE store_id = %s AND prod_id = %s
        """,
        (record["return_quantity"], store_id, record["prod_id"])
    )
 
    conn.commit()
    cursor.close()
    conn.close()
 
    print(f"Return approved. Refund of ${refund_amount:,.2f} issued.")
    logger.info(f"Floor employee '{employee_id}' approved return '{return_id}' for store '{store_id}'.")
    time.sleep(2)

def deny_return(return_id, store_id, employee_id):
    clear_screen()
    print(f"Denying Return ID: {return_id}...")
    print("-----------------------------")

    # 1. Verify the return belongs to an order from this store
    # 2. Verify the return is still in 'requested' status
    # 3. Update return_record:
    #       - return_status = 'denied'
    #       - processed_by_employee_id = employee_id

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
 
    # Verify the return belongs to this store and is still 'requested'
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
        conn.close()
        time.sleep(2)
        return
 
    if record["return_status"] != "requested":
        print(f"Return {return_id} is already '{record['return_status']}' — cannot deny.")
        cursor.close()
        conn.close()
        time.sleep(2)
        return
 
    cursor.execute(
        """
        UPDATE return_record
        SET return_status = 'denied',
            processed_by_employee_id = %s
        WHERE return_id = %s
        """,
        (employee_id, return_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
 
    print("Return denied successfully.")
    logger.info(f"Floor employee '{employee_id}' denied return '{return_id}' for store '{store_id}'.")
    time.sleep(2)
