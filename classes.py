from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# cart_status enum definition for shopping_cart attribute
class CartStatus(str, Enum):
    EMPTY = 'empty'
    IN_USE = 'in_use'
    DONE = 'done'

# rating enum definition for review attribute
class Rating(str, Enum):
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'

"""         >> CUSTOMER CLASS <<

Use to instantiate a local instance of a
customer entity.

Ex:

row = /* Raw row data obtained from customer table */

customer1: Customer = Customer(
    id = row.id,
    first_name = row.first_name,
    last_name = row.last_name,
    email = row.email,
    password_hash = row.password_hash,
    phone = row.phone,
    created_at = row.created_at
)

printf(customer1.first_name)
printf(customer2.last_name)

/* Use data however you wish */

"""
@dataclass(frozen=True)
class Customer:

    id:             int  # PK

    first_name:     str  # Max len: 15
    last_name:      str  # Max len: 15
    email:          str  # Max len: 25
    password_hash:  str  # Len: 25
    phone:          str  # Len: 10

    created_at:     datetime

    def __post_init__(self):
        
        if len(self.first_name) > 15:
            raise ValueError(f"'first_name' length exceeds 15 characters.")
        
        if len(self.last_name) > 15:
            raise ValueError(f"'last_name' length exceeds 15 characters.")
        
        if len(self.email) > 25:
            raise ValueError(f"'email' length exceeds 25 characters.")
        
        if len(self.password_hash) != 25:
            raise ValueError(f"Invalid 'password_hash' length.")
        
        if len(self.phone) != 10:
            raise ValueError(f"Invalid 'phone' length.")
        