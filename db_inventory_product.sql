-- Standalone seed file for the expanded inventory/product dataset.
-- Use this as an alternative to db_testdata.sql when you want richer
-- inventory and product testing data. Do not run both files together
-- against the same fresh database unless you intentionally want duplicates.

CREATE USER 'admin'@'localhost' IDENTIFIED BY '1234';

GRANT ALL PRIVILEGES ON hoangwholefoods.* TO 'admin'@'localhost';

FLUSH PRIVILEGES;

INSERT INTO billing_term (billing_term, description)
VALUES
('net15', 'Payment due in 15 days'),
('net30', 'Payment due in 30 days'),
('net45', 'Payment due in 45 days');

INSERT INTO store (location, branch_name, phone, email, address, store_pin, supplier_pin)
VALUES
('San Jose, CA', 'Downtown SJ', '4085551234', 'sj_downtown@hwf.com', '123 Market St', 'K7M3X9', 'T5R8Q2'),
('Santa Clara, CA', 'Santa Clara Central', '4085552345', 'sc_central@hwf.com', '456 El Camino Real', 'P9L4W6', 'H3V7Z8'),
('Sunnyvale, CA', 'Sunnyvale Plaza', '4085553456', 'sv_plaza@hwf.com', '789 Mathilda Ave', 'R6T2Y8', 'M4X9K3'),
('Cupertino, CA', 'Cupertino Square', '4085554567', 'cupertino@hwf.com', '101 Infinite Loop', 'Z8Q5N2', 'B7C3W6');

INSERT INTO category (name, description)
VALUES
('Fruits', 'Fresh fruits sold by weight, bag, or pack'),
('Vegetables', 'Fresh vegetables and salad staples'),
('Dairy', 'Milk, cheese, yogurt, and refrigerated staples'),
('Bakery', 'Bread, pastries, and fresh baked goods'),
('Pantry', 'Shelf-stable staples, grains, oils, and spreads'),
('Beverages', 'Juices, sparkling waters, and bottled drinks'),
('Snacks', 'Packaged snacks, crackers, chips, and bars');

INSERT INTO product (category_id, name, description, unit_price, units, unit_type)
VALUES
(1, 'Bananas', 'Organic bananas sold by weight', 0.59, 1.00, 'lb'),
(1, 'Fuji Apples', 'Sweet crisp Fuji apples', 1.69, 1.00, 'lb'),
(1, 'Blueberries', 'Fresh blueberry clamshell', 4.49, 6.00, 'oz'),
(2, 'Broccoli Crowns', 'Fresh broccoli crowns', 2.19, 1.00, 'lb'),
(2, 'Baby Spinach', 'Triple-washed baby spinach', 3.49, 5.00, 'oz'),
(2, 'Carrots', 'Whole carrots in produce bag', 1.09, 2.00, 'lb'),
(3, 'Whole Milk', 'Half-gallon whole milk', 3.79, 0.50, 'gallon'),
(3, 'Greek Yogurt', 'Plain Greek yogurt tub', 5.99, 32.00, 'oz'),
(3, 'Sharp Cheddar', 'Sharp cheddar cheese block', 5.49, 8.00, 'oz'),
(4, 'Sourdough Loaf', 'Fresh sourdough bread loaf', 4.79, 1.00, 'loaf'),
(4, 'Blueberry Muffins', 'Pack of four bakery muffins', 5.49, 4.00, 'count'),
(5, 'Brown Rice', 'Long grain brown rice bag', 6.99, 2.00, 'lb'),
(5, 'Extra Virgin Olive Oil', 'Cold-pressed olive oil bottle', 12.99, 1.00, 'liter'),
(5, 'Peanut Butter', 'Creamy peanut butter jar', 4.99, 16.00, 'oz'),
(6, 'Orange Juice', 'Fresh orange juice bottle', 4.29, 46.00, 'oz'),
(6, 'Sparkling Water', 'Lemon sparkling water 8-pack', 5.99, 8.00, 'can'),
(7, 'Sea Salt Chips', 'Kettle-cooked potato chips', 2.79, 8.00, 'oz'),
(7, 'Granola Bars', 'Chewy granola bar box', 4.59, 6.00, 'count');

INSERT INTO supplier (supplier_name, email, address, password_hash, billing_term, phone)
VALUES
('Fresh Farm Supply', 'freshfarm@hwf-supplier.com', '789 Supply Rd, Gilroy, CA', '$2b$12$2u3RmopbxuFNkDYsewpDMunF.I4sk3UNVVYdmej7XJ3oxnmEeKHlq', 'net30', '4085559000'),
('Golden State Wholesale', 'goldenstate@hwf-supplier.com', '245 Distribution Ave, Fremont, CA', '$2b$12$F78NgBR82wzuUMmDtheEeeO3fHFTQLIXh6rx5dqkFZ9WE54HTT7We', 'net15', '4085559001'),
('Bay Pantry Partners', 'baypantry@hwf-supplier.com', '512 Commerce Way, San Mateo, CA', '$2b$12$cz3g1tJXmhcoPkzcg/j/yOmTzbFcKnnFyij1xlj9pLZH5slaBNig2', 'net45', '4085559002');

