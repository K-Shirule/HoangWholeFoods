# SJSU CMPE 138 SPRING 2026 TEAM6
import time
from db_connector import db
from utils import clear_screen
from logger_config import get_logger

logger = get_logger(__name__)

#see past deliveries
def get_delivery_record(delivery_id, store_id, employee_id=None):
    """
    Fetch a delivery and confirm it belongs to the given store.
    If employee_id is provided, also confirm it belongs to that employee.
    Returns a dictionary row or None.
    """
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT dr.delivery_id, dr.delivery_status, dr.delivered_to, dr.delivered_at,
               dr.e_id,
               o.order_id, o.order_date, o.order_type, o.order_status,
               o.total_amount, o.delivery_method,
               COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name,
               c.email AS customer_email,
               c.phone AS customer_phone
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        LEFT JOIN customer c ON o.c_id = c.c_id
        WHERE dr.delivery_id = %s
          AND o.st_id = %s
    """
    params = [delivery_id, store_id]

    if employee_id is not None:
        query += " AND dr.e_id = %s"
        params.append(employee_id)

    cursor.execute(query, tuple(params))
    record = cursor.fetchone()

    cursor.close()
    return record

#main landing page for delivery assoc.
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

#these are delivieries that are requested by cystomer but not assigned/chosen by delivery assoc. yet
def view_pending_deliveries(store_id):
    clear_screen()
    print("Pending Deliveries")
    print("-----------------------------")

    cursor = db.cursor(dictionary=True)
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
    print("Unclaimed deliveries for your store:\n")

    cursor = db.cursor(dictionary=True)
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

    if not delivery_id:
        return

    if not delivery_id.isdigit():
        print("Delivery ID must be numeric.")
        time.sleep(2)
        return

    record = get_delivery_record(delivery_id, store_id)

    if not record:
        print(f"Delivery {delivery_id} not found for this store.")
        time.sleep(2)
        return

    if record["delivery_status"] != "pending":
        print(f"Delivery {delivery_id} is already '{record['delivery_status']}' - cannot claim.")
        time.sleep(2)
        return

    if record["e_id"] is not None:
        print(f"Delivery {delivery_id} has already been claimed by another associate.")
        time.sleep(2)
        return

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        UPDATE delivery_record
        SET e_id = %s, delivery_status = 'claimed'
        WHERE delivery_id = %s
        """,
        (employee_id, delivery_id)
    )
    db.commit()
    cursor.close()

    print(f"Delivery {delivery_id} successfully claimed.")
    logger.info(f"Delivery associate '{employee_id}' claimed delivery '{delivery_id}'.")
    time.sleep(2)

#func to show the assoc the deliveries they have claimed/picked to deliver
def view_my_deliveries(store_id, employee_id):
    while True:
        clear_screen()
        print("My Deliveries")
        print("-----------------------------")

        cursor = db.cursor(dictionary=True)
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

            if not delivery_id:
                print("Delivery ID cannot be empty.")
                time.sleep(2)
                continue

            if not delivery_id.isdigit():
                print("Delivery ID must be numeric.")
                time.sleep(2)
                continue

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

    if not delivery_id:
        print("Delivery ID cannot be empty.")
        input("\nPress Enter to return...")
        return

    if not str(delivery_id).isdigit():
        print("Delivery ID must be numeric.")
        input("\nPress Enter to return...")
        return

    record = get_delivery_record(delivery_id, store_id, employee_id)

    if not record:
        print("Delivery not found or does not belong to you.")
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

    cursor = db.cursor(dictionary=True)
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

    if not items:
        print("No items found for this delivery's order.")
    else:
        for item in items:
            print(
                f"  Prod ID: {item['prod_id']}"
                f"  |  {item['name']}"
                f"  |  Qty: {item['quantity']}"
                f"  |  Price: ${item['price_at_purchase']:,.2f}"
                f"  |  Line Total: ${item['line_total']:,.2f}"
            )

    input("\nPress Enter to return...")

