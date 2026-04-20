from time import sleep
from utils import clear_screen
from logger_config import get_logger
from db_connector import db
from datetime import date

logger = get_logger()

def create_supplier_orders_from_restock_list(list_id, store_id):
    print(f"\nConverting Restock List {list_id} into Supplier Orders...")
    print("----------------------------------------------------------")

    #Query restock_contains for all items in this restock list
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT list_id, prod_id, quantity
        FROM restock_contains
        WHERE list_id = %s
        """
    cursor.execute(query, (list_id,))
    restock_items = cursor.fetchall()

    if not restock_items:
        print(f"No items found in restock list {list_id}")
        cursor.close()
        return False
    
    #for each product, find which supplier supplies it using supplies table
    supplier_orders = {}
    for item in restock_items:
        prod_id = item['prod_id']
        quantity = item['quantity']

        #find suppliers for this product, order by cost to get the cheapest one first
        query = """
            SELECT prod_id, supplier_id, supplier_price
            FROM supplies
            WHERE prod_id = %s
            ORDER BY supplier_price ASC
            """
        cursor.execute(query, (prod_id,))
        suppliers = cursor.fetchall()

        if not suppliers:
            print(f"Product {prod_id} is no longer supplied by any supplier")
            continue
        
        #pick the cheapest supplier
        cheapest_supplier = suppliers[0]
        supplier_id = cheapest_supplier['supplier_id']
        supplier_price = cheapest_supplier['supplier_price']

        #initialize list for this supplier if not created yet
        if supplier_id not in supplier_orders:  
            supplier_orders[supplier_id] = []
        
        supplier_orders[supplier_id].append((prod_id, quantity, supplier_price))
        #Example target structure:
        #    supplier_orders = {
        #        3: [(1, 5, 2.0), (2, 4,3.0)],   # supplier 3 gets product 1 qty 5, product 2 qty 4
        #        8: [(7, 2, 2.0)]
        #    }
        #supplier_id = 3, products = [(1, 5, 2.0), (2, 4,3.0)] 

    if not supplier_orders:
        print("No supplier orders could be created from this restock list.")
        cursor.close()
        return False
    
    #create one supplier order per supplier
    today = date.today()
    for supplier_id, products in supplier_orders.items():
        #calculate total amount for this supplier order
        total_amount = 0
        for item in products:
            prod_id, quantity, price = item
            total_amount += quantity * price  

        #insert into supplier_order
        query = """
            INSERT INTO supplier_order (supplier_id, date_of_order, total_amount, payment_method, status, st_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        
        cursor.execute(query, (supplier_id, today, total_amount, 'credit_card', 'ordered', store_id))
        so_id = cursor.lastrowid  # get the generated so_id

        #insert into so_contains for each product in this supplier order
        query = """
            INSERT INTO so_contains (so_id, supplier_id, prod_id, quantity, cost_at_purchase)
            VALUES (%s, %s, %s, %s, %s)
            """
        
        values = []
        for item in products:
            prod_id, quantity, price = item
            values.append((so_id, supplier_id, prod_id, quantity, price))
        cursor.executemany(query, values)

        logger.info(f"Supplier order '{so_id}' created for supplier {supplier_id} using restock list {list_id} for store {store_id}")
        print(f"Supplier order '{so_id}' created for supplier {supplier_id} with total amount ${total_amount:.2f}")

    cursor.execute("UPDATE restock_list SET status = 'ordered' WHERE list_id = %s", (list_id,))
    db.commit()
    cursor.close()

    print("Supplier orders created successfully from the approved restock list.")

    sleep(3)
    return True