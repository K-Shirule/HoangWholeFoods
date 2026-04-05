-- SJSU CMPE 138 SPRING 2026 TEAM6
USE hoang_whole_foods;

INSERT INTO category (name, description) VALUES
('produce', 'Fresh fruits and vegetables sourced for daily grocery sales'),
('dairy', 'Milk, cheese, yogurt, and other refrigerated dairy items'),
('bakery', 'Fresh bread, pastries, and baked goods'),
('pantry', 'Shelf-stable staples such as grains, oils, and canned goods');

INSERT INTO product (category_id, name, description, unit_price, units, unit_type) VALUES
(1, 'organic bananas', 'Fresh organic bananas sold by the bunch', 1.99, 1, 'bunch'),
(1, 'baby spinach', 'Washed baby spinach in a clamshell container', 3.49, 5, 'oz'),
(2, 'whole milk', 'One gallon whole milk', 4.29, 1, 'gallon'),
(2, 'greek yogurt', 'Plain Greek yogurt tub', 5.99, 32, 'oz'),
(3, 'sourdough loaf', 'Freshly baked sourdough bread loaf', 4.79, 1, 'loaf'),
(3, 'blueberry muffins', 'Pack of four bakery muffins', 5.49, 4, 'count'),
(4, 'brown rice', 'Long grain brown rice bag', 6.99, 2, 'lb'),
(4, 'olive oil', 'Extra virgin olive oil bottle', 12.99, 1, 'liter');

INSERT INTO restock_list (store_id, created_by, approved_by, status, created_at, approved_at) VALUES
(1, 101, NULL, 'pending', '2026-04-01 09:15:00', NULL),
(2, 102, 103, 'approved', '2026-04-02 14:30:00', '2026-04-02 16:00:00');

INSERT INTO stocks (store_id, prod_id, quantity) VALUES
(1, 1, 18),
(1, 2, 7),
(1, 3, 10),
(2, 4, 22),
(2, 7, 6),
(2, 8, 12);

INSERT INTO restock_contains (list_id, prod_id, quantity) VALUES
(1, 2, 20),
(1, 5, 15),
(2, 7, 25),
(2, 8, 10);