#update status throughout delivery process
def update_delivery_status(store_id, employee_id):
    clear_screen()
    print("Update Delivery Status")
    print("-----------------------------")
    print("Your active deliveries:\n")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT dr.delivery_id, dr.delivery_status, dr.delivered_to, o.order_id
        FROM delivery_record dr
        JOIN orders o ON dr.order_id = o.order_id
        WHERE dr.e_id = %s
          AND o.st_id = %s
          AND dr.delivery_status NOT IN ('completed', 'failed')
        ORDER BY o.order_date ASC
        """,
        (employee_id, store_id)
    )
    deliveries = cursor.fetchall()
    cursor.close()

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

    if not delivery_id.isdigit():
        print("Delivery ID must be numeric.")
        time.sleep(2)
        return

    record = get_delivery_record(delivery_id, store_id, employee_id)

    if not record:
        print("Delivery not found or does not belong to you.")
        time.sleep(2)
        return

    current_status = (record["delivery_status"] or "").strip().lower()
    delivery_method = (record["delivery_method"] or "").strip().lower()
    delivered_to = (record["delivered_to"] or "").strip().lower()

    is_pickup = (
        delivery_method in ("pickup", "in_store", "in-store")
        or delivered_to in ("pickup", "in-store", "store")
    )

    if current_status in ("completed"):
        print(f"Delivery {delivery_id} is already '{current_status}' and cannot be updated.")
        time.sleep(2)
        return

    while True:
        clear_screen()
        print(f"Update Status for Delivery ID: {delivery_id}")
        print(f"Current Status: {current_status}")
        print(f"Type: {'Pickup' if is_pickup else 'Delivery'}")
        print("-----------------------------")
        print("1. Mark as Ready")

        if not is_pickup:
            print("2. Mark as Out for Delivery")
            print("3. Mark as Completed")
            print("4. Mark as Failed")
            print("5. Return")
        else:
            print("2. Mark as Completed")
            print("3. Mark as Failed")
            print("4. Return")

        choice = input("Please enter your choice: ").strip()

        new_status = None
        new_order_status = None

        if not is_pickup:
            if choice == "1":
                if current_status != "claimed":
                    print(f"Cannot mark delivery as ready from status '{current_status}'.")
                    time.sleep(2)
                    continue
                new_status = "ready"
                new_order_status = "ready"

            elif choice == "2":
                if current_status != "ready":
                    print(f"Cannot mark delivery as out for delivery from status '{current_status}'.")
                    time.sleep(2)
                    continue
                new_status = "out for delivery"
                new_order_status = "out for delivery"

            elif choice == "3":
                if current_status != "out for delivery":
                    print("Delivery must be 'out for delivery' before it can be completed.")
                    time.sleep(2)
                    continue
                new_status = "completed"
                new_order_status = "fulfilled"

            elif choice == "4":
                if current_status not in ("claimed", "ready", "out for delivery"):
                    print(f"Cannot mark delivery as failed from status '{current_status}'.")
                    time.sleep(2)
                    continue
                new_status = "failed"
                new_order_status = "failed"

            elif choice == "5":
                return

            else:
                print("Invalid choice. Please try again.")
                time.sleep(2)
                continue

        else:
            if choice == "1":
                if current_status != "claimed":
                    print(f"Cannot mark pickup as ready from status '{current_status}'.")
                    time.sleep(2)
                    continue
                new_status = "ready"
                new_order_status = "ready for pickup"

            elif choice == "2":
                if current_status != "ready":
                    print("Pickup must be 'ready' before it can be completed.")
                    time.sleep(2)
                    continue
                new_status = "completed"
                new_order_status = "fulfilled"

            elif choice == "3":
                if current_status not in ("claimed", "ready"):
                    print(f"Cannot mark pickup as failed from status '{current_status}'.")
                    time.sleep(2)
                    continue
                new_status = "failed"
                new_order_status = "failed"

            elif choice == "4":
                return

            else:
                print("Invalid choice. Please try again.")
                time.sleep(2)
                continue

        if new_status == current_status:
            print(f"Delivery is already marked as '{current_status}'.")
            time.sleep(2)
            continue

        cursor = db.cursor(dictionary=True)

        if new_status == "completed":
            cursor.execute(
                """
                UPDATE delivery_record
                SET delivery_status = %s, delivered_at = NOW()
                WHERE delivery_id = %s
                """,
                (new_status, delivery_id)
            )
        elif new_status == "failed":
            cursor.execute(
                """
                UPDATE delivery_record
                SET delivery_status = %s
                WHERE delivery_id = %s
                """,
                (new_status, delivery_id)
            )
        else:
            cursor.execute(
                """
                UPDATE delivery_record
                SET delivery_status = %s
                WHERE delivery_id = %s
                """,
                (new_status, delivery_id)
            )

        cursor.execute(
            """
            UPDATE orders
            SET order_status = %s
            WHERE order_id = %s
            """,
            (new_order_status, record["order_id"])
        )

        db.commit()
        cursor.close()

        print(f"Delivery {delivery_id} updated to status '{new_status}'.")
        logger.info(
            f"Delivery associate '{employee_id}' updated delivery '{delivery_id}' to '{new_status}'."
        )
        time.sleep(2)
        return