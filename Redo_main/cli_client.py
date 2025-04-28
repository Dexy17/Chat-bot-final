# cli_client.py

import getpass
import json
from pymongo import MongoClient
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from Redo.medical_app.config import MONGO_URI, DB_NAME, FERNET_KEY
from datetime import datetime

# Setup MongoDB and security
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["users"]
patients_col = db["patients"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(FERNET_KEY)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def encrypt_contact(contact: str) -> str:
    return fernet.encrypt(contact.encode()).decode()

def decrypt_contact(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

def register_patient():
    print("\n=== Patient Registration ===")
    username = input("Username: ").lower()
    if users_col.find_one({"username": username}):
        print("Username already exists.")
        return
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    password2 = getpass.getpass("Please confirm the password:")
    while password != password2:
        print("The passwords do not match!")
        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Please confirm the password:")
    name = input("Full Name: ")
    age = int(input("Age: "))
    gender = input("Gender: ")
    contact = input("Phone Number: ")
    # Initial symptoms
    symptoms = []
    while input("Add a symptom? (y/n): ").lower() == "y":
        symptom = input("Symptom: ")
        frequency = input("Frequency: ")
        severity = input("Severity: ")
        duration = input("Duration: ")
        notes = input("Additional Notes: ")
        symptoms.append({
            "Symptom": symptom,
            "Frequency": frequency,
            "Severity": severity,
            "Duration": duration,
            "Additional_Notes": notes
        })
    # Create user
    users_col.insert_one({
        "username": username,
        "Name": name,
        "email": email,
        "password": hash_password(password),
        "role": "patient"
    })
    # Create patient record
    patients_col.insert_one({
        "patient_id": username,
        "demographic_data": {
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Contact": encrypt_contact(contact)
        },
        "symptoms_data": symptoms,
        "doctor_notes": []
    })
    print("Patient registered with ID:", username)

def add_symptoms():
    print("\n=== Add New Symptoms ===")
    username = input("Patient ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "patient"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    new_symptoms = []
    while input("Add a new symptom? (y/n): ").lower() == "y":
        symptom = input("Symptom: ")
        frequency = input("Frequency: ")
        severity = input("Severity: ")
        duration = input("Duration: ")
        notes = input("Additional Notes: ")
        new_symptoms.append({
            "Symptom": symptom,
            "Frequency": frequency,
            "Severity": severity,
            "Duration": duration,
            "Additional_Notes": notes
        })
    if new_symptoms:
        patients_col.update_one(
            {"patient_id": username},
            {"$push": {"symptoms_data": {"$each": new_symptoms}}}
        )
        print("Symptoms added.")
    else:
        print("No symptoms added.")

def doctor_view_and_note():
    print("\n=== Doctor Portal ===")
    username = input("Doctor ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "doctor"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    patient_id = input("Enter Patient ID to view: ")
    record = patients_col.find_one({"patient_id": patient_id})
    if not record:
        print("Patient not found.")
        return
    print("\n-- Patient Medical Data --")
    print(json.dumps({
        "patient_id": record["patient_id"],
        "symptoms_data": record.get("symptoms_data", []),
        "doctor_notes": record.get("doctor_notes", [])
    }, indent=2))
    if input("Add a doctor's note? (y/n): ").lower() == "y":
        note = input("Note: ")
        entry = {
            "note": note,
            "doctor_id": username,
            "timestamp": datetime.utcnow().isoformat()
        }
        patients_col.update_one(
            {"patient_id": patient_id},
            {"$push": {"doctor_notes": entry}}
        )
        print("Note added.")

def admin_view_all():
    print("\n=== Admin: View All Records ===")
    username = input("Admin ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "admin"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    for rec in patients_col.find():
        rec["demographic_data"]["Contact"] = decrypt_contact(rec["demographic_data"]["Contact"])
        print(json.dumps({
            "patient_id": rec["patient_id"],
            "demographic_data": rec["demographic_data"],
            "symptoms_data": rec.get("symptoms_data", []),
            "doctor_notes": rec.get("doctor_notes", [])
        }, indent=2))

def admin_modify_delete():
    print("\n=== Admin: Modify/Delete Record ===")
    username = input("Admin ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "admin"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    action = input("Choose action: (m)odify / (d)elete: ").lower()
    pid = input("Patient ID: ")
    if action == "d":
        res = patients_col.delete_one({"patient_id": pid})
        print("Deleted." if res.deleted_count else "Patient not found.")
    elif action == "m":
        field = input("Field to modify (Name/Age/Gender/Contact): ")
        value = input("New value: ")
        update_field = {}
        if field.lower() == "contact":
            value = encrypt_contact(value)
            update_field["demographic_data.Contact"] = value
        else:
            key = "demographic_data." + field
            update_field[key] = value if field != "Age" else int(value)
        patients_col.update_one({"patient_id": pid}, {"$set": update_field})
        print("Record updated.")
    else:
        print("Invalid action.")

def main():
    options = {
        "1": ("Register New Patient", register_patient),
        "2": ("Add New Symptoms", add_symptoms),
        "3": ("Doctor: View/Add Note", doctor_view_and_note),
        "4": ("Admin: View All Records", admin_view_all),
        "5": ("Admin: Modify/Delete Record", admin_modify_delete),
        "q": ("Quit", None)
    }
    while True:
        print("\n=== Medical DB CLI ===")
        for key, (desc, _) in options.items():
            print(f"{key}) {desc}")
        choice = input("Select an option: ")
        if choice == "q":
            break
        action = options.get(choice)
        if action:
            action[1]()
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

