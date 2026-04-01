USE hoangwholefoods;

-- ENTITIES -- 

CREATE TABLE customer (
	id				integer not null,
	fname			varchar(15) not null,
    lname			varchar(15) not null,
    pass_hash		char(25) not null, -- ? Unsure what hash length will be
    phone			varchar(10),
    created_at 		datetime not null,
    primary key (id),
    unique (pass_hash)
);

CREATE TABLE shopping_cart (
	id				integer not null,
    created_at		datetime not null,
    c_status		integer not null, -- ? Unsure of whether status codes should be integers or strings
    cid				integer not null,
    primary key (id),
    foreign key (cid) references customer(id)
);

CREATE TABLE review (
	id				integer not null,
    rating			enum('0', '1', '2', '3', '4', '5') not null, -- * Assuming star rating system
    r_comment		text, -- * Max length 64 KB
    created_at		datetime not null,
    cid				integer not null,
    pid				integer not null,
    primary key (id),
    foreign key (cid) references customer(id)
    -- foreign key (pid) references product(id) 	-- ! Uncomment once "product" table is merged
);

-- RELATIONSHIPS --

CREATE TABLE owns_cart (
	cid				integer not null,
    scid			integer not null,
    primary key (cid, scid),
    foreign key (cid) references customer(id),
    foreign key (scid) references shopping_cart(id)
);

CREATE TABLE cart_contains (
	scid			integer not null,
    pid				integer not null,
    primary key (scid, pid),
    foreign key (scid) references shopping_cart(id)
    -- foreign key (pid) references product(id)		-- ! Uncomment once "product" table is merged
);

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