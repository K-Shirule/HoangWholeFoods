import time
from utils import clear_screen
from logger_config import get_logger

logger = get_logger()


def view_product_catalog(customer_id):
    while True:
        clear_screen()
        print("Product Catalog")
        print("-----------------------------")
        print("Please select the store you want to browse:")
        #query to display all the store info like name, location etc.
        store_id = input("Enter Store ID: ").strip()
        #make sure the store_id is valid and is less than the no. of rows returned by the above query
        # TODO:
        # Query database to display all products at that store.
        # - product ID
        # - product name
        # - category
        # - price
        # - unit type / units
        # - stock availability

        print("\nOptions:")
        print("1. Search Products")
        print("2. View Product Details")
        print("3. Add Product to Cart")
        print("4. Change Store")
        print("5. Return to Customer Page")

        choice = input("Please enter your choice (1-5): ").strip()

        if choice == "1":
            search_products(store_id)

        elif choice == "2":
            product_id = input("Enter the Product ID to view details: ").strip()
            view_product_details(product_id, customer_id)

        elif choice == "3":
            product_id = input("Enter the Product ID to add to cart: ").strip()
            quantity = input("Enter quantity: ").strip()

            if not quantity.isdigit() or int(quantity) <= 0:
                print("Quantity must be a positive integer.")
                time.sleep(2)
                continue

            add_product_to_cart(customer_id, product_id, int(quantity))

        elif choice == "4":
            continue  # will loop back to the store selection

        elif choice == "5":
            return 

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def search_products(store_id):
    while True:
        clear_screen()
        print("Search Products")
        print("-----------------------------")
        print("1. Search by Product Name")
        print("2. Search by Category")
        print("3. Search by Price Range")
        print("4. Return to Product Catalog")

        choice = input("Please enter your choice (1-4): ").strip()

        if choice == "1":
            keyword = input("Enter product name keyword: ").strip()

            # TODO:
            # Query database for products where name matches keyword

            print(f"\nShowing results for product name containing '{keyword}'...")
            input("\nPress Enter to continue...")

        elif choice == "2":
            category = input("Enter category name: ").strip()

            # TODO:
            # Query database for products in the selected category

            print(f"\nShowing results for category '{category}'...")
            input("\nPress Enter to continue...")

        elif choice == "3":
            min_price = input("Enter minimum price: ").strip()
            max_price = input("Enter maximum price: ").strip()

            # Optional validation
            try:
                min_price = float(min_price)
                max_price = float(max_price)

                if min_price < 0 or max_price < 0 or min_price > max_price:
                    print("Invalid price range.")
                    time.sleep(2)
                    continue

                # TODO:
                # Query database for products within the price range

                print(f"\nShowing results from ${min_price:.2f} to ${max_price:.2f}...")
                input("\nPress Enter to continue...")

            except ValueError:
                print("Please enter valid numeric prices.")
                time.sleep(2)

        elif choice == "4":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_product_details(product_id, customer_id):
    while True:
        clear_screen()
        print(f"Viewing details for Product ID: {product_id}")
        print("-----------------------------")

        # TODO:
        # Query database for full product details using product_id
        # Suggested fields:
        # - name
        # - description
        # - unit_price
        # - units
        # - unit_type
        # - category name
        # - stock availability
        # - average rating
        # - reviews

        print("\nOptions:")
        print("1. Add Product to Cart")
        print("2. View Reviews")
        print("3. Return to Product Catalog")

        choice = input("Please enter your choice (1-3): ").strip()

        if choice == "1":
            quantity = input("Enter quantity: ").strip()

            if not quantity.isdigit() or int(quantity) <= 0:
                print("Quantity must be a positive integer.")
                time.sleep(2)
                continue

            add_product_to_cart(customer_id, product_id, int(quantity))

        elif choice == "2":
            view_product_reviews(product_id)

        elif choice == "3":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_product_reviews(product_id):
    clear_screen()
    print(f"Viewing reviews for Product ID: {product_id}")
    print("-----------------------------")

    # TODO:
    # Query database to display all reviews for this product
    # Suggested fields:
    # - customer name (or partial display)
    # - rating
    # - comment
    # - created_at

    input("\nPress Enter to return...")


def add_product_to_cart(customer_id, product_id, quantity):
    print("\nAdding product to cart...")

    # TODO:
    # 1. Check if customer already has a shopping cart with status = 'new'
    # 2. If not, create a new shopping cart for this customer
    # 3. Check if product already exists in cart_contains
    # 4. If yes, update quantity
    # 5. If no, insert a new row into cart_contains
    # 6. make sure to check if the desired quantity is available in stock before adding to cart

    print(f"Product {product_id} added to cart (Quantity: {quantity}).")
    logger.info(
        f"Customer '{customer_id}' added product '{product_id}' to cart with quantity '{quantity}'."
    )
    time.sleep(2)
