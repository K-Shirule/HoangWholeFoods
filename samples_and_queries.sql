insert into billing_term (billing_term, description) values
('NET30', 'Payment is due within 30 days of the invoice date.'),
('NET45', 'Payment is due within 45 days of the invoice date.'),
('NET60', 'Payment is due within 60 days of the invoice date.'),
('NET90', 'Payment is due within 90 days of the invoice date.'),
('Prepaid', 'Payment is required before the goods are shipped.'),
('COD', 'Cash on Delivery - payment is made at the time of delivery.');

insert into supplier (supplier_name, email, address, password_hash, billing_term, phone) values
('Fresh Co', 'salesteam@fresh.com', '209 S 20th St, Stockton, CA', '1hbkj34', 'NET30', '408-132-1234'),
('HHEEBB Ltd', 'info@hheebb.com', '12405 N Gessner Rd, Houston, TX', 'hh341h1', 'NET60', '713-555-4321'),
('Vegetable Supplies Ltd', 'sales@vegetablesupplies.com', '1900 Davis St, Chicago, IL', '34bkj23', 'NET45', '510-232-8839'),
('Wholesale', 'info@wholesale.com', '976 3rd Ave, Brooklyn, NY', 'bk342bj', 'COD', '248-421-2343'),
('Farmers Co', 'sales@farmers.com', '6255 E Grant Rd, Tucson, AZ', '2nbj42k', 'NET45', '312-555-6789');

insert into supplier_order (so_id, supplier_id, date_of_order, total_amount, payment_method, status, expected_delivery_date, received_date, tracking_number, st_id) values
(1, 1, '2026-01-15', 500.00, 'Credit Card', 'Shipped', '2024-01-20', null, 'TRACK20260115', 1),
(1, 2, '2026-02-10', 300.00, 'Wire Transfer', 'Delivered', '2024-01-25', '2024-01-24', 'TRACK20260210', 2),
(2, 1, '2026-03-05', 400.00, 'Wire Transfer', 'Pending', null, null, null, 3),
(1, 3, '2026-04-20', 525.00, 'Credit Card', 'Shipped', '2024-01-30', null, 'TRACK20260420', 1);

insert into so_contains (so_id, supplier_id, prod_id, quantity, cost_at_purchase) values
(1, 1, 1, 100, 5.00),
(1, 2, 2, 50, 6.00),
(2, 1, 3, 200, 2.00),
(1, 3, 4, 150, 3.50);

insert into supplies (supplier_id, prod_id) values
(1, 1),
(2, 2),
(1, 3),
(3, 4);


-- insert new supplier without having all information
INSERT INTO supplier (supplier_name, email, password_hash, billing_term)
VALUES ('Greens', 'sales@greens.com', 'g34h1j2', 'Prepaid');

-- update the new supplier with the missing information
UPDATE supplier
SET address = '3980 Venture Dr, Duluth, GA', phone = '720-123-2632'
WHERE supplier_name = 'Greens';

-- show current billing terms for all suppliers
SELECT *
FROM billing_term;

-- show all suppliers
SELECT *
FROM supplier;

-- show all supplier orders
SELECT *
FROM supplier_order;

-- show all products in all supplier orders
SELECR *
FROM so_contains;

-- show all products supplied by each supplier
SELECT s.supplier_id, sp.supplier_name, s.prod_id, p.name
FROM supplier sp JOIN supplies s ON sp.supplier_id = s.supplier_id
                JOIN product p ON s.prod_id = p.prod_id
ORDER BY sp.supplier_name ASC;
        
-- show all orders with their corresponding supplier names and billing terms
SELECT sp.supplier_name, so.so_id, b.billing_term, so.total_amount, so.status
FROM supplier_order so JOIN supplier sp ON so.supplier_id = sp.supplier_id
                    JOIN billing_term b ON sp.billing_term = b.billing_term
ORDER BY so.so_id ASC;

-- show supplier that have pending orders, and total of pending orders
SELECT sp.supplier_name, COUNT(so.so_id) AS pending_orders
FROM supplier sp JOIN supplier_order so ON sp.supplier_id = so.supplier_id
WHERE so.status = 'Pending'
GROUP BY sp.supplier_name
ORDER BY sp.supplier_name ASC;

-- show the total orders for each supplier
SELECT sp.supplier_name, COUNT(so.so_id) AS total_orders
FROM supplier sp JOIN supplier_order so ON sp.supplier_id = so.supplier_id
GROUP BY sp.supplier_name
ORDER BY total_orders DESC;

