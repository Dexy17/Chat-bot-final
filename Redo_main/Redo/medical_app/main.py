from fastapi import FastAPI
from medical_app.routers import users, patients

app = FastAPI()
app.include_router(users.router)
app.include_router(patients.router)
