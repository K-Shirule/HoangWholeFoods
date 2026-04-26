-- # SJSU CMPE 138 SPRING 2026 TEAM6
CREATE USER 'admin'@'localhost' IDENTIFIED BY '1234';

GRANT ALL PRIVILEGES ON hoangwholefoods.* TO 'admin'@'localhost';

FLUSH PRIVILEGES;

INSERT INTO store (location, branch_name, phone, email, address, store_pin, supplier_pin)
VALUES
('San Jose, CA', 'Downtown SJ', '4085551234', 'sj_downtown@hwf.com', '123 Market St', 'K7M3X9', 'T5R8Q2'),
('Santa Clara, CA', 'Santa Clara Central', '4085552345', 'sc_central@hwf.com', '456 El Camino Real', 'P9L4W6', 'H3V7Z8'),
('Sunnyvale, CA', 'Sunnyvale Plaza', '4085553456', 'sv_plaza@hwf.com', '789 Mathilda Ave', 'R6T2Y8', 'M4X9K3'),
('Cupertino, CA', 'Cupertino Square', '4085554567', 'cupertino@hwf.com', '101 Infinite Loop', 'Z8Q5N2', 'B7C3W6');

INSERT INTO category (name, description)
VALUES
('Fruits', 'Fresh fruits'),
('Vegetables', 'Fresh vegetables'),
('Dairy', 'Milk, cheese, and dairy products'),
('Snacks', 'Packaged snacks'),
('Other', 'Other Products'),
('Beverages', 'Drinks and juices');

INSERT INTO product (category_id, name, description, unit_price, units, unit_type)
VALUES
(1, 'Bananas', 'Organic bananas', 0.59, 1, 'lb'),
(1, 'Apples', 'Red delicious apples', 1.49, 1, 'lb'),
(2, 'Broccoli', 'Fresh broccoli crowns', 2.19, 1, 'lb'),
(2, 'Carrots', 'Whole carrots', 1.09, 2, 'lb'),
(3, 'Milk', 'Whole milk gallon', 3.79, 0.5, 'gallon'),
(3, 'Cheddar Cheese', 'Sharp cheddar block', 5.49, 1, 'pack'),
(4, 'Potato Chips', 'Sea salt chips', 2.79, 12, 'oz'),
(4, 'Chocolate Bar', 'Dark chocolate 70%', 2.29, 1, 'bar'),
(5, 'Orange Juice', 'Fresh orange juice', 4.29, 46, 'oz'),
(5, 'Sparkling Water', 'Lemon sparkling water', 8.99, 12, 'can');

INSERT INTO employee (
    st_id, first_name, last_name, email, phone,
    salary, is_current, password_hash, role, start_date
)
VALUES
(1, 'Jim', 'Halpert', 'jim.halpert@hwf.com', '4085551111', 75000, TRUE, '$2b$12$2u3RmopbxuFNkDYsewpDMunF.I4sk3UNVVYdmej7XJ3oxnmEeKHlq', 'store_manager', CURDATE()),
(2, 'Bruce', 'Wayne', 'bruce.wayne@hwf.com', '4085552222', 76000, TRUE, '$2b$12$F78NgBR82wzuUMmDtheEeeO3fHFTQLIXh6rx5dqkFZ9WE54HTT7We', 'store_manager', CURDATE()),
(3, 'Arry', 'Potta', 'arry.potta@hwf.com', '4085553333', 74000, TRUE, '$2b$12$cz3g1tJXmhcoPkzcg/j/yOmTzbFcKnnFyij1xlj9pLZH5slaBNig2', 'store_manager', CURDATE()),
(4, 'Ishow', 'Speed', 'ishow.speed@hwf.com', '4085554444', 77000, TRUE, '$2b$12$WhdkZ1oUuPgH/gYD9HShreVwd3MmtgSJfW67qZ.daKwl9SzTvrgEW', 'store_manager', CURDATE());

#password = temp123 for jim halpert and arry potta.

UPDATE store SET manager_e_id = 1 WHERE st_id = 1;
UPDATE store SET manager_e_id = 2 WHERE st_id = 2;
UPDATE store SET manager_e_id = 3 WHERE st_id = 3;
UPDATE store SET manager_e_id = 4 WHERE st_id = 4;

INSERT INTO stocks (store_id, prod_id, quantity)
VALUES
(1, 1, 50),
(1, 2, 40),
(1, 3, 30),
(2, 1, 60),
(2, 5, 20),
(3, 7, 45),
(4, 9, 25);
