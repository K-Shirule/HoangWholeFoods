DROP DATABASE IF EXISTS hoangwholefoods;
CREATE DATABASE hoangwholefoods;
USE hoangwholefoods;

-- ENTITIES -- 

CREATE TABLE customer (
	id				integer not null,
	fname			varchar(15) not null,
    lname			varchar(15) not null,
    email			varchar(25) not null, -- ? Max email length subject to change
    pass_hash		char(25) not null, -- ? Unsure what hash length will be
    phone			char(10),
    created_at 		datetime not null,
    primary key (id),
    unique (email),
    unique (pass_hash)
);

CREATE TABLE shopping_cart (
	id				integer not null,
    created_at		datetime not null,
    c_status		enum('empty', 'in_use', 'done') not null, -- ? Card status codes available to change
    cid				integer not null,
    primary key (id),
    foreign key (cid) references customer(id)
);

CREATE TABLE review (
	id				integer not null,
    rating			enum('1', '2', '3', '4', '5'), -- * Assuming star rating system (NULL = 0 stars)
    r_comment		text, -- * Max length 64 KB
    created_at		datetime not null,
    cid				integer not null,
    pid				integer not null,
    primary key (id),
    foreign key (cid) references customer(id)
    -- foreign key (pid) references product(id) 	-- ! Uncomment once "product" table is merged
);

-- RELATIONSHIPS --

CREATE TABLE cart_contains (
	scid			integer not null,
    pid				integer not null,
    quantity		integer not null, -- ! New attribute I added that I feel is needed. Lmk if you think otherwise.
    primary key (scid, pid),
    foreign key (scid) references shopping_cart(id)
    -- foreign key (pid) references product(id)		-- ! Uncomment once "product" table is merged
);

-- ! May be unnecessary since "shopping_cart" already references (cid) as a foreign key !
-- CREATE TABLE owns_cart (
-- 	cid				integer not null,
--     scid			integer not null,
--     primary key (cid, scid),
--     foreign key (cid) references customer(id),
--     foreign key (scid) references shopping_cart(id)
-- );

-- ! May be unnecessary since "review" already references the corresponding foreign keys !
-- CREATE TABLE writes (
-- 	   cid				integer not null,
--     rid				integer not null,
--     primary key (cid, rid),
--     foreign key (cid) references customer(id),
--     foreign key (rid) references review(id)
-- );

-- CREATE TABLE about (
-- 	pid				integer not null,
--     rid				integer not null,
--     primary key (pid, rid),
--     -- foreign key (pid) references product(id),
--     foreign key (rid) references review(id)
-- );