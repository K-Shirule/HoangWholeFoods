USE hoangwholefoods

USE hoangwholefoods;

-- [CUSTOMER] --

-- > SIGN-IN

-- >> getPassHash(String: email)
SELECT c.pass_hash
FROM customer AS c
WHERE c.email = 'bbrown123@gmail.com' -- email
;
