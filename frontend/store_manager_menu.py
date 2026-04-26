# SJSU CMPE 138 SPRING 2026 TEAM6
import time
from db_connector import db
from logger_config import get_logger
from utils import clear_screen, print_load
from create_supplier_orders import create_supplier_orders_from_restock_list

logger = get_logger(__name__)

#store manager landing menu
def store_manager_page(store_id, e_id):
    while True:
        clear_screen()
        print("Welcome to the Store Manager Page")
        print("Here you can manage employees, approve restock requests, and view store activity.")

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT branch_name FROM store WHERE st_id = %s", (store_id,))
        store = cursor.fetchone()
        cursor.close()

        store_name = store["branch_name"] if store else "Unknown Store"

        print(f"\nStore Name: {store_name}")
        print("1. View Employees")
        print("2. View Pending Restock Lists")
        print("3. View Past Restock Lists")
        print("4. View Store Orders")
        print("5. View Store Pin")
        print("6. View Supplier Pin")
        print("7. Change Employee Salary")
        print("8. Logout")

        choice = input("Please enter your choice (1-8): ").strip()

        if choice == "1":
            view_employees(store_id, e_id)
        elif choice == "2":
            view_pending_restock_list(store_id, e_id)
        elif choice == "3":
            view_past_restock_lists(store_id)
        elif choice == "4":
            view_store_orders(store_id)
        elif choice == "5":
            view_store_pin(store_id)
        elif choice == "6":
            view_supplier_pin(store_id)
        elif choice == "7":
            change_employee_salary(store_id, e_id)
        elif choice == "8":
            print("Logging out...")
            logger.info(f"Store manager '{e_id}' logged out.")
            time.sleep(2)
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

#helper functions to do all operations of the manager menu
def view_employees(store_id, e_id):
    while True:
        clear_screen()
        print("\nOptions:")
        print("1. View Current Employee Details")
        print("2. View Past Employee Details")
        print("3. Return to Store Manager Page")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            view_current_employee_details(store_id, e_id)
        elif choice == "2":
            view_past_employee_details(store_id)
        elif choice == "3":
            return
        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)

