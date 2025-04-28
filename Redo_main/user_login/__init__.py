import getpass
import json
from pymongo import MongoClient
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from Redo.medical_app.config import MONGO_URI, DB_NAME, FERNET_KEY
from datetime import datetime
import common
import report_gen as rg
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


def admin_login():
    print("\n=== Admin login ===")
    username = input("Admin ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "admin"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    
    while True:
        action = input('''Choose action: 
1)(V)iew all records
2)(S)earch for a record
3)(M)odify a record
4)(D)elete a user
5)(A)dd new record 
6)(Q)uit\n''').lower()
        if(action == "v" or action == "1"):
            a = input('''1)Print in console
2)Generate output file\n''').lower()
            if a == '1':
                for rec in patients_col.find():
                    rec["demographic_data"]["Contact"] = decrypt_contact(rec["demographic_data"]["Contact"])
                    print(json.dumps({
                        "patient_id": rec["patient_id"],
                        "demographic_data": rec["demographic_data"],
                        "symptoms_data": rec.get("symptoms_data", []),
                        "doctor_notes": rec.get("doctor_notes", [])
                    }, indent=2))
            elif a == '2':
                with open("patients_output.json", "w") as file:
                    patients_data = []
                    for rec in patients_col.find():
                        # Decrypt contact information
                        rec["demographic_data"]["Contact"] = decrypt_contact(rec["demographic_data"]["Contact"])
                        
                        # Structure the patient data
                        patient_entry = {
                            "patient_id": rec["patient_id"],
                            "demographic_data": rec["demographic_data"],
                            "symptoms_data": rec.get("symptoms_data", []),
                            "doctor_notes": rec.get("doctor_notes", [])
                        }
                        patients_data.append(patient_entry)
                    
                    # Write all data to the file with proper formatting
                    json.dump(patients_data, file, indent=2)
                print("Created file patients_output.json")
            else:
                print("Invalid option provided")
        elif action == '2' or action == 's':
            patient_id = input("Please input the patientID:")
            rec = patients_col.find_one({"patient_id": patient_id})
            if not rec:
                print(f"❌ No patient found with ID {patient_id}")
                
            else:
                # Decrypt contact
                rec["demographic_data"]["Contact"] = decrypt_contact(rec["demographic_data"]["Contact"])

                print("\n--- Patient Record ---")
                print(json.dumps({
                        "patient_id": rec["patient_id"],
                        "demographic_data": rec["demographic_data"],
                        "symptoms_data": rec.get("symptoms_data", []),
                        "doctor_notes": rec.get("doctor_notes", [])
                    }, indent=2))
        elif action == '3' or action == 'm':
            pid = input("Patient ID: ")
            rec = users_col.find_one({"username": pid})
            if not rec:
                print(f"No record found for user: {pid}")
                continue
            field = input("Field to modify (Name/Age/Gender/Contact): ")
            value = input("New value: ")
            update_field = {}
            if field.lower() == "contact":
                value = encrypt_contact(value)
                update_field["demographic_data.Contact"] = value
            else:
                key = "demographic_data." + field
                update_field[key] = value if field != "Age" else int(value)
            try:
                patients_col.update_one({"patient_id": pid}, {"$set": update_field})
                print("Record updated.")
            except:
                print("Record Faile to update")
        elif action == '4' or action == 'd':
            pid = input("User ID: ")
            rec = users_col.find_one({"username": pid})
            if not rec:
                print(f"No record found for user: {pid}")
                continue
            con = input(f'Are you sure you want to delete the {(rec["role"])} {pid}')                
            if con == 'y':
                if(rec["role"] == "patient"):

                    res = patients_col.delete_one({"patient_id": pid})
                res = users_col.delete_one({"username":pid})
                print("Deleted." if res.deleted_count else "Patient not found.")
        elif action == '5' or action == 'a':
            print("\n=== Add user ===")
            username = input("Username: ").lower()
            while users_col.find_one({"username": username}):
                print("Username already exists.")
                username = input("Username: ")
            email = input("Email: ")
            password = getpass.getpass("Password: ")
            password2 = getpass.getpass("Please confirm the password:")
            while password != password2:
                print("The passwords do not match!")
                password = getpass.getpass("Password: ")
                password2 = getpass.getpass("Please confirm the password:")

            # name = input("Full Name: ")
            role = input('''Role? p:patient d:doctor a:admin:''').lower()
            if(role == 'a'):
                cnf = input("Are you sure you want to add a new admin? The new admin will have access to the complete database(y/n)").lower()
                while cnf not in ['y','n']:
                    cnf = input("Please Give a valid input.\n n for no you don't want to add another admin\n y for yes you want to add another admin")
                if cnf == 'y':
                    users_col.insert_one({
                            "username": username,
                            "email": email,
                            "password": hash_password(password),
                            "role": "admin"
                        })
                    print(f"New admin added successfully with username {username}")
            elif(role == 'd'):
                cnf = input("Are you sure you want to add a new doctor?").lower()
                while cnf not in ['y','n']:
                    cnf = input("Please Give a valid input.\n n for no you don't want to add another admin\n y for yes you want to add another admin")
                if cnf == 'y':
                    name = input("Full Name: ")
                    users_col.insert_one({
                            "username": username,
                            "name":name,
                            "email": email,
                            "password": hash_password(password),
                            "role": "doctor"
                        })
                    print("New doctor added successfully")
            elif(role == 'p'):
                users_col.insert_one({
                            "username": username,
                            "name":name,
                            "email": email,
                            "password": hash_password(password),
                            "role": "patient"
                        })
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
        elif action == '6' or action == 'q':
            break
        else:
            print("Please provide a valid option")

def doc_login():
    print("\n=== Doctor Portal ===")
    username = input("Doctor ID: ")
    password = getpass.getpass("Password: ")
    user = users_col.find_one({"username": username, "role": "doctor"})
    if not user or not verify_password(password, user["password"]):
        print("Invalid credentials.")
        return
    while True:
        patient_id = input("Enter Patient ID to view: (or simply type 'n' to logout) ").lower()
        if(patient_id == 'n'):
            return
        record = patients_col.find_one({"patient_id": patient_id})

        
        if not record:
            print("Patient not found.")
        else:
            print(record)
            rg.generate_medical_report_pdf(record, "reports/"+patient_id+".pdf")
            print("--------------------------------------")
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
                    "timestamp": datetime.now().isoformat()
                }
                patients_col.update_one(
                    {"patient_id": patient_id},
                    {"$push": {"doctor_notes": entry}}
                )
                print("Note added.")

# def add_patient(app):
import os
FILE_PATH = "last_id.txt"
def get_patient_id():

    # Read last ID from file
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            last_id = int(file.read())
    else:
        last_id = 0

    next_id = last_id + 1

    # Write new ID to file
    with open(FILE_PATH, "w") as file:
        file.write(str(next_id))

    return next_id
