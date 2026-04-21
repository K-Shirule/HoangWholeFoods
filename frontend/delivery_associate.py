# ALTER TABLE delivery_record MODIFY e_id INT NULL;
# i added this into queries since claim flow requires pending deliveries to have no associate yet

import time
from db_connection import get_connection
from utils import clear_screen
from logger_config import get_logger

logger = get_logger(__name__)


def delivery_associate_page(store_id, employee_id):
    while True:
        clear_screen()
        print("Welcome to the Delivery Associate Page")
        print("Here you can claim pending deliveries and update delivery status.")
        print("1. View Pending Deliveries")
        print("2. Claim a Delivery")
        print("3. View My Deliveries")
        print("4. Update Delivery Status")
        print("5. Logout")

        choice = input("Please enter your choice (1-5): ").strip()

        if choice == "1":
            view_pending_deliveries(store_id)

        elif choice == "2":
            claim_delivery(store_id, employee_id)

        elif choice == "3":
            view_my_deliveries(store_id, employee_id)

        elif choice == "4":
            update_delivery_status(store_id, employee_id)

        elif choice == "5":
            print("Logging out...")
            logger.info(f"Delivery associate '{employee_id}' logged out successfully.")
            time.sleep(2)
            break

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_pending_deliveries(store_id):
    clear_screen()
    print("Pending Deliveries")
    print("-----------------------------")

    # Query database for pending deliveries for this store.
    #
    # Suggested logic:
    # - delivery_record.delivery_status = 'pending'
    # - delivery_record.e_id IS NULL
    # - orders.st_id = store_id
    #
    # Suggested fields to show:
    # - delivery_id
    # - order_id
    # - delivered_to
    # - order_date
    # - total_amount
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivered_to, dr.delivery_status,
               o.order_id, o.order_date, o.total_amount,
               COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        LEFT JOIN customer c ON o.c_id = c.c_id
        WHERE o.st_id = %s
          AND dr.delivery_status = 'pending'
          AND dr.e_id IS NULL
        ORDER BY o.order_date ASC
        """,
        (store_id,)
    )
    deliveries = cursor.fetchall()
    cursor.close()
    conn.close()
 
    if not deliveries:
        print("No pending deliveries at this time.")
    else:
        for d in deliveries:
            print(
                f"  Delivery ID: {d['delivery_id']}"
                f"  |  Order ID: {d['order_id']}"
                f"  |  Order Date: {d['order_date']}"
                f"  |  Deliver To: {d['delivered_to'] or 'N/A'}"
                f"  |  Customer: {d['customer_name']}"
                f"  |  Total: ${d['total_amount'] or 0:,.2f}"
            )

    input("\nPress Enter to return...")


def claim_delivery(store_id, employee_id):
    clear_screen()
    print("Claim a Delivery")
    print("-----------------------------")

    # Show all pending deliveries for this store first
    # so the employee can choose one to claim
    print("Unclaimed deliveries for your store:\n")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivered_to,
               o.order_id, o.order_date, o.total_amount
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        WHERE o.st_id = %s
          AND dr.delivery_status = 'pending'
          AND dr.e_id IS NULL
        ORDER BY o.order_date ASC
        """,
        (store_id,)
    )
    deliveries = cursor.fetchall()
    cursor.close()
    conn.close()
 
    if not deliveries:
        print("No unclaimed deliveries available.")
        time.sleep(2)
        return
 
    for d in deliveries:
        print(
            f"  Delivery ID: {d['delivery_id']}"
            f"  |  Order ID: {d['order_id']}"
            f"  |  Order Date: {d['order_date']}"
            f"  |  Deliver To: {d['delivered_to'] or 'N/A'}"
            f"  |  Total: ${d['total_amount'] or 0:,.2f}"
        )

    delivery_id = input("Enter Delivery ID to claim (or press Enter to cancel): ").strip()

    # 1. Verify this delivery belongs to the employee's store
    # 2. Verify delivery status is 'pending'
    # 3. Verify e_id is currently NULL / unassigned
    # 4. Update delivery_record:
    #       - e_id = employee_id
    #       - delivery_status = 'claimed'
    if not delivery_id:
        return
 
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivery_status, dr.e_id
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        WHERE dr.delivery_id = %s AND o.st_id = %s
        """,
        (delivery_id, store_id)
    )
    record = cursor.fetchone()
 
    if not record:
        print(f"Delivery {delivery_id} not found for this store.")
        cursor.close()
        conn.close()
        time.sleep(2)
        return
 
    if record["delivery_status"] != "pending":
        print(f"Delivery {delivery_id} is already '{record['delivery_status']}' - cannot claim.")
        cursor.close()
        conn.close()
        time.sleep(2)
        return
 
    if record["e_id"] is not None:
        print(f"Delivery {delivery_id} has already been claimed by another associate.")
        cursor.close()
        conn.close()
        time.sleep(2)
        return
 
    cursor.execute(
        """
        UPDATE delivery_record
        SET e_id = %s, delivery_status = 'claimed'
        WHERE delivery_id = %s
        """,
        (employee_id, delivery_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Delivery {delivery_id} successfully claimed.")
    logger.info(f"Delivery associate '{employee_id}' claimed delivery '{delivery_id}'.")
    time.sleep(2)


def view_my_deliveries(store_id, employee_id):
    while True:
        clear_screen()
        print("My Deliveries")
        print("-----------------------------")

        # Query database for deliveries claimed by this employee.
        #
        # Suggested filters:
        # - delivery_record.e_id = employee_id
        # - orders.st_id = store_id
        #
        # Suggested fields:
        # - delivery_id
        # - order_id
        # - delivered_to
        # - delivery_status
        # - delivered_at
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT dr.delivery_id, dr.delivery_status, dr.delivered_to,
                   dr.delivered_at,
                   o.order_id, o.order_date, o.total_amount
            FROM delivery_record dr
            JOIN orders o ON dr.order_id = o.order_id
            WHERE dr.e_id = %s AND o.st_id = %s
            ORDER BY o.order_date DESC
            """,
            (employee_id, store_id)
        )
        deliveries = cursor.fetchall()
        cursor.close()
        conn.close()
 
        if not deliveries:
            print("You have no deliveries assigned.")
        else:
            for d in deliveries:
                print(
                    f"  Delivery ID: {d['delivery_id']}"
                    f"  |  Order ID: {d['order_id']}"
                    f"  |  Status: {d['delivery_status']}"
                    f"  |  Deliver To: {d['delivered_to'] or 'N/A'}"
                    f"  |  Delivered At: {d['delivered_at'] or 'N/A'}"
                    f"  |  Total: ${d['total_amount'] or 0:,.2f}"
                )

        print("\nOptions:")
        print("1. View Delivery Details")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            delivery_id = input("Enter Delivery ID: ").strip()
            view_delivery_details(delivery_id, store_id, employee_id)

        elif choice == "2":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_delivery_details(delivery_id, store_id, employee_id):
    clear_screen()
    print(f"Viewing details for Delivery ID: {delivery_id}")
    print("-----------------------------")

    # Query database for full delivery details.
    # Make sure:
    # - delivery belongs to this employee
    # - delivery belongs to this store
    #
    # Suggested information:
    # - delivery_record fields
    # - related order info from orders
    # - ordered items from order_contains if desired
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
 
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivery_status, dr.delivered_to, dr.delivered_at,
               o.order_id, o.order_date, o.order_type, o.order_status,
               o.total_amount, o.delivery_method,
               COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name,
               c.email AS customer_email, c.phone AS customer_phone
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        LEFT JOIN customer c ON o.c_id = c.c_id
        WHERE dr.delivery_id = %s
          AND dr.e_id = %s
          AND o.st_id = %s
        """,
        (delivery_id, employee_id, store_id)
    )
    record = cursor.fetchone()
 
    if not record:
        print("Delivery not found or does not belong to you.")
        cursor.close()
        conn.close()
        input("\nPress Enter to return...")
        return
 
    print(f"Delivery ID     : {record['delivery_id']}")
    print(f"Status          : {record['delivery_status']}")
    print(f"Deliver To      : {record['delivered_to'] or 'N/A'}")
    print(f"Delivered At    : {record['delivered_at'] or 'N/A'}")
    print(f"Order ID        : {record['order_id']}")
    print(f"Order Date      : {record['order_date']}")
    print(f"Order Status    : {record['order_status']}")
    print(f"Delivery Method : {record['delivery_method'] or 'N/A'}")
    print(f"Customer        : {record['customer_name']}")
    print(f"Email           : {record['customer_email'] or 'N/A'}")
    print(f"Phone           : {record['customer_phone'] or 'N/A'}")
    print(f"Total           : ${record['total_amount'] or 0:,.2f}")
    print("-----------------------------")
    print("Items:")
 
    cursor.execute(
        """
        SELECT oc.prod_id, p.name, oc.quantity, oc.price_at_purchase,
               (oc.quantity * oc.price_at_purchase) AS line_total
        FROM order_contains oc
        JOIN product p ON oc.prod_id = p.prod_id
        WHERE oc.order_id = %s
        """,
        (record["order_id"],)
    )
    items = cursor.fetchall()
    cursor.close()
    conn.close()
 
    for item in items:
        print(
            f"  Prod ID: {item['prod_id']}"
            f"  |  {item['name']}"
            f"  |  Qty: {item['quantity']}"
            f"  |  Price: ${item['price_at_purchase']:,.2f}"
            f"  |  Line Total: ${item['line_total']:,.2f}"
        )

    input("\nPress Enter to return...")


def update_delivery_status(store_id, employee_id):
    clear_screen()
    print("Update Delivery Status")
    print("-----------------------------")

    # Show this employee's claimed deliveries
    print("Your active deliveries:\n")
 
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivery_status, dr.delivered_to, o.order_id
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        WHERE dr.e_id = %s
          AND o.st_id = %s
          AND dr.delivery_status NOT IN ('Completed', 'Failed')
        ORDER BY o.order_date ASC
        """,
        (employee_id, store_id)
    )
    deliveries = cursor.fetchall()
    cursor.close()
    conn.close()
 
    if not deliveries:
        print("No active deliveries to update.")
        time.sleep(2)
        return
 
    for d in deliveries:
        print(
            f"  Delivery ID: {d['delivery_id']}"
            f"  |  Order ID: {d['order_id']}"
            f"  |  Status: {d['delivery_status']}"
            f"  |  Deliver To: {d['delivered_to'] or 'N/A'}"
        )

    delivery_id = input("Enter Delivery ID for which you want to update status: ").strip()
    if not delivery_id:
        return

    while True:
        clear_screen()
        print(f"Update Status for Delivery ID: {delivery_id}")
        print("-----------------------------")
        print("1. Mark as Ready")
        print("2. Mark as Completed")
        print("3. Mark as Failed")
        print("4. Return")

        choice = input("Please enter your choice (1-4): ").strip()

        if choice == "1":
            new_status = "Ready"
            new_order_status = "out_for_delivery"

        elif choice == "2":
            new_status = "Completed"
            new_order_status = "delivered"

        elif choice == "3":
            new_status = "Failed"
            new_order_status = "delivery_failed"

        elif choice == "4":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)
            continue

        # 1. Verify this delivery belongs to employee_id
        # 2. Verify delivery belongs to store_id
        # 3. Update delivery_record.delivery_status = new_status
        # 4. If new_status == 'delivered':
        #       optionally update delivered_at
        # 5. Optionally update the related orders.order_status too
        #    Example:
        #       - 'out_for_delivery'
        #       - 'delivered'
        #       - 'delivery_failed'

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT dr.delivery_id, dr.delivery_status, o.order_id
            FROM delivery_record dr
            JOIN orders o ON dr.order_id = o.order_id
            WHERE dr.delivery_id = %s
              AND dr.e_id = %s
              AND o.st_id = %s
            """,
            (delivery_id, employee_id, store_id)
        )
        record = cursor.fetchone()
 
        if not record:
            print("Delivery not found or does not belong to you.")
            cursor.close()
            conn.close()
            time.sleep(2)
            return
 
        # Update delivery_record; stamp delivered_at when completed
        if new_status == "Completed":
            cursor.execute(
                """
                UPDATE delivery_record
                SET delivery_status = %s, delivered_at = NOW()
                WHERE delivery_id = %s
                """,
                (new_status, delivery_id)
            )
        else:
            cursor.execute(
                "UPDATE delivery_record SET delivery_status = %s WHERE delivery_id = %s",
                (new_status, delivery_id)
            )
 
        # Mirror on the parent order so order_status stays in sync
        cursor.execute(
            "UPDATE orders SET order_status = %s WHERE order_id = %s",
            (new_order_status, record["order_id"])
        )
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Delivery {delivery_id} updated to status '{new_status}'.")
        logger.info(
            f"Delivery associate '{employee_id}' updated delivery '{delivery_id}' to '{new_status}'."
        )
        time.sleep(2)
        return
