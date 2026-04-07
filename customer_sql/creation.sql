DROP DATABASE IF EXISTS hoangwholefoods;
CREATE DATABASE hoangwholefoods;
USE hoangwholefoods;

-- ENTITIES -- 

CREATE TABLE customer (
	c_id			integer auto_increment not null,
	first_name		varchar(15) not null,
    last_name		varchar(15) not null,
    email			varchar(25) not null,
    password_hash	char(25) not null, 
    phone			char(10),
    created_at 		datetime not null,
    primary key (c_id),
    unique (email),
    unique (password_hash)
);

CREATE TABLE shopping_cart (
	cart_id			integer auto_increment not null,
    created_at		datetime not null,
    cart_status		enum('new', 'done') not null,
    c_id			integer not null,
    primary key (cart_id),
    foreign key (c_id) references customer(c_id)
		on delete cascade
        on update cascade
);

CREATE TABLE review (
	review_id		integer auto_increment not null,
    rating			enum('1', '2', '3', '4', '5'), -- * Assuming star rating system (NULL = 0 stars)
    r_comment		text, -- * Max length 64 KB
    created_at		datetime not null,
    c_id			integer not null,
    p_id			integer not null,
    primary key (review_id),
    foreign key (c_id) references customer(c_id)
		on delete cascade
        on update cascade
    -- foreign key (p_id) references product(prod_id) 	-- ! Uncomment once "product" table is merged
    -- 		on delete cascade
    --      on update cascade
);

-- RELATIONSHIPS --

CREATE TABLE cart_contains (
	cart_id			integer not null,
    p_id			integer not null,
    quantity		integer not null,
    primary key (cart_id, p_id),
    foreign key (cart_id) references shopping_cart(cart_id)
		on delete cascade
        on update cascade
    -- foreign key (p_id) references product(prod_id)		-- ! Uncomment once "product" table is merged
    -- 		on delete set null
    --      on update cascade
);
