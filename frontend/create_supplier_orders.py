from time import sleep
def create_supplier_orders_from_restock_list(list_id, store_id):
    print(f"\nConverting Restock List {list_id} into Supplier Orders...")
    print("----------------------------------------------------------")

    # TODO:

    #IMP Edge Cases: 
    #   a.  if a product in the list is no longer supplied just print message saying
    # "Product - product_id is no longer supplied by any supplier"
    #   b. if a product has more than one supplier just pick the cheapest one in the list I guess.
    #
    # 1. Query restock_contains for all items in this restock list
    #    Needed fields:
    #    - prod_id
    #    - quantity
    #
    # 2. For each product, find which supplier supplies it using supplies table
    #    Needed fields:
    #    - supplier_id
    #    - prod_id
    #
    # 3. Group products by supplier_id
    #
    #    Example target structure:
    #    supplier_orders = {
    #        3: [(1, 5), (2, 4)],   # supplier 3 gets product 1 qty 5, product 2 qty 4
    #        8: [(7, 2)]
    #    }
    #
    # 4. For each supplier_id group:
    #    a. Generate/create a new supplier_order
    #    b. Insert one row into supplier_order
    #       using:
    #       - so_id
    #       - supplier_id
    #       - date_of_order
    #       - total_amount
    #       - payment_method
    #       - status
    #       - st_id = store_id
    #
    # 5. For each product in that supplier's group:
    #    insert into so_contains:
    #       - so_id
    #       - supplier_id
    #       - prod_id
    #       - quantity
    #       - cost_at_purchase
    #
    # 6. Update restock_list status after conversion
    #    Example:
    #       status = 'ordered'
    
    # 7. Add to the log files using this format:
    #   logger.info(f" supplier order '{so_id}' created for supplier {supplier_id} using restock list {list_id} for store {store_id}") 

    print("Supplier orders created successfully from the approved restock list.")

    sleep(3)
    return True