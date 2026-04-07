USE HoangWholeFoods;

create table store (
    st_id int auto_increment primary key,
    location varchar(100) not null,
    branch_name varchar(100) not null,
    phone varchar(20),
    email varchar(100),
    address_id int,
    manager_e_id int unique
);

create table employee (
    e_id int auto_increment primary key,
    st_id int not null,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    email varchar(100) not null unique,
    phone varchar(20),
    salary decimal(10,2),
    current boolean default true,
    password_hash varchar(255) not null,
    role varchar(50) not null,
    start_date date not null,
    end_date date,
    
    constraint fk_employee_store
        foreign key (st_id) references store(st_id),

    constraint chk_employee_role
        check (role in (
            'store_manager',
            'inventory_manager',
            'floor_employee',
            'customer_service_associate',
            'delivery_associate'
        )),

    constraint chk_employee_dates
        check (end_date is null or end_date >= start_date)
);

alter table store
add constraint fk_store_manager
foreign key (manager_e_id) references employee(e_id);