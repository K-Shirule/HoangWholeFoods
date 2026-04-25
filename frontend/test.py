import bcrypt
password = "temp123"

hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print(hashed.decode("utf-8"))