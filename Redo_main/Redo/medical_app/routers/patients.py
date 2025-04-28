from fastapi import APIRouter, HTTPException, Depends, Body
from medical_app.models import PatientRecord, DoctorNote
from medical_app.database import db
from medical_app.dependencies import get_current_user, role_required
from cryptography.fernet import Fernet
from medical_app.config import FERNET_KEY
from datetime import datetime

router = APIRouter(prefix="/patients", tags=["Patients"])
patients_collection = db["patients"]

fernet = Fernet(FERNET_KEY)

def encrypt_contact(contact: str) -> str:
    return fernet.encrypt(contact.encode()).decode()

def decrypt_contact(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

@router.post("/", response_model=dict)
def add_patient(record: PatientRecord, user=Depends(get_current_user)):
    role = user["role"]
    if role == "patient":
        if record.patient_id != user["user_id"]:
            raise HTTPException(status_code=403, detail="Cannot create other patient's record")
    elif role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    record.demographic_data.Contact = encrypt_contact(record.demographic_data.Contact)
    patients_collection.insert_one(record.dict())
    return {"message": "Record added"}

@router.get("/", response_model=list, dependencies=[Depends(role_required("admin"))])
def get_all_patients():
    docs = list(patients_collection.find())
    for doc in docs:
        doc["demographic_data"]["Contact"] = decrypt_contact(doc["demographic_data"]["Contact"])
        doc["_id"] = str(doc["_id"])
    return docs

@router.get("/{patient_id}", response_model=dict)
def get_patient(patient_id: str, user=Depends(get_current_user)):
    role = user["role"]
    doc = patients_collection.find_one({"patient_id": patient_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")
    if role == "admin":
        doc["demographic_data"]["Contact"] = decrypt_contact(doc["demographic_data"]["Contact"])
    elif role == "doctor":
        return {
            "patient_id": doc["patient_id"],
            "symptoms_data": doc.get("symptoms_data", []),
            "doctor_notes": doc.get("doctor_notes", [])
        }
    elif role == "patient":
        if user["user_id"] != patient_id:
            raise HTTPException(status_code=403, detail="Access denied")
        doc["demographic_data"]["Contact"] = decrypt_contact(doc["demographic_data"]["Contact"])
    else:
        raise HTTPException(status_code=403, detail="Unauthorized")
    doc["_id"] = str(doc["_id"])
    return doc

@router.put("/update/{patient_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
def update_patient(patient_id: str, update_data: dict = Body(...)):
    if "demographic_data" in update_data and "Contact" in update_data["demographic_data"]:
        update_data["demographic_data"]["Contact"] = encrypt_contact(update_data["demographic_data"]["Contact"])
    result = patients_collection.update_one({"patient_id": patient_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Record updated"}

@router.delete("/{patient_id}", response_model=dict, dependencies=[Depends(role_required("admin"))])
def delete_patient(patient_id: str):
    result = patients_collection.delete_one({"patient_id": patient_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Record deleted"}

@router.post("/{patient_id}/add_note", response_model=dict, dependencies=[Depends(role_required("doctor"))])
def add_doctor_note(patient_id: str, note: DoctorNote, user=Depends(get_current_user)):
    entry = {
        "note": note.note,
        "doctor_id": user["user_id"],
        "timestamp": datetime.utcnow().isoformat()
    }
    result = patients_collection.update_one({"patient_id": patient_id}, {"$push": {"doctor_notes": entry}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Note added successfully"}