def view_current_employee_details(store_id, e_id):
    while True:
        clear_screen()
        print("Viewing details for current employees:")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e_id, first_name, last_name, email, phone,
                   role, salary, start_date
            FROM employee
            WHERE st_id = %s AND is_current = TRUE
            ORDER BY role, last_name
            """,
            (store_id,)
        )
        employees = cursor.fetchall()
        cursor.close()

        if not employees:
            print("No current employees found.")
        else:
            for emp in employees:
                print(
                    f"  ID: {emp['e_id']}"
                    f"  |  {emp['first_name']} {emp['last_name']}"
                    f"  |  Role: {emp['role']}"
                    f"  |  Email: {emp['email']}"
                    f"  |  Phone: {emp['phone'] or 'N/A'}"
                    f"  |  Salary: ${emp['salary'] or 0:,.2f}"
                    f"  |  Start: {emp['start_date']}"
                )

        print("\nOptions:")
        print("1. Mark Employee as Inactive")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            target_employee_id = input("Enter Employee ID to mark as inactive: ").strip()
            if str(target_employee_id) == str(e_id):
                print("You cannot mark yourself as inactive.")
                time.sleep(2)
                continue
            print(f"\nMarking Employee {target_employee_id} as inactive...")

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT e_id, first_name, last_name
                FROM employee
                WHERE e_id = %s AND st_id = %s AND is_current = TRUE
                """,
                (target_employee_id, store_id)
            )
            target = cursor.fetchone()

            if not target:
                print(f"No active employee with ID {target_employee_id} found for this store.")
                cursor.close()
                time.sleep(2)
                continue

            cursor.execute(
                """
                UPDATE employee
                SET is_current = FALSE, end_date = CURDATE()
                WHERE e_id = %s
                """,
                (target_employee_id,)
            )
            db.commit()
            cursor.close()

            print(f"Employee {target['first_name']} {target['last_name']} marked as inactive.")
            logger.info(f"Employee '{target_employee_id}' marked inactive by manager '{e_id}'.")
            time.sleep(2)

        elif choice == "2":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def view_past_employee_details(store_id):
    clear_screen()
    print("Viewing details for past employees:")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT e_id, first_name, last_name, email, phone,
               role, start_date, end_date
        FROM employee
        WHERE st_id = %s AND is_current = FALSE
        ORDER BY end_date DESC
        """,
        (store_id,)
    )
    employees = cursor.fetchall()
    cursor.close()

    if not employees:
        print("No past employees found.")
    else:
        for emp in employees:
            print(
                f"  ID: {emp['e_id']}"
                f"  |  {emp['first_name']} {emp['last_name']}"
                f"  |  Role: {emp['role']}"
                f"  |  Start: {emp['start_date']}"
                f"  |  End: {emp['end_date']}"
            )

    input("\nPress Enter to return...")

def view_pending_restock_list(store_id, e_id):
    while True:
        clear_screen()
        print("Pending Restock Lists")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT rl.list_id, rl.created_at,
                   e.first_name, e.last_name,
                   COUNT(rc.prod_id) AS item_count
            FROM restock_list rl
            JOIN employee e ON rl.created_by = e.e_id
            LEFT JOIN restock_contains rc ON rl.list_id = rc.list_id
            WHERE rl.store_id = %s AND rl.restock_status = 'pending'
            GROUP BY rl.list_id, rl.created_at, e.first_name, e.last_name
            ORDER BY rl.created_at DESC
            """,
            (store_id,)
        )
        lists = cursor.fetchall()
        cursor.close()

        if not lists:
            print("No pending restock lists.")
        else:
            for rl in lists:
                print(
                    f"  List ID: {rl['list_id']}"
                    f"  |  Created: {rl['created_at']}"
                    f"  |  By: {rl['first_name']} {rl['last_name']}"
                    f"  |  Items: {rl['item_count']}"
                )

        print("\nOptions:")
        print("1. View List Details")
        print("2. Approve Restock List")
        print("3. Deny/Cancel Restock List")
        print("4. Return")

        choice = input("Please enter your choice (1-4): ").strip()

        if choice == "1":
            list_id = input("Enter List ID to view: ").strip()

            if not list_id:
                print("Restock List ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT list_id
                FROM restock_list
                WHERE list_id = %s AND store_id = %s AND restock_status = 'pending'
                """,
                (list_id, store_id)
            )
            rl = cursor.fetchone()
            cursor.close()

            if not rl:
                print(f"Pending restock list {list_id} not found for this store.")
                time.sleep(2)
                continue

            view_restock_list_details(list_id, store_id)

        elif choice == "2":
            list_id = input("Enter List ID to approve: ").strip()

            if not list_id:
                print("Restock List ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT list_id, restock_status
                FROM restock_list
                WHERE list_id = %s AND store_id = %s
                """,
                (list_id, store_id)
            )
            rl = cursor.fetchone()
            cursor.close()

            if not rl:
                print(f"Restock list {list_id} not found for this store.")
                time.sleep(2)
                continue

            if rl["restock_status"] != "pending":
                print(f"List {list_id} is already '{rl['restock_status']}' and cannot be approved.")
                time.sleep(2)
                continue

            approve_restock_list(list_id, store_id, e_id)

        elif choice == "3":
            list_id = input("Enter List ID to deny/cancel: ").strip()

            if not list_id:
                print("Restock List ID cannot be empty.")
                time.sleep(2)
                continue

            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT list_id, restock_status
                FROM restock_list
                WHERE list_id = %s AND store_id = %s
                """,
                (list_id, store_id)
            )
            rl = cursor.fetchone()
            cursor.close()

            if not rl:
                print(f"Restock list {list_id} not found for this store.")
                time.sleep(2)
                continue

            if rl["restock_status"] != "pending":
                print(f"List {list_id} is already '{rl['restock_status']}' and cannot be denied/cancelled.")
                time.sleep(2)
                continue

            deny_restock_list(list_id, store_id, e_id)

        elif choice == "4":
            return

        else:
            print("Invalid choice.")
            time.sleep(2)

def approve_restock_list(list_id, store_id, employee_id):
    if not list_id:
        print("Restock List ID cannot be empty.")
        time.sleep(2)
        return

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT list_id, store_id, restock_status
        FROM restock_list
        WHERE list_id = %s AND store_id = %s
        """,
        (list_id, store_id)
    )
    rl = cursor.fetchone()

    if not rl:
        print(f"Restock list {list_id} not found for this store.")
        cursor.close()
        time.sleep(2)
        return

    if rl["restock_status"] != "pending":
        print(f"List {list_id} is already '{rl['restock_status']}' and cannot be approved.")
        cursor.close()
        time.sleep(2)
        return

    cursor.close()

    print(f"\nApproving Restock List {list_id}...")

    if create_supplier_orders_from_restock_list(list_id, store_id):
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            UPDATE restock_list
            SET restock_status = 'approved',
                approved_by = %s,
                approved_at = NOW()
            WHERE list_id = %s AND store_id = %s
            """,
            (employee_id, list_id, store_id)
        )
        db.commit()
        cursor.close()

        print(f"Restock list {list_id} approved.")
        logger.info(f"Restock list '{list_id}' approved by '{employee_id}' for store '{store_id}'.")
    else:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            UPDATE restock_list
            SET restock_status = 'denied'
            WHERE list_id = %s AND store_id = %s
            """,
            (list_id, store_id)
        )
        db.commit()
        cursor.close()

        print(f"Restock list {list_id} could not be approved and has been cancelled.")
        logger.info(f"Restock list '{list_id}' denied by '{employee_id}' for store '{store_id}'.")

    time.sleep(2)

