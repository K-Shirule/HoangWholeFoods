-- insert sample orders
insert into orders (
    delivery_method,
    total_amount,
    order_type,
    order_status,
    c_id,
    st_id,
    e_id
) values
('instore', 24.50, 'instore', 'completed', 1, 1, 3),
('pickup', 42.75, 'online', 'pending', 2, 1, null),
('delivery', 58.90, 'online', 'out_for_delivery', 3, 2, null),
('delivery', 30.00, 'online', 'pending', 1, 1, null);

-- insert items for each order
insert into order_contains (
    order_id,
    prod_id,
    quantity,
    price_at_purchase
) values
(1, 1, 2, 4.50),
(1, 2, 1, 15.50),
(2, 3, 3, 5.25),
(2, 4, 1, 27.00),
(3, 5, 2, 19.45),
(4, 6, 2, 5.00),
(4, 7, 1, 20.00);

-- insert a sample return request
insert into return_record (
    order_id,
    prod_id,
    return_quantity,
    return_reason,
    return_status,
    processed_by_employee_id
) values
(1, 101, 1, 'damaged item', 'requested', null),
(4, 201, 1, 'wrong item received', 'approved', 5);

-- insert payment records for purchases and refunds
insert into payments (
    method,
    amount,
    payment_status,
    order_id,
    return_id
) values
('credit_card', 24.50, 'completed', 1, null),
('cash', 42.75, 'pending', 2, null),
('debit_card', 58.90, 'completed', 3, null),
('debit_card', 30.00, 'completed', 4, null),
('credit_card', 4.50, 'refunded', null, 1),
('debit_card', 5.00, 'refunded', null, 2);

-- insert delivery tracking records
insert into delivery_record (
    delivered_at,
    delivery_status,
    order_id,
    e_id
) values
(current_timestamp, 'delivered', 3, 7),
(null, 'assigned', 4, 8);

-- update an order status
update orders
set order_status = 'completed'
where order_id = 2;

-- update a return request after review
update return_record
set return_status = 'approved',
    processed_by_employee_id = 5
where return_id = 1;

-- update a payment status after completion
update payments
set payment_status = 'completed'
where trans_id = 2;

-- update delivery after completion
update delivery_record
set delivery_status = 'delivered',
    delivered_at = current_timestamp
where order_id = 4;

-- view all orders
select *
from orders;

-- view one specific order
select *
from orders
where order_id = 1;

-- view all orders for one customer
select *
from orders
where c_id = 1
order by order_date desc;

-- view all orders for one store
select *
from orders
where st_id = 1
order by order_date desc;

-- view all online orders
select *
from orders
where order_type = 'online';

-- view all in-store orders
select *
from orders
where order_type = 'instore';

-- view all delivery orders
select *
from orders
where delivery_method = 'delivery';

-- view all pending orders
select *
from orders
where order_status = 'pending';

-- view all items in a specific order
select *
from order_contains
where order_id = 1;

-- view product details for items in an order
select
    oc.order_id,
    oc.prod_id,
    p.prod_name,
    oc.quantity,
    oc.price_at_purchase
from order_contains oc
join product p on oc.prod_id = p.prod_id
where oc.order_id = 1;

-- find all orders containing a product
select *
from order_contains
where prod_id = 101;

-- view all return requests
select *
from return_record;

-- view only requested returns
select *
from return_record
where return_status = 'requested';

-- view only approved returns
select *
from return_record
where return_status = 'approved';

-- view all returns for one order
select *
from return_record
where order_id = 1;

-- view returns handled by one employee
select *
from return_record
where processed_by_employee_id = 5;

-- view all payment records
select *
from payments;

-- view payments for a specific order
select *
from payments
where order_id = 1;

-- view refund records for a return
select *
from payments
where return_id = 1;

-- view all completed payments
select *
from payments
where payment_status = 'completed';

-- view all refunded payments
select *
from payments
where payment_status = 'refunded';

-- view all delivery records
select *
from delivery_record;

-- view delivery info for one order
select *
from delivery_record
where order_id = 3;

-- view all deliveries handled by one employee
select *
from delivery_record
where e_id = 7;

-- view all delivered orders
select *
from delivery_record
where delivery_status = 'delivered';

-- view all active deliveries
select *
from delivery_record
where delivery_status in ('assigned', 'out_for_delivery', 'in_transit');

-- view an order with customer and store info
select
    o.order_id,
    o.order_date,
    o.order_type,
    o.delivery_method,
    o.order_status,
    o.total_amount,
    c.c_id,
    s.st_id
from orders o
join customer c on o.c_id = c.c_id
join store s on o.st_id = s.st_id
where o.order_id = 1;

-- view an order and all its items
select
    o.order_id,
    o.order_date,
    o.order_status,
    oc.prod_id,
    oc.quantity,
    oc.price_at_purchase
from orders o
join order_contains oc on o.order_id = oc.order_id
where o.order_id = 1;

-- view an order with payment info
select
    o.order_id,
    o.total_amount,
    p.trans_id,
    p.method,
    p.amount,
    p.payment_status,
    p.payment_time
from orders o
left join payments p on o.order_id = p.order_id
where o.order_id = 1;

-- view an order with delivery info
select
    o.order_id,
    o.order_status,
    d.delivery_id,
    d.delivery_status,
    d.delivered_at,
    d.e_id
from orders o
left join delivery_record d on o.order_id = d.order_id
where o.order_id = 3;

-- view a return with related refund info
select
    r.return_id,
    r.order_id,
    r.prod_id,
    r.return_quantity,
    r.return_reason,
    r.return_status,
    p.trans_id,
    p.amount,
    p.payment_status
from return_record r
left join payments p on r.return_id = p.return_id
where r.return_id = 1;

-- calculate total completed sales
select sum(amount) as total_sales
from payments
where payment_status = 'completed'
  and order_id is not null;

-- calculate total refunded amount
select sum(amount) as total_refunded
from payments
where payment_status = 'refunded'
  and return_id is not null;

-- count number of orders per customer
select
    c_id,
    count(*) as total_orders
from orders
group by c_id;

-- count number of orders per store
select
    st_id,
    count(*) as total_orders
from orders
group by st_id;

-- find the most ordered products
select
    prod_id,
    sum(quantity) as total_units_sold
from order_contains
group by prod_id
order by total_units_sold desc;

-- find the most returned products
select
    prod_id,
    sum(return_quantity) as total_units_returned
from return_record
group by prod_id
order by total_units_returned desc;

-- calculate revenue by store
select
    o.st_id,
    sum(p.amount) as store_revenue
from orders o
join payments p on o.order_id = p.order_id
where p.payment_status = 'completed'
group by o.st_id;

-- check ordered quantity before allowing a return
select quantity
from order_contains
where order_id = 1
  and prod_id = 101;

-- check how many units have already been returned
select coalesce(sum(return_quantity), 0) as already_returned
from return_record
where order_id = 1
  and prod_id = 101
  and return_status in ('requested', 'approved', 'completed');

-- check whether an order exists
select *
from orders
where order_id = 1;

-- check whether delivery info already exists for an order
select *
from delivery_record
where order_id = 3;

-- check whether payment already exists for an order
select *
from payments
where order_id = 1;

-- delete a return record if needed
delete from return_record
where return_id = 2;

-- delete all items from an order if needed
delete from order_contains
where order_id = 2;

-- delete an order after dependent rows are removed
delete from orders
where order_id = 2;