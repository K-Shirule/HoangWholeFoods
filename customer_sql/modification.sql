USE hoangwholefoods;

-- [CUSTOMER] --

-- >> setCustomerAttr(int: customer_id, String: attr, String: val)
UPDATE customer AS c
SET c.%s = %s
WHERE c.c_id = %d
;

-- [SHOPPING CART] --

-- >> setCartStatus(int: cart_id, int: status)
UPDATE shopping_cart AS cart
SET cart.cart_status = %s
WHERE cart.card_id = %d
;

-- [REVIEW] --

-- >> setRating(int: review_id, int: rating)
UPDATE review AS r
SET r.rating = %d
WHERE r.review_id = %d
;

-- >> setComment(int: review_id, String: text)
UPDATE review AS r
SET r.r_comment = %s
WHERE r.review_id = %d
;

-- [CART CONTAINS] --

-- >> setQuantity(int: cart_id, int: prod_id, int: quantity)
UPDATE cart_contains AS cc
SET cc.quantity = %d
WHERE cc.card_id = %d AND cc.prod_id = %d
;

-- >> incQuantity(int: cart_id, int: prod_id)
UPDATE cart_contains AS cc
SET cc.quantity = cc.quantity + 1
WHERE cc.card_id = %d AND cc.prod_id = %d
;