def deny_restock_list(list_id, store_id, employee_id):
    if not list_id:
        print("Restock List ID cannot be empty.")
        time.sleep(2)
        return

    print(f"\nDenying Restock List {list_id}...")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT list_id, restock_status
        FROM restock_list
        WHERE list_id = %s AND store_id = %s
        """,
        (list_id, store_id)
    )
    rl = cursor.fetchone()

    if not rl:
        print(f"Restock list {list_id} not found for this store.")
        cursor.close()
        time.sleep(2)
        return

    if rl["restock_status"] != "pending":
        print(f"List {list_id} is already '{rl['restock_status']}' and cannot be denied/cancelled.")
        cursor.close()
        time.sleep(2)
        return

    cursor.execute(
        """
        UPDATE restock_list
        SET restock_status = 'cancelled'
        WHERE list_id = %s AND store_id = %s
        """,
        (list_id, store_id)
    )
    db.commit()
    cursor.close()

    print(f"Restock list {list_id} cancelled.")
    logger.info(f"Restock list '{list_id}' denied/cancelled by '{employee_id}'.")
    time.sleep(2)

def view_past_restock_lists(store_id):
    while True:
        clear_screen()
        print("Past Restock Lists")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT rl.list_id, rl.restock_status, rl.created_at, rl.approved_at,
                   c.first_name AS creator_first, c.last_name AS creator_last,
                   a.first_name AS approver_first, a.last_name AS approver_last
            FROM restock_list rl
            JOIN employee c ON rl.created_by = c.e_id
            LEFT JOIN employee a ON rl.approved_by = a.e_id
            WHERE rl.store_id = %s AND rl.restock_status != 'pending'
            ORDER BY rl.created_at DESC
            """,
            (store_id,)
        )
        lists = cursor.fetchall()
        cursor.close()

        if not lists:
            print("No past restock lists found.")
        else:
            for rl in lists:
                approver = (
                    f"{rl['approver_first']} {rl['approver_last']}"
                    if rl["approver_first"] else "N/A"
                )
                print(
                    f"  List ID: {rl['list_id']}"
                    f"  |  Status: {rl['restock_status']}"
                    f"  |  Created: {rl['created_at']}"
                    f"  |  By: {rl['creator_first']} {rl['creator_last']}"
                    f"  |  Approved by: {approver}"
                )

        print("\nOptions:")
        print("1. View Details")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            list_id = input("Enter Restock List ID: ").strip()
            view_restock_list_details(list_id, store_id)
        elif choice == "2":
            return
        else:
            print("Invalid choice.")
            time.sleep(2)

