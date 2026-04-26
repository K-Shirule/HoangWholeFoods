# SJSU CMPE 138 SPRING 2026 TEAM6
import time

from db_connector import db
from utils import clear_screen
from logger_config import get_logger


logger = get_logger(__name__)


#helper functions for operations related to customer and product interaction and general product functions
def _fetch_all(query, params=None):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()

def _fetch_one(query, params=None):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()

def _execute(query, params=None):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def _print_product_rows(rows):
    if not rows:
        print("No matching products found.")
        return

    for row in rows:
        units = row.get("units")
        unit_type = row.get("unit_type")
        size_text = ""
        if units is not None and unit_type:
            size_text = f"{units} {unit_type}"
        elif units is not None:
            size_text = str(units)
        elif unit_type:
            size_text = unit_type

        print(
            f"ID: {row['prod_id']} | "
            f"{row['product_name']} | "
            f"Category: {row['category_name']} | "
            f"Price: ${row['unit_price']:.2f} | "
            f"Size: {size_text or 'n/a'} | "
            f"Stock: {row['stock_quantity']}"
        )

def _get_store_products(store_id):
    return _fetch_all(
        """
        SELECT
            p.prod_id,
            p.name AS product_name,
            c.name AS category_name,
            p.unit_price,
            p.units,
            p.unit_type,
            s.quantity AS stock_quantity
        FROM stocks AS s
        JOIN product AS p
            ON s.prod_id = p.prod_id
        JOIN category AS c
            ON p.category_id = c.cat_id
        WHERE s.store_id = %s and s.quantity != 0
        ORDER BY p.name
        """,
        (store_id,),
    )

def view_product_catalog(customer_id, store_id):
    while True:
        clear_screen()
        print("Product Catalog")
        print("-----------------------------")

        while True:
            clear_screen()
            _print_product_rows(_get_store_products(store_id))

            print("\nOptions:")
            print("1. Search Products")
            print("2. View Product Details")
            print("3. Add Product to Cart")
            print("4. Return to Customer Page")

            choice = input("Please enter your choice (1-4): ").strip()

            if choice == "1":
                search_products(store_id)

            elif choice == "2":
                product_id = input("Enter the Product ID to view details: ").strip()
                view_product_details(product_id, customer_id, store_id)

            elif choice == "3":
                product_id = input("Enter the Product ID to add to cart: ").strip()
                quantity = input("Enter quantity: ").strip()

                if not quantity.isdigit() or int(quantity) <= 0:
                    print("Quantity must be a positive integer.")
                    time.sleep(2)
                    continue

                add_product_to_cart(customer_id, product_id, int(quantity), store_id)

            elif choice == "4":
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
            rows = _fetch_all(
                """
                SELECT
                    p.prod_id,
                    p.name AS product_name,
                    c.name AS category_name,
                    p.unit_price,
                    p.units,
                    p.unit_type,
                    s.quantity AS stock_quantity
                FROM stocks AS s
                JOIN product AS p
                    ON s.prod_id = p.prod_id
                JOIN category AS c
                    ON p.category_id = c.cat_id
                WHERE s.store_id = %s
                  AND p.name LIKE %s
                ORDER BY p.name
                """,
                (store_id, f"%{keyword}%"),
            )

            print(f"\nShowing results for product name containing '{keyword}'...")
            _print_product_rows(rows)
            input("\nPress Enter to continue...")
            category_formatted = f"%{category}%"

        elif choice == "2":
            category = input("Enter category name: ").strip()
            rows = _fetch_all(
                """
                SELECT
                    p.prod_id,
                    p.name AS product_name,
                    c.name AS category_name,
                    p.unit_price,
                    p.units,
                    p.unit_type,
                    s.quantity AS stock_quantity
                FROM stocks AS s
                JOIN product AS p
                    ON s.prod_id = p.prod_id
                JOIN category AS c
                    ON p.category_id = c.cat_id
                WHERE s.store_id = %s
                  AND (c.name LIKE \% %s OR c.description LIKE %s)
                ORDER BY p.name
                """,
                (store_id, category_formatted, category_formatted),
            )

            print(f"\nShowing results for category '{category}'...")
            _print_product_rows(rows)
            input("\nPress Enter to continue...")

        elif choice == "3":
            min_price = input("Enter minimum price: ").strip()
            max_price = input("Enter maximum price: ").strip()

            try:
                min_price = float(min_price)
                max_price = float(max_price)

                if min_price < 0 or max_price < 0 or min_price > max_price:
                    print("Invalid price range.")
                    time.sleep(2)
                    continue

                rows = _fetch_all(
                    """
                    SELECT
                        p.prod_id,
                        p.name AS product_name,
                        c.name AS category_name,
                        p.unit_price,
                        p.units,
                        p.unit_type,
                        s.quantity AS stock_quantity
                    FROM stocks AS s
                    JOIN product AS p
                        ON s.prod_id = p.prod_id
                    JOIN category AS c
                        ON p.category_id = c.cat_id
                    WHERE s.store_id = %s
                      AND p.unit_price BETWEEN %s AND %s
                    ORDER BY p.unit_price, p.name
                    """,
                    (store_id, min_price, max_price),
                )

                print(f"\nShowing results from ${min_price:.2f} to ${max_price:.2f}...")
                _print_product_rows(rows)
                input("\nPress Enter to continue...")

            except ValueError:
                print("Please enter valid numeric prices.")
                time.sleep(2)

        elif choice == "4":
            return

        else:
            print("Invalid choice. Please try again.")
            time.sleep(2)


