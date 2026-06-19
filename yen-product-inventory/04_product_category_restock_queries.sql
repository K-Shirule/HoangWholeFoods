-- SJSU CMPE 138 SPRING 2026 TEAM6
USE hoang_whole_foods;

-- 1. View all products together with their category names.
SELECT
    p.prod_id,
    p.name AS product_name,
    c.name AS category_name,
    p.unit_price,
    p.units,
    p.unit_type
FROM product AS p
JOIN category AS c
    ON p.category_id = c.cat_id
ORDER BY c.name, p.name;

-- 2. View stock quantities for each product by store.
SELECT
    s.store_id,
    p.prod_id,
    p.name AS product_name,
    s.quantity
FROM stocks AS s
JOIN product AS p
    ON s.prod_id = p.prod_id
ORDER BY s.store_id, p.name;

-- 3. Find low-stock products with quantity below 10 units.
SELECT
    s.store_id,
    p.name AS product_name,
    s.quantity
FROM stocks AS s
JOIN product AS p
    ON s.prod_id = p.prod_id
WHERE s.quantity < 10
ORDER BY s.quantity ASC, p.name;

-- 4. View all products included in a specific restock list (example: list_id = 1).
SELECT
    rc.list_id,
    p.prod_id,
    p.name AS product_name,
    rc.quantity AS requested_quantity
FROM restock_contains AS rc
JOIN product AS p
    ON rc.prod_id = p.prod_id
WHERE rc.list_id = 1
ORDER BY p.name;

-- 5. Create a new restock list for store 1 by employee 101.
INSERT INTO restock_list (store_id, created_by, approved_by, status, created_at, approved_at)
VALUES (1, 101, NULL, 'pending', NOW(), NULL);

-- 6. Add a product to a restock list (example: add product 3 to list 1).
INSERT INTO restock_contains (list_id, prod_id, quantity)
VALUES (1, 3, 12);

-- 7. Approve a restock list by assigning approver 103 and timestamp.
UPDATE restock_list
SET approved_by = 103,
    status = 'approved',
    approved_at = NOW()
WHERE list_id = 1;

-- 8. View pending restock lists with creator and approver employee IDs.
SELECT
    list_id,
    store_id,
    created_by,
    approved_by,
    status,
    created_at,
    approved_at
FROM restock_list
WHERE status = 'pending'
ORDER BY created_at;

-- 9. Show the total requested quantity for each restock list.
SELECT
    rl.list_id,
    rl.store_id,
    rl.status,
    SUM(rc.quantity) AS total_requested_units
FROM restock_list AS rl
JOIN restock_contains AS rc
    ON rl.list_id = rc.list_id
GROUP BY rl.list_id, rl.store_id, rl.status
ORDER BY rl.list_id;

-- 10. View products that have not yet been stocked in any store.
SELECT
    p.prod_id,
    p.name AS product_name
FROM product AS p
LEFT JOIN stocks AS s
    ON p.prod_id = s.prod_id
WHERE s.prod_id IS NULL
ORDER BY p.name;
