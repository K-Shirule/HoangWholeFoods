use HoangWholeFoods;

insert into store (st_id, location, branch_name, phone, email, address_id, manager_e_id)
values
(1, 'San Francisco, CA', 'HWF Market Street',    '415-101-0001', 'marketst@hwf.com',   1, null),
(2, 'Oakland, CA',       'HWF Grand Avenue',     '510-101-0002', 'grandave@hwf.com',   2, null),
(3, 'San Jose, CA',      'HWF Santana Row',      '408-101-0003', 'santanarow@hwf.com', 3, null);

-- Store 1
insert into employee (e_id, st_id, first_name, last_name, email, phone, salary, current, password_hash, role, start_date, end_date) values
(1,  1, 'Diana',   'Nguyen',    'diana.nguyen@hwf.com',    '415-201-0001', 85000.00, true,  'hash_001', 'store_manager',                '2019-03-10', null),
(2,  1, 'Marcus',  'Tran',      'marcus.tran@hwf.com',     '415-201-0002', 72000.00, true,  'hash_002', 'inventory_manager',            '2020-06-15', null),
(3,  1, 'Sofia',   'Patel',     'sofia.patel@hwf.com',     '415-201-0003', 48000.00, true,  'hash_003', 'floor_employee',               '2021-01-20', null),
(4,  1, 'James',   'Kim',       'james.kim@hwf.com',       '415-201-0004', 48000.00, true,  'hash_004', 'floor_employee',               '2021-09-05', null),
(5,  1, 'Priya',   'Sharma',    'priya.sharma@hwf.com',    '415-201-0005', 52000.00, true,  'hash_005', 'customer_service_associate',   '2020-11-01', null),
(6,  1, 'Leon',    'Garcia',    'leon.garcia@hwf.com',     '415-201-0006', 46000.00, true,  'hash_006', 'delivery_associate',           '2022-03-14', null),
(7,  1, 'Aisha',   'Brown',     'aisha.brown@hwf.com',     '415-201-0007', 46000.00, false, 'hash_007', 'delivery_associate',           '2020-05-01', '2023-08-31'),
(8,  1, 'Tyler',   'Nguyen',    'tyler.nguyen@hwf.com',    '415-201-0008', 48000.00, true,  'hash_008', 'floor_employee',               '2023-02-01', null);

-- Store 2
insert into employee (e_id, st_id, first_name, last_name, email, phone, salary, current, password_hash, role, start_date, end_date) values
(9,  2, 'Carlos',  'Mendez',    'carlos.mendez@hwf.com',   '510-201-0001', 85000.00, true,  'hash_009', 'store_manager',                '2018-07-22', null),
(10, 2, 'Hana',    'Yamamoto',  'hana.yamamoto@hwf.com',   '510-201-0002', 72000.00, true,  'hash_010', 'inventory_manager',            '2019-10-10', null),
(11, 2, 'Derek',   'Okafor',    'derek.okafor@hwf.com',    '510-201-0003', 48000.00, true,  'hash_011', 'floor_employee',               '2021-04-12', null),
(12, 2, 'Nina',    'Petrov',    'nina.petrov@hwf.com',     '510-201-0004', 52000.00, true,  'hash_012', 'customer_service_associate',   '2020-08-18', null),
(13, 2, 'Omar',    'Hassan',    'omar.hassan@hwf.com',     '510-201-0005', 46000.00, true,  'hash_013', 'delivery_associate',           '2022-01-03', null),
(14, 2, 'Grace',   'Chen',      'grace.chen@hwf.com',      '510-201-0006', 48000.00, true,  'hash_014', 'floor_employee',               '2021-11-29', null),
(15, 2, 'Brent',   'Walker',    'brent.walker@hwf.com',    '510-201-0007', 46000.00, false, 'hash_015', 'delivery_associate',           '2019-06-01', '2023-12-15'),
(16, 2, 'Fatima',  'Ali',       'fatima.ali@hwf.com',      '510-201-0008', 52000.00, true,  'hash_016', 'customer_service_associate',   '2023-03-07', null);

-- Store 3
insert into employee (e_id, st_id, first_name, last_name, email, phone, salary, current, password_hash, role, start_date, end_date) values
(17, 3, 'Linda',   'Hoang',     'linda.hoang@hwf.com',     '408-201-0001', 85000.00, true,  'hash_017', 'store_manager',                '2020-02-17', null),
(18, 3, 'Samuel',  'Torres',    'samuel.torres@hwf.com',   '408-201-0002', 72000.00, true,  'hash_018', 'inventory_manager',            '2020-09-01', null),
(19, 3, 'Mei',     'Liu',       'mei.liu@hwf.com',         '408-201-0003', 48000.00, true,  'hash_019', 'floor_employee',               '2021-06-14', null),
(20, 3, 'Andre',   'Dubois',    'andre.dubois@hwf.com',    '408-201-0004', 52000.00, true,  'hash_020', 'customer_service_associate',   '2022-01-10', null),
(21, 3, 'Rachel',  'Johnson',   'rachel.johnson@hwf.com',  '408-201-0005', 46000.00, true,  'hash_021', 'delivery_associate',           '2022-07-19', null),
(22, 3, 'Kwame',   'Asante',    'kwame.asante@hwf.com',    '408-201-0006', 48000.00, true,  'hash_022', 'floor_employee',               '2021-03-25', null),
(23, 3, 'Julia',   'Reyes',     'julia.reyes@hwf.com',     '408-201-0007', 48000.00, false, 'hash_023', 'floor_employee',               '2020-11-11', '2024-01-31'),
(24, 3, 'Nathan',  'Brooks',    'nathan.brooks@hwf.com',   '408-201-0008', 46000.00, true,  'hash_024', 'delivery_associate',           '2023-05-22', null),
(25, 3, 'Yara',    'Saleh',     'yara.saleh@hwf.com',      '408-201-0009', 52000.00, true,  'hash_025', 'customer_service_associate',   '2023-08-14', null);

-- set manager for store 1
update store
set manager_e_id = 1
where st_id = 1;

-- set manager for store 2
update store
set manager_e_id = 9
where st_id = 2;

-- set manager for store 3
update store
set manager_e_id = 17
where st_id = 3;