def view_product_details(product_id, customer_id, store_id):
    while True:
        clear_screen()
        print(f"Viewing details for Product ID: {product_id}")
        print("-----------------------------")

        if not str(product_id).isdigit():
            print("Product ID must be numeric.")
            time.sleep(2)
            return

        product = _fetch_one(
            """
            SELECT
                p.prod_id,
                p.name,
                p.description,
                p.unit_price,
                p.units,
                p.unit_type,
                c.name AS category_name,
                COALESCE(s.quantity, 0) AS stock_quantity,
                COALESCE(AVG(CAST(r.rating AS UNSIGNED)), 0) AS average_rating,
                COUNT(r.review_id) AS review_count
            FROM product AS p
            JOIN category AS c
                ON p.category_id = c.cat_id
            LEFT JOIN stocks AS s
                ON p.prod_id = s.prod_id
               AND s.store_id = %s
            LEFT JOIN review AS r
                ON p.prod_id = r.prod_id
            WHERE p.prod_id = %s
            GROUP BY
                p.prod_id,
                p.name,
                p.description,
                p.unit_price,
                p.units,
                p.unit_type,
                c.name,
                s.quantity
            """,
            (store_id, int(product_id)),
        )

        if not product:
            print("Product not found.")
            time.sleep(2)
            return

        print(f"Name: {product['name']}")
        print(f"Category: {product['category_name']}")
        print(f"Description: {product['description'] or 'No description available.'}")
        print(f"Price: ${product['unit_price']:.2f}")
        print(f"Units: {product['units'] or 'n/a'}")
        print(f"Unit Type: {product['unit_type'] or 'n/a'}")
        print(f"Stock Availability: {product['stock_quantity']}")
        print(f"Average Rating: {product['average_rating']:.2f}")
        print(f"Review Count: {product['review_count']}")

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

            add_product_to_cart(customer_id, product_id, int(quantity), store_id)

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

    if not str(product_id).isdigit():
        print("Product ID must be numeric.")
        input("\nPress Enter to return...")
        return

    reviews = _fetch_all(
        """
        SELECT
            CONCAT(c.first_name, ' ', LEFT(c.last_name, 1), '.') AS customer_name,
            r.rating,
            r.r_comment,
            r.created_at
        FROM review AS r
        JOIN customer AS c
            ON r.c_id = c.c_id
        WHERE r.prod_id = %s
        ORDER BY r.created_at DESC
        """,
        (int(product_id),),
    )

    if not reviews:
        print("No reviews found for this product.")
    else:
        for review in reviews:
            print(
                f"{review['customer_name']} | "
                f"Rating: {review['rating']} | "
                f"{review['created_at']}"
            )
            print(f"Comment: {review['r_comment'] or 'No comment provided.'}")
            print("-" * 40)

    input("\nPress Enter to return...")


