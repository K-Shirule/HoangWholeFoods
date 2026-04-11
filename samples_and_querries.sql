insert into billing_term (billing_term, description) values
('Net 30', 'Payment is due within 30 days of the invoice date.'),
('Net 60', 'Payment is due within 60 days of the invoice date.'),
('Net 90', 'Payment is due within 90 days of the invoice date.'),
('Prepaid', 'Payment is required before the goods are shipped.'),
('COD', 'Cash on Delivery - payment is made at the time of delivery.');

insert into supplier (supplier_name, email, address, password_hash, billing_term, phone) values
('Fresh Co', 'salesteam@fresh.com', '209 S 20th St, Stockton, CA', '1hbkj34', 'NET30', '408-132-1234'),
('HHEEBB Ltd', 'info@hheebb.com', '12405 N Gessner Rd, Houston, TX', 'hh341h1', 'NET60', '713-555-4321'),
('Vegetable Supplies Ltd', 'sales@vegetablesupplies.com', '1900 Davis St, Chicago, IL', '34bkj23', 'NET15', '510-232-8839'),
('Wholesale', 'info@wholesale.com', '976 3rd Ave, Brooklyn, NY', 'bk342bj', 'COD', '248-421-2343');
('Farmers Co', 'sales@farmers.com', '6255 E Grant Rd, Tucson, AZ', '2nbj42k', 'NET45', '312-555-6789');

insert into supplier_order (supplier_id, date_of_order, total_amount, payment_method, status, expected_delivery_date, received_date, tracking_number, st_id) values
(1, '2026-01-15', 500.00, 'Credit Card', 'Shipped', '2024-01-20', null, 'TRACK20260115', 1),
(2, '2026-02-10', 300.00, 'Wire Transfer', 'Delivered', '2024-01-25', '2024-01-24', 'TRACK20260210', 2),
(1, '2026-03-05', 400.00, 'Wire Transfer', 'Pending', null, null, null, 3);
(3, '2026-04-20', 525.00, 'Credit Card', 'Shipped', '2024-01-30', null, 'TRACK20260420', 1);

insert into so_contains (so_id, supplier_id, prod_id, quantity, cost_at_purchase) values
(1, 1, 1111, 100, 5.00),
(2, 2, 2222, 50, 6.00),
(3, 1, 3333, 200, 2.00),
(4, 3, 4444, 150, 3.50);

insert into supplies (supplier_id, prod_id) values
(1, 1111),
(2, 2222),
(1, 3333),
(3, 4444);



