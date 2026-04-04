import bcrypt
from logger_config import get_logger

logger = get_logger(__name__)


def login_user(role):
    print("\nPlease enter your Username: ")
    username = input().strip()
    print("\nPlease enter your Password: ")
    password = input().strip()
    if(check_username(username, role)):
        if(check_password(password, role)):
            print("\nLogin successful.")
            logger.info(f"{role} '{username}' logged in successfully.")
        else:
            print("\nIncorrect Login Credentials.")
            logger.warning(f"{role} '{username}' entered incorrect password.")
    else:
        print("\nIncorrect Login Credentials.")
        logger.warning(f"{role} '{username}' - username not found in database.")


def register_user(role):
    if(role =="employee"):
        print("Please enter the store pin provided by your store manager: ")
        store_pin = input().strip()
        #query to check if store pin is correct store result in a boolean
        if(pin_match):
            print("\nStore pin accepted.")
        else:
            print("\nInvalid store pin.")
            logger.warning(f"Employee attempted to register with invalid store pin.")
            return
        
        print("Please select your exact role:")
        print("1. Inventory Manager")
        print("2. Floor Employee")
        print("3. Deliver Associate")
        print("4. Customer Associate")
        role = input("\nEnter your choice: ").strip()
    
    elif(role == "supplier"):
        print("Please enter the company pin provided by the store manager:")
        supplier_pin = input().strip()
        #query to check if supplier pin is correct company result in a boolean
        if(pin_match):
            print("\nCompany pin accepted.")
        else:
            print("\nInvalid company pin.")
            logger.warning(f"Supplier attempted to register with invalid company pin.")
            return
    
    print("\nPlease enter your desired username: ")
    username = input().strip()
    #check if username already exists
    while(check_username(username, role)):
        print("\nUsername already exists. Please choose a different username.")
        logger.info(f"Attempted registration with existing username: '{username}'.")
        username = input("\nPlease enter a different username: ").strip()
    
    print("\nPlease enter your desired password: ")
    password = input().strip()
    #hash password using bcrypt
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    if(role == "employee"):
        #query to insert new employee into database with username, hashed password, and store id
        pass
    elif(role == "supplier"):
        #query to insert new supplier into database with username, hashed password, and company id
        pass
    else:
        #query to insert new customer into database with username and hashed password
        pass

#check if username in a table for given role
def check_username(username, role):
    #query to check if username exists in database
    if(role == "employee"):
        #query employee table for username
        pass
    elif(role == "supplier"):
        #query supplier table for username
        pass
    else:
        #query customer table for username
        pass

    '''if(database_username)
        return True
    else
        return False'''
    pass

#check if password is correct for a given username and role
def check_password(password, role):
    #query to retrieve hashed password from database
    '''if bcrypt.checkpw(b"secure_password_123", hashed):
        return True
    else
        return False'''
    pass


