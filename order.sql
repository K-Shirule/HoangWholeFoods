create table orders(
	order_id int auto_increment,
    order_date timestamp default current_timestamp,
    delivery_method varchar(20),
    total_amount decimal(10,2) UNSIGNED,
    order_type varchar(20),
    order_status varchar(20),
    c_id int NOT NULL,
    st_id int NOT NULL,
    e_id int,
	primary key (order_id),
    foreign key (c_id) references customer (c_id),
    foreign key (st_id) references store (st_id),
    foreign key (e_id) references employee(e_id)    
);
create table order_contains (
    order_id int,
    prod_id int,
    quantity int not null,
    price_at_purchase decimal(10,2) not null,
    primary key (order_id, prod_id),
    foreign key (order_id) references orders(order_id),
    foreign key (prod_id) references product(prod_id)
);

CREATE TABLE return_record (
    return_id int auto_increment,
    order_id int not null,
    prod_id int not null,
    return_quantity int not null,
    return_reason varchar(255),
    return_status varchar(20) default 'requested',
    requested_at timestamp default current_timestamp,
    processed_by_employee_id int null,
    primary key (return_id),
    foreign key (order_id, prod_id) references order_contains(order_id, prod_id),
    foreign key (processed_by_employee_id) references employee(e_id)
);

create table payments(
	trans_id int auto_increment,
    method varchar(20),
    amount decimal(10,2),
    payment_time timestamp default current_timestamp,
    payment_status varchar(20),
    order_id int null unique,
    return_id int null unique,
    primary key (trans_id),
    foreign key (order_id) references orders(order_id),
    foreign key (return_id) references return_record(return_id)
);

create table delivery_record(
	delivery_id int auto_increment,
    delivered_at timestamp default current_timestamp,
    delivery_status varchar(20),
    order_id int not null unique,
    e_id int not null,
    primary key (delivery_id),
    foreign key (order_id) references orders (order_id),
    foreign key (e_id) references employee(e_id) 
);
