drop database if exists HoangWholeFoods;
create database HoangWholeFoods;
use HoangWholeFoods;

create table billing_term
(
    billing_term varchar(20) not null,
    description  varchar(255),

    primary key (billing_term)
);

create table supplier
(
    supplier_id     int          auto_increment,
    supplier_name   varchar(255) not null,
    email           varchar(255) not null unique,
    address         varchar(255),
    password_hash   varchar(255) not null,
    billing_term    varchar(20),
    phone           varchar(20),

    primary key (supplier_id),
    foreign key (billing_term) references billing_term(billing_term)
);

create table supplier_order
(
    so_id                   int,
    supplier_id             int          not null,
    date_of_order           date         not null,
    total_amount            decimal(10, 2) not null,
    payment_method          varchar(50),
    status                  varchar(20),
    expected_delivery_date  date,
    received_date           date,
    tracking_number         varchar(100),
    st_id                   int,

    primary key (so_id, supplier_id),
    foreign key (supplier_id) references supplier(supplier_id)
        on delete cascade,
    foreign key (st_id) references store(st_id)
        on delete set null, 
);

create table so_contains
(
    so_id               int          not null,
    supplier_id         int          not null,
    prod_id             int          not null,
    quantity            int,
    cost_at_purchase    decimal(10, 2),

    primary key (so_id, supplier_id, prod_id),
    foreign key (so_id, supplier_id) references supplier_order(so_id, supplier_id)
        on delete cascade,
    foreign key (prod_id) references product(prod_id)
        on delete cascade
);

create table supplies
(
    supplier_id     int,
    prod_id         int,

    primary key (supplier_id, prod_id),
    foreign key (supplier_id) references supplier(supplier_id)
        on delete cascade,
    foreign key (prod_id) references product(prod_id)
        on delete cascade
);