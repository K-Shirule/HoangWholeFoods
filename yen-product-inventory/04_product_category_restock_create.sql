-- SJSU CMPE 138 SPRING 2026 TEAM6
USE hoang_whole_foods;

CREATE TABLE category (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE product (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit_price DECIMAL(10,2) NOT NULL,
    units INT,
    unit_type VARCHAR(50),
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES category(cat_id)
);

CREATE TABLE restock_list (
    list_id INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    created_by INT NOT NULL,
    approved_by INT NULL,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    approved_at DATETIME NULL,
    CONSTRAINT fk_restock_list_store
        FOREIGN KEY (store_id) REFERENCES store(store_id),
    CONSTRAINT fk_restock_list_created_by
        FOREIGN KEY (created_by) REFERENCES employee(emp_id),
    CONSTRAINT fk_restock_list_approved_by
        FOREIGN KEY (approved_by) REFERENCES employee(emp_id)
);

CREATE TABLE stocks (
    store_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (store_id, prod_id),
    CONSTRAINT fk_stocks_store
        FOREIGN KEY (store_id) REFERENCES store(store_id),
    CONSTRAINT fk_stocks_product
        FOREIGN KEY (prod_id) REFERENCES product(prod_id)
);

CREATE TABLE restock_contains (
    list_id INT NOT NULL,
    prod_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (list_id, prod_id),
    CONSTRAINT fk_restock_contains_list
        FOREIGN KEY (list_id) REFERENCES restock_list(list_id),
    CONSTRAINT fk_restock_contains_product
        FOREIGN KEY (prod_id) REFERENCES product(prod_id)
);
