from dataclasses import dataclass
from typing import Self
from datetime import datetime
from enum import Enum

# cart_status enum definition for shopping_cart attribute
class CartStatus(str, Enum):
    NEW = 'new'
    DONE = 'done'

# rating enum definition for review attribute
class Rating(str, Enum):
    ONE = '1'
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'

"""             >> CUSTOMER CLASS <<

Description:    Use to instantiate a local instance of a
                customer entity. Gives direct access to
                all attributes without the need for
                separate queries.

IMPORTANT:      Row data must be accessed as a dictionary
                and NOT a tuple

                cursor = db.cursor(dictionary = True)

Example Usage:

row = /* Raw row data obtained from customer table */

# Easiest way
customer1: Customer = Customer.from_dict(row)

# Alternate way
customer2: Customer = Customer(
    c_id = row['c_id'],
    first_name = row['first_name'],
    last_name = row['last_name'],
    email = row['email'],
    password_hash = row['password_hash'],
    phone = row['phone'],
    created_at = row['created_at']
)

printf(customer1.first_name)
printf(customer2.last_name)

/* Use data however you wish */

"""
@dataclass(frozen=True)
class Customer:

    c_id:           int  # PK

    first_name:     str  # Max len: 15
    last_name:      str  # Max len: 15
    email:          str  # Max len: 25
    password_hash:  str  # Len: 25
    phone:          str  # Len: 10

    created_at:     datetime

    @classmethod
    def from_dict(cls, data: dict) -> Self:

        c_id = data['c_id']
        first_name = data['first_name'],
        last_name = data['last_name'],
        email = data['email'],
        password_hash = data['password_hash'],
        phone = data['phone'],
        created_at = data['created_at']

        return cls(
            c_id = c_id,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password_hash = password_hash,
            phone = phone,
            created_at = created_at
        )

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
        