def view_restock_list_details(list_id, store_id):
    clear_screen()

    if not list_id:
        print("Restock List ID cannot be empty.")
        input("\nPress Enter to return...")
        return

    print(f"Viewing Restock List {list_id}")

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT rl.list_id, rl.restock_status, rl.created_at, rl.approved_at,
               c.first_name AS creator_first, c.last_name AS creator_last,
               a.first_name AS approver_first, a.last_name AS approver_last
        FROM restock_list rl
        JOIN employee c ON rl.created_by = c.e_id
        LEFT JOIN employee a ON rl.approved_by = a.e_id
        WHERE rl.list_id = %s AND rl.store_id = %s
        """,
        (list_id, store_id)
    )
    rl = cursor.fetchone()

    if not rl:
        print(f"Restock list {list_id} not found for this store.")
        cursor.close()
        input("\nPress Enter to return...")
        return

    approver_name = (
        f"{rl['approver_first']} {rl['approver_last']}"
        if rl["approver_first"] and rl["approver_last"]
        else "N/A"
    )

    print(f"Status      : {rl['restock_status']}")
    print(f"Created At  : {rl['created_at']}")
    print(f"Created By  : {rl['creator_first']} {rl['creator_last']}")
    print(f"Approved At : {rl['approved_at'] or 'N/A'}")
    print(f"Approved By : {approver_name}")
    print("-" * 100)
    print("Items:")

    cursor.execute(
        """
        SELECT
            rc.prod_id,
            p.name AS product_name,
            rc.supplier_id,
            s.supplier_name,
            rc.quantity,
            sp.supplier_price,
            (
                SELECT MIN(sp2.supplier_price)
                FROM supplies sp2
                WHERE sp2.prod_id = rc.prod_id
            ) AS lowest_supplier_price
        FROM restock_contains rc
        JOIN product p
            ON rc.prod_id = p.prod_id
        JOIN supplier s
            ON rc.supplier_id = s.supplier_id
        JOIN supplies sp
            ON sp.prod_id = rc.prod_id
           AND sp.supplier_id = rc.supplier_id
        WHERE rc.list_id = %s
        ORDER BY p.name, s.supplier_name
        """,
        (list_id,)
    )
    items = cursor.fetchall()
    cursor.close()

    if not items:
        print("No items found in this restock list.")
        input("\nPress Enter to return...")
        return

    for item in items:
        cheapest_flag = ""
        if float(item["supplier_price"]) == float(item["lowest_supplier_price"]):
            cheapest_flag = "CHEAPEST"

        print(
            f"Product ID: {item['prod_id']} | "
            f"{item['product_name']} | "
            f"Supplier: {item['supplier_name']} ({item['supplier_id']}) | "
            f"Qty: {item['quantity']} | "
            f"Chosen Price: ${float(item['supplier_price']):.2f} | "
            f"Lowest Available: ${float(item['lowest_supplier_price']):.2f} {cheapest_flag}"
        )

    input("\nPress Enter to return...")

def view_store_orders(store_id):
    while True:
        clear_screen()
        print("Store Orders  (most recent 50)")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT o.order_id, o.order_date, o.order_type,
                   o.order_status, o.delivery_method, o.total_amount,
                   COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name
            FROM orders o
            LEFT JOIN customer c ON o.c_id = c.c_id
            WHERE o.st_id = %s
            ORDER BY o.order_date DESC
            LIMIT 50
            """,
            (store_id,)
        )
        orders = cursor.fetchall()
        cursor.close()

        if not orders:
            print("No orders found for this store.")
        else:
            for ord_ in orders:
                print(
                    f"  Order ID: {ord_['order_id']}"
                    f"  |  {ord_['order_date']}"
                    f"  |  Type: {ord_['order_type'] or 'N/A'}"
                    f"  |  Status: {ord_['order_status']}"
                    f"  |  Total: ${ord_['total_amount'] or 0:,.2f}"
                    f"  |  Customer: {ord_['customer_name']}"
                )

        print("\nOptions:")
        print("1. View Order Details")
        print("2. Return")

        choice = input("Please enter your choice (1-2): ").strip()

        if choice == "1":
            order_id = input("Enter Order ID: ").strip()
            view_store_order_details(order_id, store_id)
        elif choice == "2":
            return
        else:
            print("Invalid choice.")
            time.sleep(2)

