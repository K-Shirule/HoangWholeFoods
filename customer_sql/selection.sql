USE hoangwholefoods;

-- [CUSTOMER] --

-- >> getCustomer(String: email)
SELECT c.*
FROM customer AS c
WHERE c.email = %s
;

-- >> getCustomersFromAttr(String: attr, String: key)
SELECT c.*
FROM customer AS c
WHERE c.%s = %s
;

-- >> getPasswordHash(String: email)
SELECT c.password_hash
FROM customer AS c
WHERE c.email = %s
;


-- [SHOPPING_CART] --

-- >> getCustomerCarts(int: customer_id)
SELECT cart.*
FROM shopping_cart AS cart
WHERE cart.c_id = %d
;

-- >> getCartTotal(int: cart_id)
SELECT sc.*, SUM(cc.quantity) AS total_items
FROM shopping_cart AS sc JOIN cart_contains AS cc
	ON sc.cart_id = cc.cart_id
WHERE cc.cart_id = %d
GROUP BY cc.cart_id
;


-- [REVIEW] --

-- >> getCustomerReviews(int: customer_id)
SELECT r.*
FROM review AS r
WHERE r.c_id = %d
;

-- >> getProductReviews(int: product_id)
SELECT r.*
FROM review AS r
WHERE r.p_id = %d
;

-- >> getProductReviewsBy(int: product_id, int: customer_id)
SELECT r.*
FROM review AS r
WHERE r.p_id = %d, AND r.c_id = %d
;