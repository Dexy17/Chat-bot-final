from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Auth models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

# Patient models
class DemographicData(BaseModel):
    Name: str
    Age: int
    Gender: str
    Contact: str

class Symptom(BaseModel):
    Symptom: str
    Frequency: str
    Severity: str
    Duration: str
    Additional_Notes: Optional[str] = None

class PatientRecord(BaseModel):
    patient_id: str
    demographic_data: DemographicData
    symptoms_data: List[Symptom]

class DoctorNote(BaseModel):
    note: str