def view_store_order_details(order_id, store_id):
    clear_screen()
    print(f"Viewing Order {order_id}")

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT o.order_id, o.order_date, o.order_type,
               o.order_status, o.delivery_method, o.total_amount,
               COALESCE(CONCAT(c.first_name, ' ', c.last_name), 'Guest') AS customer_name,
               c.email AS customer_email,
               CONCAT(e.first_name, ' ', e.last_name) AS employee_name
        FROM orders o
        LEFT JOIN customer c ON o.c_id = c.c_id
        LEFT JOIN employee e ON o.e_id = e.e_id
        WHERE o.order_id = %s AND o.st_id = %s
        """,
        (order_id, store_id)
    )
    order = cursor.fetchone()

    if not order:
        print(f"Order {order_id} not found for this store.")
        cursor.close()
        input("\nPress Enter to return...")
        return

    print(f"Order ID    : {order['order_id']}")
    print(f"Date        : {order['order_date']}")
    print(f"Type        : {order['order_type']}")
    print(f"Status      : {order['order_status']}")
    print(f"Delivery    : {order['delivery_method'] or 'N/A'}")
    print(f"Customer    : {order['customer_name']}  ({order['customer_email'] or 'N/A'})")
    print(f"Handled by  : {order['employee_name'] or 'N/A'}")
    print(f"Total       : ${order['total_amount'] or 0:,.2f}")
    print("-----------------------------")
    print("Items:")

    cursor.execute(
        """
        SELECT oc.prod_id, p.name, oc.quantity,
               oc.price_at_purchase,
               (oc.quantity * oc.price_at_purchase) AS line_total
        FROM order_contains oc
        JOIN product p ON oc.prod_id = p.prod_id
        WHERE oc.order_id = %s
        """,
        (order_id,)
    )
    items = cursor.fetchall()

    cursor.execute(
        "SELECT method, amount, payment_status, payment_time "
        "FROM payments WHERE order_id = %s",
        (order_id,)
    )
    payment = cursor.fetchone()
    cursor.close()

    for item in items:
        print(
            f"  Prod ID: {item['prod_id']}"
            f"  |  {item['name']}"
            f"  |  Qty: {item['quantity']}"
            f"  |  Price: ${item['price_at_purchase']:,.2f}"
            f"  |  Line Total: ${item['line_total']:,.2f}"
        )

    if payment:
        print("-----------------------------")
        print(
            f"Payment  : {payment['method']}"
            f"  |  ${payment['amount']:,.2f}"
            f"  |  Status: {payment['payment_status']}"
            f"  |  Time: {payment['payment_time']}"
        )

    input("\nPress Enter to return...")

def change_employee_salary(store_id, manager_e_id):
    while True:
        clear_screen()
        print("Change Employee Salary")

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e_id, first_name, last_name, role, salary
            FROM employee
            WHERE st_id = %s
              AND is_current = TRUE
              AND role != 'store_manager'
            ORDER BY role, last_name
            """,
            (store_id,)
        )
        employees = cursor.fetchall()
        cursor.close()

        if not employees:
            print("No eligible employees found.")
            input("\nPress Enter to return...")
            return

        for emp in employees:
            print(
                f"  ID: {emp['e_id']}"
                f"  |  {emp['first_name']} {emp['last_name']}"
                f"  |  Role: {emp['role']}"
                f"  |  Current Salary: ${emp['salary'] or 0:,.2f}"
            )

        print("\nEnter Employee ID to update (or press Enter to cancel): ", end="")
        target_id = input().strip()
        if not target_id:
            return

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e_id, first_name, last_name, role, salary
            FROM employee
            WHERE e_id = %s
              AND st_id = %s
              AND is_current = TRUE
              AND role != 'store_manager'
            """,
            (target_id, store_id)
        )
        target = cursor.fetchone()
        cursor.close()

        if not target:
            print("Employee not found, not active, or you cannot change a store manager's salary.")
            time.sleep(2)
            continue

        print(
            f"\n{target['first_name']} {target['last_name']}"
            f" — current salary: ${target['salary'] or 0:,.2f}"
        )
        new_salary = input("Enter new salary (or press Enter to cancel): ").strip()
        if not new_salary:
            continue

        try:
            new_salary = float(new_salary)
            if new_salary < 0:
                raise ValueError
        except ValueError:
            print("Invalid salary. Please enter a positive number.")
            time.sleep(2)
            continue

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "UPDATE employee SET salary = %s WHERE e_id = %s",
            (new_salary, target_id)
        )
        db.commit()
        cursor.close()

        print(f"Salary updated to ${new_salary:,.2f} for {target['first_name']} {target['last_name']}.")
        logger.info(
            f"Manager '{manager_e_id}' changed salary of employee '{target_id}' "
            f"from ${target['salary'] or 0:.2f} to ${new_salary:.2f} in store '{store_id}'."
        )
        time.sleep(2)

def view_store_pin(store_id):
    print(f"Viewing Store PIN for Store {store_id}")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT store_pin FROM store WHERE st_id = %s", (store_id,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        print(f"Store PIN for Store {store_id}: {row['store_pin']}")
    else:
        print("Store not found.")

    input("\nPress Enter to return...")

def view_supplier_pin(store_id):
    print(f"Viewing Supplier PIN for Store {store_id}")

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT supplier_pin FROM store WHERE st_id = %s", (store_id,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        print(f"Supplier PIN for Store {store_id}: {row['supplier_pin']}")
    else:
        print("Store not found.")

    input("\nPress Enter to return...")