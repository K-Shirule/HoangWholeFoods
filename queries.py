import mysql.connector as MySQL
from classes import Customer

# Write general query statements that can be resued here

# > Selection

# >> Customer

# Returns customer row with the given email
def getCustomer(db, email: str):

    cursor = db.cursor(dictionary = True)
    query = (
        f"SELECT c.* " \
        f"FROM customer AS c " \
        f"WHERE c.email = %s"
    )
    cursor.execute(query, (email,))
    return cursor.fetchone()


# Returns customer rows with the given attribute
def getCustomersFromAttr(db, attr: str, key: str):

    cursor = db.cursor(dictionary = True)
    query = (
        f"SELECT c.* " \
        f"FROM customer AS c " \
        f"WHERE c.{attr} = %s"
    )
    cursor.execute(query, (key,))
    return cursor.fetchall()


# Returns password hash for customer with given email, if it exists
def getPasswordHash(db, email: str):

    cursor = db.cursor(dictionary = True)
    query = (
        f"SELECT c.password_hash " \
        f"FROM customer AS c " \
        f"WHERE c.email = %s"
    )
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    return result['password_hash']
