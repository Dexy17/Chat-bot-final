# seed_admin.py

"""
Simple seed script to create the first admin user in your MongoDB 'users' collection.
"""

from passlib.context import CryptContext
from pymongo import MongoClient
from Redo.medical_app.config import MONGO_URI, DB_NAME

# -- Configure your desired doctor credentials here --
ADMIN_USERNAME = "doctor_user"
ADMIN_EMAIL    = "doctor@example.com"
ADMIN_PASSWORD = "doctorpass"
# ----------------------------------------------------

# Setup bcrypt hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_col = db["users"]

    # Check if admin already exists
    if users_col.find_one({"username": ADMIN_USERNAME}):
        print(f"Admin '{ADMIN_USERNAME}' already exists. Exiting.")
        return

    # Insert admin user
    users_col.insert_one({
        "username": ADMIN_USERNAME,
        "email": ADMIN_EMAIL,
        "password": hash_password(ADMIN_PASSWORD),
        "role": "doctor"
    })
    print(f"✅ Seeded doctor user: {ADMIN_USERNAME}")

if __name__ == "__main__":
    main()