INSERT INTO employee (
    st_id, first_name, last_name, email, phone,
    salary, is_current, password_hash, role, start_date
)
VALUES
(1, 'Jim', 'Halpert', 'jim.halpert@hwf.com', '4085551111', 75000, TRUE, '$2b$12$2u3RmopbxuFNkDYsewpDMunF.I4sk3UNVVYdmej7XJ3oxnmEeKHlq', 'store_manager', CURDATE()),
(2, 'Bruce', 'Wayne', 'bruce.wayne@hwf.com', '4085552222', 76000, TRUE, '$2b$12$F78NgBR82wzuUMmDtheEeeO3fHFTQLIXh6rx5dqkFZ9WE54HTT7We', 'store_manager', CURDATE()),
(3, 'Arry', 'Potta', 'arry.potta@hwf.com', '4085553333', 74000, TRUE, '$2b$12$cz3g1tJXmhcoPkzcg/j/yOmTzbFcKnnFyij1xlj9pLZH5slaBNig2', 'store_manager', CURDATE()),
(4, 'Ishow', 'Speed', 'ishow.speed@hwf.com', '4085554444', 77000, TRUE, '$2b$12$WhdkZ1oUuPgH/gYD9HShreVwd3MmtgSJfW67qZ.daKwl9SzTvrgEW', 'store_manager', CURDATE()),
(1, 'Yen', 'Tran', 'yen.tran@hwf.com', '4085555551', 66000, TRUE, '$2b$12$2u3RmopbxuFNkDYsewpDMunF.I4sk3UNVVYdmej7XJ3oxnmEeKHlq', 'inventory_manager', CURDATE()),
(2, 'Maya', 'Patel', 'maya.patel@hwf.com', '4085555552', 66500, TRUE, '$2b$12$F78NgBR82wzuUMmDtheEeeO3fHFTQLIXh6rx5dqkFZ9WE54HTT7We', 'inventory_manager', CURDATE()),
(3, 'Leo', 'Nguyen', 'leo.nguyen@hwf.com', '4085555553', 65500, TRUE, '$2b$12$cz3g1tJXmhcoPkzcg/j/yOmTzbFcKnnFyij1xlj9pLZH5slaBNig2', 'inventory_manager', CURDATE()),
(4, 'Sara', 'Kim', 'sara.kim@hwf.com', '4085555554', 67000, TRUE, '$2b$12$WhdkZ1oUuPgH/gYD9HShreVwd3MmtgSJfW67qZ.daKwl9SzTvrgEW', 'inventory_manager', CURDATE());

# password = temp123 for the seeded employee accounts.

UPDATE store SET manager_e_id = 1 WHERE st_id = 1;
UPDATE store SET manager_e_id = 2 WHERE st_id = 2;
UPDATE store SET manager_e_id = 3 WHERE st_id = 3;
UPDATE store SET manager_e_id = 4 WHERE st_id = 4;

INSERT INTO supplies (supplier_id, prod_id, supplier_price)
VALUES
(1, 1, 0.35),
(2, 1, 0.38),
(1, 2, 0.92),
(2, 2, 0.95),
(1, 3, 2.85),
(1, 4, 1.25),
(2, 4, 1.32),
(1, 5, 2.10),
(2, 5, 2.05),
(1, 6, 0.62),
(1, 7, 2.45),
(2, 7, 2.52),
(2, 8, 3.90),
(2, 9, 3.55),
(2, 10, 2.85),
(2, 11, 3.20),
(3, 12, 4.10),
(3, 13, 8.40),
(3, 14, 2.95),
(1, 15, 2.65),
(3, 15, 2.75),
(3, 16, 3.60),
(3, 17, 1.85),
(3, 18, 2.95);

INSERT INTO stocks (store_id, prod_id, quantity)
VALUES
(1, 1, 50),
(1, 2, 34),
(1, 4, 22),
(1, 5, 9),
(1, 7, 16),
(1, 10, 12),
(1, 12, 14),
(1, 15, 18),
(1, 17, 20),
(2, 1, 61),
(2, 3, 11),
(2, 6, 27),
(2, 8, 14),
(2, 9, 8),
(2, 11, 10),
(2, 13, 7),
(2, 16, 25),
(3, 2, 19),
(3, 4, 15),
(3, 5, 6),
(3, 7, 13),
(3, 12, 17),
(3, 14, 9),
(3, 18, 21),
(4, 3, 12),
(4, 6, 18),
(4, 8, 20),
(4, 10, 7),
(4, 13, 16),
(4, 15, 9),
(4, 17, 14);

INSERT INTO restock_list (store_id, created_by, approved_by, restock_status, created_at, approved_at)
VALUES
(1, 5, NULL, 'pending', '2026-04-20 09:15:00', NULL),
(2, 6, 2, 'approved', '2026-04-18 10:30:00', '2026-04-18 12:00:00'),
(3, 7, 3, 'ordered', '2026-04-15 08:45:00', '2026-04-15 10:00:00'),
(4, 8, 4, 'delivered', '2026-04-12 14:20:00', '2026-04-12 16:05:00');

INSERT INTO restock_contains (list_id, prod_id, supplier_id, quantity)
VALUES
(1, 5, 2, 24),
(1, 13, 3, 10),
(1, 15, 1, 18),
(2, 9, 2, 20),
(2, 13, 3, 12),
(2, 16, 3, 30),
(3, 5, 2, 16),
(3, 14, 3, 14),
(4, 10, 2, 18),
(4, 17, 3, 24);
