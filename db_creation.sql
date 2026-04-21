DROP DATABASE IF EXISTS HoangWholeFoods;
CREATE DATABASE HoangWholeFoods;
USE HoangWholeFoods;

CREATE TABLE billing_term (
    billing_term VARCHAR(20) NOT NULL,
    description VARCHAR(255),
    PRIMARY KEY (billing_term)
);

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
    address varchar(60) not null,
    manager_e_id INT UNIQUE,
    store_pin varchar(10),
    supplier_pin varchar(10)
);

CREATE TABLE customer (
    c_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at timestamp NOT NULL default current_timestamp
);

CREATE TABLE supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    billing_term VARCHAR(20),
    phone VARCHAR(20),
    FOREIGN KEY (billing_term) REFERENCES billing_term(billing_term)
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
        'delivery_associate'
    )),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

ALTER TABLE store
ADD CONSTRAINT fk_store_manager
FOREIGN KEY (manager_e_id) REFERENCES employee(e_id);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_method VARCHAR(20),
    total_amount DECIMAL(10,2) UNSIGNED,
    order_type VARCHAR(20),
    order_status VARCHAR(20),
    c_id INT,
    st_id INT NOT NULL,
    e_id INT,
    FOREIGN KEY (c_id) REFERENCES customer(c_id),
    FOREIGN KEY (st_id) REFERENCES store(st_id),
    FOREIGN KEY (e_id) REFERENCES employee(e_id)
);

CREATE TABLE shopping_cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at timestamp NOT NULL default current_timestamp,
    cart_status ENUM('new', 'done') NOT NULL,
    c_id INT NOT NULL UNIQUE,
    FOREIGN KEY (c_id) REFERENCES customer(c_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    rating ENUM('1', '2', '3', '4', '5'),
    r_comment TEXT,
    created_at DATETIME NOT NULL default current_timestamp,
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
    e_id INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (e_id) REFERENCES employee(e_id)
);

CREATE TABLE restock_list (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    created_by INT NOT NULL,
    approved_by INT,
    restock_status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL default current_timestamp,
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

CREATE TABLE supplier_order (
    so_id INT NOT NULL,
    supplier_id INT NOT NULL,
    date_of_order TIMESTAMP NOT NULL default current_timestamp,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    status VARCHAR(20),
    expected_delivery_date DATE,
    received_date DATE,
    tracking_number VARCHAR(100),
    st_id INT,
    list_id INT,
    PRIMARY KEY (so_id, supplier_id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (st_id) REFERENCES store(st_id)
        ON DELETE SET NULL,
    FOREIGN KEY (list_id) REFERENCES restock_list(list_id)
);

CREATE TABLE so_contains (
    so_id INT NOT NULL,
    supplier_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT,
    cost_at_purchase DECIMAL(10,2),
    PRIMARY KEY (so_id, supplier_id, prod_id),
    FOREIGN KEY (so_id, supplier_id)
        REFERENCES supplier_order(so_id, supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
        ON DELETE CASCADE
);

CREATE TABLE supplies (
    supplier_id INT NOT NULL,
    prod_id INT NOT NULL,
    supplier_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (supplier_id, prod_id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (prod_id) REFERENCES product(prod_id)
        ON DELETE CASCADE
);