def add_product_to_cart(customer_id, product_id, quantity, store_id):
    cursor = db.cursor(dictionary=True)
    print("\nAdding product to cart...")

    try:
        if not str(customer_id).isdigit() or not str(product_id).isdigit() or not str(store_id).isdigit():
            print("Customer ID, Product ID, and Store ID must be numeric.")
            time.sleep(2)
            return

        customer_id = int(customer_id)
        product_id = int(product_id)
        store_id = int(store_id)

        # Check stock at selected store
        cursor.execute(
            """
            SELECT quantity
            FROM stocks
            WHERE store_id = %s AND prod_id = %s
            """,
            (store_id, product_id),
        )
        stock_row = cursor.fetchone()

        if not stock_row:
            print("That product is not stocked at the selected store.")
            time.sleep(2)
            return

        # Get or create the customer's one cart
        cursor.execute(
            """
            SELECT cart_id, cart_status, st_id
            FROM shopping_cart
            WHERE c_id = %s
            LIMIT 1
            """,
            (customer_id,),
        )
        cart = cursor.fetchone()

        if not cart:
            cursor.execute(
                """
                INSERT INTO shopping_cart (created_at, cart_status, c_id, st_id)
                VALUES (CURRENT_TIMESTAMP, 'new', %s, %s)
                """,
                (customer_id, store_id),
            )
            db.commit()
            cart_id = cursor.lastrowid
            cart_store_id = store_id

        else:
            cart_id = cart["cart_id"]
            cart_store_id = cart["st_id"]

            # If cart is empty/unassigned, assign it to this store
            if cart_store_id is None:
                cursor.execute(
                    """
                    UPDATE shopping_cart
                    SET st_id = %s, cart_status = 'new'
                    WHERE cart_id = %s
                    """,
                    (store_id, cart_id),
                )
                db.commit()
                cart_store_id = store_id

            # Block adding from a different store
            if cart_store_id != store_id:
                print("Your cart already has items from another store.")
                print("Please clear your cart or checkout before adding items from a different store.")
                time.sleep(3)
                return

            # If cart was somehow marked done, reopen it
            if cart["cart_status"] != "new":
                cursor.execute(
                    """
                    UPDATE shopping_cart
                    SET cart_status = 'new'
                    WHERE cart_id = %s
                    """,
                    (cart_id,),
                )
                db.commit()

        # Check how many of this product are already in cart
        cursor.execute(
            """
            SELECT quantity
            FROM cart_contains
            WHERE cart_id = %s AND prod_id = %s
            """,
            (cart_id, product_id),
        )
        cart_item = cursor.fetchone()

        current_cart_qty = cart_item["quantity"] if cart_item else 0
        requested_total = quantity + current_cart_qty

        if requested_total > stock_row["quantity"]:
            print(
                f"Only {stock_row['quantity']} unit(s) are available at this store. "
                f"Your cart already contains {current_cart_qty}."
            )
            time.sleep(2)
            return

        # Insert or update cart item
        if cart_item:
            cursor.execute(
                """
                UPDATE cart_contains
                SET quantity = quantity + %s
                WHERE cart_id = %s AND prod_id = %s
                """,
                (quantity, cart_id, product_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO cart_contains (cart_id, prod_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (cart_id, product_id, quantity),
            )

        db.commit()

        print(f"Product {product_id} added to cart (Quantity: {quantity}).")
        logger.info(
            f"Customer '{customer_id}' added product '{product_id}' to cart with quantity '{quantity}' from store '{store_id}'."
        )
        time.sleep(2)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add product '{product_id}' to cart for customer '{customer_id}': {e}")
        print("Failed to add product to cart.")
        time.sleep(2)

    finally:
        cursor.close()