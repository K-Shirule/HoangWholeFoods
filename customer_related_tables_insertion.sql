USE hoangwholefoods;

-- datetime: 'YYYY-MM-DD HH:MM:SS'
-- text: varchar(65535)

-- customer(int, varchar(15), varchar(15), char(25), char(10), datetime)
INSERT INTO customer(id, fname, lname, pass_hash, phone, created_at)
VALUES  (10000, 'Bob', 'Brown', 'FAP35RIvGWb32lyZZBOQlSiVf', 0123456789, '2026-04-02 07:37:15'),
		(10001, 'Jane', 'Smith', 'ExcPXwvFkW4LXvcL1QpakAZkQ', NULL, '2026-04-06 14:53:15');

-- shopping_cart(int, datetime, enum((1)'empty', (2)'in-use', (3)'done'), int)
INSERT INTO shopping_cart(id, created_at, c_status, cid)
VALUES 	(100, '2026-04-06 23:16:00', 'empty', 10000),
		(101, '2026-04-06 23:16:00', 2, 10001);
        
-- review(int, enum((1)'1', ..., (5)'5'), text, datetime, int, int)
INSERT INTO review(id, rating, r_comment, created_at, cid, pid)
VALUES	(1, 3, 'Tastes good!', '2026-04-06 23:16:00', 10001, 2000);

-- cart_contains(int, int, int)
INSERT INTO cart_contains(scid, pid, quantity)
VALUES	(101, 2000, 10);