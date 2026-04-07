USE hoangwholefoods;

-- Customer >> removeCustomer(int: customer_id)
DELETE c
FROM customer AS c
WHERE c.c_id = %d
;

-- Shopping Cart >> removeCart(int: cart_id)
DELETE cart
FROM shopping_cart AS cart
WHERE cart.cart_id = %d
;

-- Review >> removeReview(int: review_id)
DELETE r
FROM review AS r
WHERE r.review_id = %d