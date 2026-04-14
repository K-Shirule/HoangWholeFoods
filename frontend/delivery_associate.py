import time
from frontend.utils import clear_screen
from logger_config import get_logger

logger = get_logger()


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

    # TODO:
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

    input("\nPress Enter to return...")


def claim_delivery(store_id, employee_id):
    clear_screen()
    print("Claim a Delivery")
    print("-----------------------------")

    # TODO:
    # Show all pending deliveries for this store first
    # so the employee can choose one to claim

    delivery_id = input("Enter Delivery ID to claim: ").strip()

    # TODO:
    # 1. Verify this delivery belongs to the employee's store
    # 2. Verify delivery status is 'pending'
    # 3. Verify e_id is currently NULL / unassigned
    # 4. Update delivery_record:
    #       - e_id = employee_id
    #       - delivery_status = 'claimed'

    print(f"Delivery {delivery_id} successfully claimed.")
    logger.info(f"Delivery associate '{employee_id}' claimed delivery '{delivery_id}'.")
    time.sleep(2)


def view_my_deliveries(store_id, employee_id):
    while True:
        clear_screen()
        print("My Deliveries")
        print("-----------------------------")

        # TODO:
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

    # TODO:
    # Query database for full delivery details.
    # Make sure:
    # - delivery belongs to this employee
    # - delivery belongs to this store
    #
    # Suggested information:
    # - delivery_record fields
    # - related order info from orders
    # - ordered items from order_contains if desired

    input("\nPress Enter to return...")


def update_delivery_status(store_id, employee_id):
    clear_screen()
    print("Update Delivery Status")
    print("-----------------------------")

    # TODO:
    # Show this employee's claimed deliveries

    delivery_id = input("Enter Delivery ID for which you want to update status: ").strip()

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

        elif choice == "2":
            new_status = "Completed"

        elif choice == "3":
            new_status = "Failed"

        elif choice == "4":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)
            continue

        # TODO:
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

        print(f"Delivery {delivery_id} updated to status '{new_status}'.")
        logger.info(
            f"Delivery associate '{employee_id}' updated delivery '{delivery_id}' to '{new_status}'."
        )
        time.sleep(2)
        return
