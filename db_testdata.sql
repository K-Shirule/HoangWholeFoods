drop database if exists HoangWholeFoods;
create database HoangWholeFoods;
use HoangWholeFoods;

CREATE TABLE category (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE store (
    st_id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    branch_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) not null,
    email VARCHAR(100) not null,
    store_address varchar(255) not null,
    manager_e_id INT UNIQUE not null
);

CREATE TABLE employee (
    e_id INT AUTO_INCREMENT PRIMARY KEY,
    st_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    salary DECIMAL(10,2),
    is_current BOOLEAN DEFAULT TRUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (st_id) REFERENCES store(st_id),
    CHECK (role IN (
        'store_manager',
        'inventory_manager',
        'floor_employee',
        'customer_service_associate',
        'delivery_associate'
    )),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

ALTER TABLE store
ADD FOREIGN KEY (manager_e_id) REFERENCES employee(e_id);

CREATE TABLE customer (
    c_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at DATETIME NOT NULL
);

CREATE TABLE product (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    units INT,
    unit_type VARCHAR(50),
    FOREIGN KEY (category_id) REFERENCES category(cat_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_method VARCHAR(20),
    total_amount DECIMAL(10,2) UNSIGNED,
    order_type VARCHAR(20),
    order_status VARCHAR(20),
    c_id INT NOT NULL,
    st_id INT NOT NULL,
    e_id INT,
    FOREIGN KEY (c_id) REFERENCES customer(c_id),
    FOREIGN KEY (st_id) REFERENCES store(st_id),
    FOREIGN KEY (e_id) REFERENCES employee(e_id)
);

CREATE TABLE shopping_cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME NOT NULL,
    cart_status ENUM('new', 'done') NOT NULL,
    c_id INT NOT NULL,
    FOREIGN KEY (c_id) REFERENCES customer(c_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    rating ENUM('1', '2', '3', '4', '5'),
    r_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    c_id INT NOT NULL,
    prod_id INT NOT NULL,
    FOREIGN KEY (c_id) REFERENCES customer(c_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE cart_contains (
    cart_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (cart_id, prod_id),
    FOREIGN KEY (cart_id) REFERENCES shopping_cart(cart_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE order_contains (
    order_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_purchase DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, prod_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
);

CREATE TABLE return_record (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    prod_id INT NOT NULL,
    return_quantity INT NOT NULL,
    return_reason VARCHAR(255),
    return_status VARCHAR(20) DEFAULT 'requested',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_by_employee_id INT,
    FOREIGN KEY (order_id, prod_id)
        REFERENCES order_contains(order_id, prod_id),
    FOREIGN KEY (processed_by_employee_id)
        REFERENCES employee(e_id)
);

CREATE TABLE payments (
    trans_id INT AUTO_INCREMENT PRIMARY KEY,
    method VARCHAR(20),
    amount DECIMAL(10,2),
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status VARCHAR(20),
    order_id INT UNIQUE,
    return_id INT UNIQUE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (return_id) REFERENCES return_record(return_id)
);

CREATE TABLE delivery_record (
    delivery_id INT AUTO_INCREMENT PRIMARY KEY,
    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_to VARCHAR(60),
    delivery_status VARCHAR(20),
    order_id INT NOT NULL UNIQUE,
    e_id INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (e_id) REFERENCES employee(e_id)
);

CREATE TABLE restock_list (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    created_by INT NOT NULL,
    approved_by INT,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    approved_at DATETIME,
    FOREIGN KEY (store_id) REFERENCES store(st_id),
    FOREIGN KEY (created_by) REFERENCES employee(e_id),
    FOREIGN KEY (approved_by) REFERENCES employee(e_id)
);

CREATE TABLE stocks (
    store_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (store_id, prod_id),
    FOREIGN KEY (store_id) REFERENCES store(st_id),
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
);

CREATE TABLE restock_contains (
    list_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (list_id, prod_id),
    FOREIGN KEY (list_id) REFERENCES restock_list(list_id),
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
);


-- >> TEST DATA << --


-- Category
INSERT INTO category (name, description) VALUES
('Produce', 'Fresh fruits and vegetables'),
('Dairy', 'Milk, cheese, and related products'),
('Bakery', 'Bread and baked goods'),
('Meat', 'Fresh and processed meats'),
('Beverages', 'Drinks and refreshments');

-- Temporarily allow Manager to be NULL
ALTER TABLE store
MODIFY manager_e_id INT NULL;

-- Store (With NULL Managers)
INSERT INTO store (location, branch_name, phone, email, store_address, manager_e_id) VALUES
('San Jose', 'SJ Downtown', '408-111-2222', 'sj@hwf.com', '123 Market St', NULL),
('Santa Clara', 'SC Central', '408-333-4444', 'sc@hwf.com', '456 El Camino', NULL);

-- Employee
INSERT INTO employee 
(st_id, first_name, last_name, email, phone, salary, password_hash, role, start_date)
VALUES
(1, 'Alice', 'Nguyen', 'alice@hwf.com', '111-111-1111', 80000, 'hash1', 'store_manager', '2023-01-01'),
(2, 'Bob', 'Tran', 'bob@hwf.com', '222-222-2222', 78000, 'hash2', 'store_manager', '2023-01-01'),
(1, 'Charlie', 'Le', 'charlie@hwf.com', '333-333-3333', 50000, 'hash3', 'inventory_manager', '2023-02-01'),
(1, 'David', 'Pham', 'david@hwf.com', '444-444-4444', 35000, 'hash4', 'floor_employee', '2023-03-01'),
(2, 'Eva', 'Hoang', 'eva@hwf.com', '555-555-5555', 36000, 'hash5', 'customer_service_associate', '2023-03-01'),
(2, 'Frank', 'Vu', 'frank@hwf.com', '666-666-6666', 34000, 'hash6', 'delivery_associate', '2023-03-01');

-- Store (Include Managers)
UPDATE store SET manager_e_id = 1 WHERE st_id = 1;
UPDATE store SET manager_e_id = 2 WHERE st_id = 2;

-- Customer
INSERT INTO customer 
(first_name, last_name, email, password_hash, phone, created_at)
VALUES
('John', 'Doe', 'john@email.com', 'hash', '999-111-2222', NOW()),
('Jane', 'Smith', 'jane@email.com', 'hash', '999-333-4444', NOW()),
('Mike', 'Lee', 'mike@email.com', 'hash', '999-555-6666', NOW());

-- Product
INSERT INTO product 
(category_id, name, description, unit_price, units, unit_type)
VALUES
(1, 'Apple', 'Red apples', 0.99, 1, 'each'),
(1, 'Banana', 'Yellow bananas', 0.59, 1, 'each'),
(2, 'Milk', 'Whole milk gallon', 4.99, 1, 'gallon'),
(3, 'Bread', 'White bread loaf', 2.99, 1, 'loaf'),
(4, 'Chicken Breast', 'Boneless chicken', 6.99, 1, 'lb'),
(5, 'Orange Juice', 'Fresh juice', 3.99, 1, 'bottle');

-- Stocks
INSERT INTO stocks (store_id, prod_id, quantity) VALUES
(1, 1, 100),
(1, 2, 120),
(1, 3, 50),
(2, 1, 80),
(2, 4, 60),
(2, 6, 70);

-- Shopping Cart
INSERT INTO shopping_cart (created_at, cart_status, c_id) VALUES
(NOW(), 'new', 1),
(NOW(), 'done', 2);

-- Cart Contains
INSERT INTO cart_contains (cart_id, prod_id, quantity) VALUES
(1, 1, 3),
(1, 3, 1),
(2, 4, 2);

-- Orders
INSERT INTO orders 
(delivery_method, total_amount, order_type, order_status, c_id, st_id, e_id)
VALUES
('delivery', 25.50, 'online', 'completed', 1, 1, 6),
('pickup', 15.00, 'in_store', 'pending', 2, 2, 5);

-- Order Contains
INSERT INTO order_contains (order_id, prod_id, quantity, price_at_purchase) VALUES
(1, 1, 5, 0.99),
(1, 3, 2, 4.99),
(2, 4, 3, 2.99);

-- Review
INSERT INTO review (rating, r_comment, created_at, c_id, prod_id) VALUES
('5', 'Great apples!', NOW(), 1, 1),
('4', 'Good milk', NOW(), 2, 3);

-- Return Record
INSERT INTO return_record 
(order_id, prod_id, return_quantity, return_reason, processed_by_employee_id)
VALUES
(1, 1, 1, 'Damaged item', 3);

-- Payments
INSERT INTO payments (method, amount, payment_status, order_id) VALUES
('card', 25.50, 'paid', 1),
('cash', 15.00, 'pending', 2);

-- Delivery Record
INSERT INTO delivery_record (delivered_to, delivery_status, order_id, e_id) VALUES
('John Doe', 'delivered', 1, 6);

-- Restock List
INSERT INTO restock_list 
(store_id, created_by, approved_by, status, created_at, approved_at)
VALUES
(1, 3, 1, 'approved', NOW(), NOW());

-- Restock Contains
INSERT INTO restock_contains (list_id, prod_id, quantity) VALUES
(1, 1, 50),
(1, 3, 30);